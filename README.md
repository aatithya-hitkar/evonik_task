# Recipe Search with AI

I got tired of scrolling through long recipe blogs just to find cooking instructions, so I built this recipe search tool that uses AI to find and explain recipes from my collection. This project includes two different RAG (Retrieval-Augmented Generation) implementations to choose from.

## What it does

Ask questions about cooking and it searches through 15 recipes using AI embeddings, then gives you helpful answers using ChatGPT. Way better than keyword matching.

## RAG Implementations

This project provides two different approaches to recipe search:

### 1. Simple RAG (`rag_query.py`)
- **Traditional RAG approach**: Directly searches the vector store and includes retrieved context in the prompt
- **How it works**: Retrieves relevant recipes first, then generates response based on the context
- **Best for**: Straightforward question-answering scenarios
- **Pros**: Simple, predictable, fast
- **Cons**: Always searches even for non-recipe questions

### 2. Tool-calling RAG (`tool_rag_query.py`)
- **Function-calling approach**: Uses OpenAI's function calling feature where the LLM decides when to search
- **How it works**: LLM analyzes the question and calls the search tool only when needed
- **Best for**: More conversational interactions and mixed question types
- **Pros**: More intelligent, can handle non-recipe questions gracefully
- **Cons**: Slightly more complex, may use more tokens

## Setup

1. Make sure you have Python 3.11+ installed

2. Install the requirements:
```bash
pip install -r requirements.txt
```

3. Add your OpenAI API key to the `.env` file (it's already there, just make sure it works)

4. Run either version:

**Simple RAG:**
```bash
python rag_query.py
```

**Tool-calling RAG:**
```bash
python tool_rag_query.py
```

## How to use

Just ask cooking questions like:
- "How do I make carbonara?"
- "What's a good vegetarian dinner?"
- "How long should I cook quinoa?"
- "What can I substitute for eggs in baking?"

Both systems will find relevant recipes and give you practical answers. The tool-calling version can also handle follow-up questions and non-recipe queries more naturally.

## Files

### Core Files
- `rag_query.py` - Simple RAG implementation
- `tool_rag_query.py` - Tool-calling RAG implementation
- `vector_store.py` - Handles the AI search functionality
- `recipe_data.json` - All the recipes (15 recipes)
- `recipe_embeddings.faiss` - Pre-built search index
- `recipe_metadata.pkl` - Recipe data for search results

### Configuration & Dependencies
- `requirements.txt` - Python packages needed
- `.env` - OpenAI API key configuration

### Evaluation & Documentation
- `evaluation_script.py` - Performance evaluation script
- `evaluation_dataset.json` - Test cases for evaluation
- `evaluation_results.md` - Detailed evaluation results
- `design_documentation.md` - Technical documentation

## Notes

- The first time you run either version, it might take a few seconds to load the recipe database
- Both implementations use the same underlying vector store and recipe data
- Choose the simple RAG for straightforward use cases, or tool-calling RAG for more interactive experiences
- The evaluation shows both approaches achieve good performance (83% hit rate, 89% quality score)
