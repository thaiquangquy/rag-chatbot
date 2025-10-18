```markdown
# data-model.md — RAG Chatbot Entities

## Document

- document_id: string (Google Drive ID, primary key)
- title: string
- url: string
- mime_type: string
- owner: string (email)
- created_at: timestamp
- updated_at: timestamp
- last_indexed: timestamp
- content_hash: string
- size_bytes: integer
- ingestion_status: enum [pending, succeeded, failed]

## Section

- section_id: uuid
- document_id: string (FK -> Document.document_id)
- title: string
- content: text
- char_offset_start: integer
- char_offset_end: integer
- embedding_id: uuid
- embedding_vector: vector (stored in vector store)
- created_at: timestamp

## Query

- query_id: uuid
- user_id: string
- text: string
- session_id: uuid
- embedding_id: uuid
- timestamp: timestamp

## Response

- response_id: uuid
- query_id: uuid
- generated_text: text
- source_sections: array of { section_id, document_id, snippet, url }
- confidence_score: float
- created_at: timestamp

## Conversation

- conversation_id: uuid
- user_id: string
- created_at: timestamp
- last_active_at: timestamp
- messages: ordered list of message references (query_id/response_id)

## Contracts to enforce

- Document.content hash validation (reject if empty)
- Section size limit (max 8k chars per section)
- Embedding vector dimension consistent with provider
```
