-- Enable pgcrypto (for gen_random_uuid) and vector extension
create extension if not exists pgcrypto;
create extension if not exists vector;

-- Session state (KV temporal)
create table if not exists public.session_state (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  key text not null,
  value jsonb not null,
  created_at timestamptz not null default now()
);
create index if not exists session_state_session_key_idx on public.session_state (session_id, key);

-- Tool audit log
create table if not exists public.tool_audit (
  id bigserial primary key,
  tool text not null,
  parameters jsonb not null,
  principal text,
  created_at timestamptz not null default now()
);

-- Vector store (1536 dims as ejemplo)
create table if not exists public.vector_store (
  id uuid primary key default gen_random_uuid(),
  namespace text not null,
  ref text not null,
  embedding vector(1536) not null,
  metadata jsonb,
  created_at timestamptz not null default now()
);
create index if not exists vector_store_namespace_idx on public.vector_store (namespace);
-- IVFFlat index (requires analyze; adjust lists based on data size)
create index if not exists vector_store_embedding_idx on public.vector_store using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- RPC for vector search
create or replace function public.match_vectors(ns text, query vector, top_k int)
returns table(ref text, metadata jsonb, score float)
language plpgsql as $$
begin
  return query
  select v.ref, v.metadata, 1 - (v.embedding <=> query) as score
  from public.vector_store v
  where v.namespace = ns
  order by v.embedding <-> query
  limit top_k;
end;
$$;
