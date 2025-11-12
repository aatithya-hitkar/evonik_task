# RAG System Design

## Architecture Overview

- **Ingestion**: Load 15 recipes from JSON file into memory
- **Chunking**: Each complete recipe (title, ingredients, instructions) forms one chunk
- **Embedding**: Generate embeddings using OpenAI text-embedding-3-mini model
- **Retrieval**: FAISS vector store with cosine similarity, returns top-3 matches
- **Generation**: GPT-5-mini generates responses based on retrieved recipe context
- **Guardrails**: System prompt restricts responses to recipe-related queries only
