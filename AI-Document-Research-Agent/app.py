import streamlit as st
import os

from dotenv import load_dotenv

from document_processor import process_uploaded_file
from vector_store import create_vector_store
from qa_engine import get_answer


# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("GOOGLE_API_KEY"):
    st.error(
        "Google API key is missing. "
        "Please configure your .env file."
    )
    st.stop()


# Streamlit configuration
st.set_page_config(
    page_title="AI Document Research Agent",
    page_icon="📚",
    layout="wide"
)


# Custom styling
# st.markdown("""
# <style>

# .stApp {
#     background-color: #f4f7fb;
# }

# .main-title {
#     font-size: 32px;
#     font-weight: bold;
#     color: #1f2937;
# }

# .stButton button {
#     background-color: #2563eb;
#     color: white;
#     border-radius: 8px;
#     padding: 8px 20px;
# }

# </style>
# """, unsafe_allow_html=True)
st.markdown("""
<style>

/* Main application background */
.stApp {
    background-color: #f4f7fb;
}

/* All general text */
.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp div,
.stMarkdown,
.stMarkdown p,
.stMarkdown li {
    color: #000000;
}

/* Main headings */
h1, h2, h3, h4, h5, h6 {
    color: #000000 !important;
}

/* Text area labels */
.stTextArea label {
    color: #000000 !important;
}

/* Text area input */
.stTextArea textarea {
    color: #000000 !important;
    background-color: #ffffff !important;
}

/* Input placeholder */
.stTextArea textarea::placeholder {
    color: #666666 !important;
}

/* Buttons */
.stButton button {
    background-color: #2563eb;
    color: #ffffff !important;
    border-radius: 8px;
    padding: 8px 20px;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #ffffff;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] p {
    color: #000000 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #e8eef5;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #000000 !important;
}

</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="main-title">'
    '📚 AI Document Research Agent'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "Upload documents and ask questions "
    "using AI-powered document research."
)


# Session state
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "document_names" not in st.session_state:
    st.session_state.document_names = []

if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0


# Sidebar

with st.sidebar:

    st.header("PAI Assistant")

    

    uploaded_files = st.file_uploader(
        "Upload your documents",
        type=["pdf", "docx", "xlsx", "xlsm", "txt"],
        accept_multiple_files=True
    )


    if st.button(
        "Process Documents",
        use_container_width=True
    ):

        if not uploaded_files:
            st.warning(
                "Please upload at least one document."
            )

        else:

            all_documents = []
            errors = []

            progress = st.progress(0)

            for index, file in enumerate(
                uploaded_files
            ):

                try:
                    documents = process_uploaded_file(
                        file
                    )

                    all_documents.extend(documents)

                except Exception as error:
                    errors.append(
                        f"{file.name}: {str(error)}"
                    )

                progress.progress(
                    (index + 1) / len(uploaded_files)
                )

            if errors:
                for error in errors:
                    st.error(error)

            if all_documents:

                try:
                    with st.spinner(
                        "Creating vector database..."
                    ):

                        vector_store, chunk_count = (
                            create_vector_store(
                                all_documents
                            )
                        )

                    st.session_state.vector_store = (
                        vector_store
                    )

                    st.session_state.document_names = [
                        file.name for file in uploaded_files
                    ]

                    st.session_state.chunk_count = (
                        chunk_count
                    )

                    st.success(
                        "Documents processed successfully!"
                    )

                except Exception as error:
                    st.error(
                        f"Indexing failed: {error}"
                    )


    st.divider()

    st.subheader("Knowledge Base")

    if st.session_state.vector_store:

        st.write(
            f"Documents: "
            f"{len(st.session_state.document_names)}"
        )

        st.write(
            f"Chunks: "
            f"{st.session_state.chunk_count}"
        )

        for name in st.session_state.document_names:
            st.caption(f"📄 {name}")

    else:
        st.info("No documents indexed yet.")


# Main question-answering section
st.subheader("Ask Your Documents")

question = st.text_area(
    "Enter your question",
    placeholder="Example: What is the main topic of this document?",
    height=100
)


if st.button("Generate Answer"):

    if not question.strip():
        st.warning("Please enter a question.")

    elif st.session_state.vector_store is None:
        st.warning(
            "Please upload and process documents first."
        )

    else:

        try:

            with st.spinner(
                "Searching documents and generating answer..."
            ):

                result = get_answer(
                    st.session_state.vector_store,
                    question
                )

            st.divider()

            st.subheader("Generated Answer")

            st.markdown(result["answer"])

            if result["warnings"]:

                st.warning(
                    "Potential security issues detected "
                    "in retrieved document content."
                )

                for warning in result["warnings"]:
                    st.write(f"- {warning}")

            st.subheader("Source References")

            if result["sources"]:

                for source in result["sources"]:

                    with st.expander(
                        f"{source['id']} - "
                        f"{source['document']} "
                        f"{source['location']}"
                    ):

                        st.write(source["content"])

            else:
                st.info("No sources were retrieved.")

        except Exception as error:

            st.error(
                f"An error occurred: {str(error)}"
            )
