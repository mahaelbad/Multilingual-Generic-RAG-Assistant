# Generic RAG Assistant

A Retrieval-Augmented Generation (RAG) chatbot that allows users to upload multiple documents and ask questions about them.

## Features

- Upload multiple documents
- Supports:
  - PDF
  - DOCX
  - TXT
  - CSV
  - MD
- FAISS Vector Database
- HuggingFace Embeddings
- OpenRouter LLM
- Arabic & English Responses
- Chat Memory
- Rebuild Vector Database on New Upload

## Tech Stack

- Python
- Streamlit
- LangChain
- FAISS
- HuggingFace Embeddings
- OpenRouter

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```