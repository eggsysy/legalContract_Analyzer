import os
import time
import chromadb
from dotenv import load_dotenv

# Using the classic package for these specific chain constructors
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# Import your ingestion logic
from ingestion import extract_text_from_pdf, chunk_text

load_dotenv()

VECTOR_STORE_PATH = "data/vector_store"
COLLECTION_NAME = "legal_docs"

# Module-level singleton — one PersistentClient for the entire process lifetime.
# This prevents stale file-handle bugs when Streamlit reruns the script.
_chroma_client = None

def _get_chroma_client():
    """Return (or create) a single PersistentClient for this process.
    
    Reusing one client avoids the Rust/SQLite file-handle conflicts that
    occur when multiple PersistentClient instances point at the same path.
    """
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)
    return _chroma_client

def reset_vector_store():
    """Cleanly wipe the old collection through ChromaDB's API.
    
    This replaces shutil.rmtree — never delete the SQLite files on disk
    while the Rust backend has open handles on them.
    """
    client = _get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Old collection deleted.")
    except Exception:
        # Collection didn't exist yet — that's fine.
        pass

def build_vector_store(pdf_path):
    """Reads a PDF, chunks it, and saves it into a searchable Vector Database."""
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text: 
        return None
        
    chunks = chunk_text(raw_text)
    print(f"Loaded {len(chunks)} chunks. Vectorizing...")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Wipe any existing collection, then create a fresh one
    reset_vector_store()
    client = _get_chroma_client()
    
    vector_store = Chroma.from_texts(
        texts=chunks, 
        embedding=embeddings,
        client=client,
        collection_name=COLLECTION_NAME,
    )
    return vector_store

def get_retriever():
    """Returns a retriever using MMR to ensure a diverse set of document chunks."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    client = _get_chroma_client()
    
    vector_store = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )
    
    # MMR (Maximal Marginal Relevance) is better for legal docs 
    # because it avoids picking 5 identical boilerplate paragraphs.
    return vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 15, "fetch_k": 30}
    )

def ask_contract_question(question, chat_history=""):
    """Searches the document and STREAMS the text answer back."""
    
    # Initialize the AI
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    # IMPROVED PROMPT: Instructs AI to look for specific entity names in headers
    system_prompt = (
        "You are a precise legal assistant. Your task is to identify specific details "
        "from the provided contract context.\n\n"
        "IMPORTANT GUIDELINES:\n"
        "1. Look for entity names (companies/individuals) near the top of the document.\n"
        "2. CORPORATE ENTITY VS SIGNATORY: Do not confuse the corporate entity (the company itself) "
        "with the human authorized signatory (the person signing at the bottom). If asked 'Who is the party?', "
        "provide the company name (e.g., Nova Solutions LLC), NOT the employee signing it (e.g., Jane Smith).\n"
        "3. Use ONLY the provided context. If the specific name is missing, say you cannot find it.\n\n"
        "Previous Conversation History:\n{chat_history}\n\n"
        "Retrieved Context:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    retriever = get_retriever()
    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)
    
    print(f"\nAnalyzing (Streaming): '{question}'...")
    
    # --- NEW: Streaming Logic ---
    # We iterate through the chain's stream instead of calling invoke()
    for chunk in rag_chain.stream({
        "input": question, 
        "chat_history": chat_history
    }):
        # The chain outputs dictionary chunks. We only want to yield the actual answer text.
        if "answer" in chunk:
            yield chunk["answer"]
            time.sleep(0.03)

# --- Test Block ---
if __name__ == "__main__":
    import sys # Needed for flush printing
    print("--- Testing the AI Pipeline (Streaming) ---")
    
    test_question = "Who is the Disclosing Party and who is the Receiving Party?"
    
    try:
        # Get the generator object
        stream_generator = ask_contract_question(test_question)
        
        print("\n🤖 AI Assistant says:")
        print("-" * 30)
        
        # Iterate over the generator and print chunk by chunk
        for text_chunk in stream_generator:
            print(text_chunk, end="", flush=True)
            
        print("\n" + "-" * 30)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")