# API Specification

Base URL for local development:

```text
http://localhost:8000
```

Phase 1 uses a demo user created automatically from `DEMO_USER_EMAIL`.

## Health

### `GET /health`

Returns backend status.

Response `200`:

```json
{
  "status": "ok"
}
```

## Workspaces

### `POST /workspaces`

Creates a workspace owned by the demo user.

Request:

```json
{
  "name": "Acme Knowledge Base"
}
```

Response `201`:

```json
{
  "id": "6d5779be-983a-42cf-9855-f9e178dc8334",
  "name": "Acme Knowledge Base",
  "owner_id": "6a154bbf-6e91-462c-ac4c-30be99dfd5f0",
  "created_at": "2026-05-05T06:30:00Z"
}
```

### `GET /workspaces`

Lists workspaces owned by the demo user.

Response `200`:

```json
[
  {
    "id": "6d5779be-983a-42cf-9855-f9e178dc8334",
    "name": "Acme Knowledge Base",
    "owner_id": "6a154bbf-6e91-462c-ac4c-30be99dfd5f0",
    "created_at": "2026-05-05T06:30:00Z"
  }
]
```

## Documents

### `POST /workspaces/{workspace_id}/documents/upload`

Uploads a PDF, TXT, Markdown, or CSV file and creates document metadata with status `uploaded`.

Content type:

```text
multipart/form-data
```

Form fields:

- `file`: uploaded document file

Supported extensions:

- `.pdf`
- `.txt`
- `.md`
- `.csv`

Response `201`:

```json
{
  "id": "65be9ecc-4520-42f4-ae16-cf028ce70f58",
  "workspace_id": "6d5779be-983a-42cf-9855-f9e178dc8334",
  "filename": "quarterly_report.pdf",
  "file_type": "pdf",
  "status": "uploaded",
  "error_message": null,
  "created_at": "2026-05-05T06:35:00Z",
  "updated_at": "2026-05-05T06:35:00Z"
}
```

Errors:

- `400`: unsupported file type
- `404`: workspace not found

### `GET /workspaces/{workspace_id}/documents`

Lists uploaded documents for a workspace.

Response `200`:

```json
[
  {
    "id": "65be9ecc-4520-42f4-ae16-cf028ce70f58",
    "workspace_id": "6d5779be-983a-42cf-9855-f9e178dc8334",
    "filename": "quarterly_report.pdf",
    "file_type": "pdf",
    "status": "uploaded",
    "error_message": null,
    "created_at": "2026-05-05T06:35:00Z",
    "updated_at": "2026-05-05T06:35:00Z"
  }
]
```

Errors:

- `404`: workspace not found

### `POST /workspaces/{workspace_id}/documents/{document_id}/ingest`

Runs ingestion for one uploaded document.

The backend:

1. marks the document `processing`
2. loads the persisted file
3. extracts text or CSV row content
4. chunks the extracted content
5. stores chunks in PostgreSQL
6. marks the document `completed` or `failed`

Response `200` on successful ingestion:

```json
{
  "document": {
    "id": "65be9ecc-4520-42f4-ae16-cf028ce70f58",
    "workspace_id": "6d5779be-983a-42cf-9855-f9e178dc8334",
    "filename": "quarterly_report.txt",
    "file_type": "txt",
    "status": "completed",
    "error_message": null,
    "created_at": "2026-05-05T06:35:00Z",
    "updated_at": "2026-05-05T06:36:00Z"
  },
  "chunk_count": 3
}
```

Response `200` when ingestion runs but fails:

```json
{
  "document": {
    "id": "65be9ecc-4520-42f4-ae16-cf028ce70f58",
    "workspace_id": "6d5779be-983a-42cf-9855-f9e178dc8334",
    "filename": "quarterly_report.txt",
    "file_type": "txt",
    "status": "failed",
    "error_message": "Uploaded file not found: uploads/...",
    "created_at": "2026-05-05T06:35:00Z",
    "updated_at": "2026-05-05T06:36:00Z"
  },
  "chunk_count": 0
}
```

Errors:

- `404`: workspace or document not found

## Not Implemented Yet

These endpoints are planned for later phases:

- `POST /workspaces/{workspace_id}/chat`
- `GET /workspaces/{workspace_id}/conversations`
- `GET /workspaces/{workspace_id}/analytics`
