import os
import re
from collections import deque

from dotenv import load_dotenv
from openai import OpenAI

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_huggingface import (
    HuggingFaceEmbeddings
)

from langchain_community.vectorstores import (
    FAISS
)

# ==================================================
# ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ==================================================
# CHAT MEMORY
# ==================================================

chat_history = deque(maxlen=10)

# ==================================================
# LANGUAGE DETECTION
# ==================================================

def detect_language(text):

    arabic_pattern = re.compile(r'[\u0600-\u06FF]')

    if arabic_pattern.search(text):
        return "Arabic"

    return "English"

# ==================================================
# LOAD DOCUMENTS
# ==================================================

def load_documents(file_paths):

    documents = []

    for file_path in file_paths:

        extension = os.path.splitext(
            file_path
        )[1].lower()

        try:

            if extension == ".pdf":

                loader = PyPDFLoader(
                    file_path
                )

            elif extension == ".txt":

                loader = TextLoader(
                    file_path,
                    encoding="utf-8"
                )

            elif extension == ".csv":

                loader = CSVLoader(
                    file_path
                )

            elif extension == ".docx":

                loader = (
                    UnstructuredWordDocumentLoader(
                        file_path
                    )
                )

            elif extension == ".md":

                loader = TextLoader(
                    file_path,
                    encoding="utf-8"
                )

            else:

                print(
                    f"Unsupported file: {file_path}"
                )

                continue

            docs = loader.load()

            documents.extend(docs)

        except Exception as e:

            print(
                f"Error loading {file_path}: {e}"
            )

    return documents

# ==================================================
# CHUNKING
# ==================================================

def split_chunks(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(
        documents
    )

    return chunks

# ==================================================
# EMBEDDINGS
# ==================================================

def get_embeddings():

    embeddings = HuggingFaceEmbeddings(
        model_name=
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    return embeddings

# ==================================================
# CREATE VECTORSTORE
# ==================================================

def create_vectorstore(
    chunks,
    embeddings
):

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    vectorstore.save_local(
        "faiss_db"
    )

    return vectorstore

# ==================================================
# LOAD VECTORSTORE
# ==================================================

def load_vectorstore(
    embeddings
):

    if not os.path.exists(
        "faiss_db"
    ):

        return None

    vectorstore = FAISS.load_local(
        "faiss_db",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore

# ==================================================
# RETRIEVAL
# ==================================================

def retrieve(
    vectorstore,
    query,
    k=4
):

    results = vectorstore.similarity_search(
        query,
        k=k
    )

    return results

# ==================================================
# GENERATE ANSWER
# ==================================================

def generate_answer(
    context,
    question
):

    language = detect_language(
        question
    )

    history_text = "\n".join(
        chat_history
    )

    if language == "Arabic":

        not_found_message = (
            "لم أتمكن من العثور على هذه المعلومة في الملفات المرفوعة."
        )

    else:

        not_found_message = (
            "I couldn't find this information in the uploaded documents."
        )

    prompt = f"""
You are a helpful RAG assistant.

Answer ONLY using the provided context.

DO NOT use outside knowledge.

If the answer is not found in the context,
reply exactly with:

{not_found_message}

Language Rules:
- If user language is Arabic, answer in Arabic.
- If user language is English, answer in English.
- Always use the same language as the user.

Conversation History:
{history_text}

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
    model="openai/gpt-oss-20b:free",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

    answer = response.choices[0].message.content.strip()
    try:

       answer = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    except Exception:

        answer = "Error generating response."

        chat_history.append(
        f"User: {question}"
    )

    chat_history.append(
        f"Assistant: {answer}"
    )

    return answer
