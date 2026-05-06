# RAG Pipeline

This document describes the ingestion and retrieval design for Smart Enterprise RAG Knowledge Base.

Phase 2 implements document ingestion up through chunk persistence and vector-store abstraction. Query embedding, retrieval, prompt construction, OpenAI chat calls, and citation generation are planned for Phase 3.

## Phase 2 Ingestion Flow

Implemented endpoint:

```text
POST /workspaces/{workspace_id}/documents/{document_id}/ingest
```

The ingestion pipeline runs synchronously for now and follows these stages:

```text
1. Load file
2. Extract content
3. Chunk content
4. Store chunks
5. Prepare vector store abstraction
6. Update document status
```

## Stage 1: Load File

Uploaded files are persisted during:

```text
POST /workspaces/{workspace_id}/documents/upload
```

Files are stored locally under:

```text
UPLOAD_DIR/<workspace_id>/<document_id>/<filename>
```

Document metadata is stored in PostgreSQL with status `uploaded`.

Supported extensions:

- `.pdf`
- `.txt`
- `.md`
- `.csv`

If ingestion starts and the file is missing from storage, the document is marked `failed`.

## Stage 2: Extract Content

Extraction lives in `apps/api/app/ingestion/loaders.py`.

PDF:

- Uses `pypdf`.
- Extracts text page by page.
- Stores page number in section metadata.
- Fails if no extractable text is found.

TXT/Markdown:

- Reads UTF-8 text directly.
- Stores source type metadata.
- Fails if no text is found.

CSV:

- Uses `pandas`.
- Converts each row into searchable text.
- Generates a dataset summary containing:
  - column names
  - row count
  - numeric column min/max/mean
  - missing value counts
- Stores the CSV summary in chunk metadata for Phase 2.

## Stage 3: Chunk Content

Chunking lives in `apps/api/app/ingestion/chunking.py`.

Defaults:

- `chunk_size`: 3500 characters
- `overlap`: 450 characters

The chunker:

- Preserves source metadata such as `page` or `csv_summary`.
- Adds `char_start` and `char_end` offsets.
- Assigns sequential `chunk_index` values.
- Computes an approximate token count using whitespace splitting.

## Stage 4: Store Chunks

Chunk persistence lives in `apps/api/app/ingestion/pipeline.py`.

For each generated chunk, the backend inserts a `document_chunks` row with:

- `document_id`
- `workspace_id`
- `chunk_index`
- `text`
- `token_count`
- `metadata`
- `vector_id`

The current vector id format is:

```text
<document_id>:<chunk_index>
```

Re-ingesting a document deletes the document's existing chunks before inserting the latest chunks.

## Stage 5: Vector Store Abstraction

Phase 2 adds the vector store interface under:

```text
apps/api/app/vectorstores
```

Implemented pieces:

- `VectorStore` protocol
- `EmbeddedChunk`
- `SearchResult`
- `LocalVectorStore`
- `get_vector_store`

`LocalVectorStore` stores provided embeddings in a local JSON file and can perform cosine-similarity queries. The ingestion pipeline does not generate embeddings yet, so it does not upsert vectors in Phase 2.

Embedding generation and vector upsert are planned for Phase 3.

## Stage 6: Document Status Transitions

Document statuses:

- `uploaded`
- `processing`
- `completed`
- `failed`

Ingestion behavior:

```text
uploaded -> processing -> completed
```

On failure:

```text
uploaded -> processing -> failed
```

When ingestion fails, `error_message` is saved on the document. Failures include missing files, unsupported file types, empty extracted content, malformed CSV input, and PDF extraction errors.

## Tests

Phase 2 includes tests for:

- chunking behavior and overlap validation
- CSV summary generation
- CSV row-to-text conversion
- TXT extraction
- successful document ingestion status and chunk storage
- failed ingestion status handling

## Not Implemented Yet

Planned for Phase 3:

- OpenAI embeddings
- Vector upsert during ingestion
- Query embedding
- Workspace-scoped vector retrieval
- RAG prompt construction
- Chat endpoint
- Citation response generation
- Conversation history
- Query logging
