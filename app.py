import os
import shutil
import streamlit as st

from rag import (
    load_documents,
    split_chunks,
    get_embeddings,
    create_vectorstore,
    load_vectorstore,
    retrieve,
    generate_answer,
    chat_history
)

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Generic RAG Assistant",
    page_icon="🤖",
    layout="centered"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.block-container{
    max-width:900px;
    padding-top:2rem;
}

.main-title{
    text-align:center;
    font-size:48px;
    font-weight:700;
}

.sub-title{
    text-align:center;
    color:#9CA3AF;
    font-size:18px;
    margin-bottom:30px;
}

.stChatMessage p{
    font-size:18px !important;
    line-height:1.8;
}

section[data-testid="stSidebar"]{
    background-color:#111827;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================

st.markdown("""
<div class="main-title">
🤖 Generic RAG Assistant
</div>

<div class="sub-title">
Upload documents and ask questions about them
</div>
""", unsafe_allow_html=True)

# ==================================================
# SESSION STATE
# ==================================================

if "database_ready" not in st.session_state:
    st.session_state.database_ready = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("📂 Upload Documents")

    uploaded_files = st.file_uploader(
        "Supported: PDF, DOCX, TXT, CSV, MD",
        type=["pdf", "docx", "txt", "csv", "md"],
        accept_multiple_files=True
    )

    process_btn = st.button(
        "🚀 Process Documents"
    )

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):

       st.session_state.messages = []

       chat_history.clear()

       st.rerun()

# ==================================================
# PROCESS DOCUMENTS
# ==================================================

if process_btn:

    if not uploaded_files:

        st.warning(
            "Please upload at least one document."
        )

    else:

        with st.spinner(
            "Processing documents..."
        ):

            # delete old database

            if os.path.exists("faiss_db"):

                shutil.rmtree(
                    "faiss_db"
                )
            if os.path.exists("uploads"):

                shutil.rmtree("uploads")
            os.makedirs(
                   "uploads",
                    exist_ok=True
                      )

            # create uploads folder

            file_paths = []

            for file in uploaded_files:

                file_path = os.path.join(
                    "uploads",
                    file.name
                )

                with open(
                    file_path,
                    "wb"
                ) as f:

                    f.write(
                        file.getbuffer()
                    )

                file_paths.append(
                    file_path
                )

            try:

                docs = load_documents(
                    file_paths
                )

                chunks = split_chunks(
                    docs
                )

                embeddings = (
                    get_embeddings()
                )

                create_vectorstore(
                    chunks,
                    embeddings
                )
                # Clear old memory
                chat_history.clear()
                # Clear old chat messages
                st.session_state.messages = []

                st.session_state.database_ready = True

                st.success(
                    "Documents processed successfully."
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )

# ==================================================
# LOAD DATABASE
# ==================================================

embeddings = get_embeddings()

vectorstore = load_vectorstore(
    embeddings
)

if vectorstore is not None:

    st.session_state.database_ready = True

# ==================================================
# DISPLAY CHAT
# ==================================================

for message in st.session_state.messages:

    avatar = (
        "👤"
        if message["role"] == "user"
        else "🤖"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        st.markdown(
            message["content"]
        )

# ==================================================
# CHAT INPUT
# ==================================================

question = st.chat_input(
    "Ask a question..."
)

if question:

    if not st.session_state.database_ready:

        st.warning(
            "Please upload and process documents first."
        )

        st.stop()

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.markdown(
            question
        )

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner(
            "Thinking..."
        ):

            results = retrieve(
                vectorstore,
                question
            )

            context = "\n\n".join(
                [
                    doc.page_content
                    for doc in results
                ]
            )

            answer = generate_answer(
                context,
                question
            )

            st.markdown(
                answer
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
