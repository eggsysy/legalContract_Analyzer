import os
from dotenv import load_dotenv

# LangChain Vector & Embeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# LangChain LLM & Prompts
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Import your working ingestion code
from ingestion import extract_text_from_pdf, chunk_text

# Load the secret API key from your .env file
load_dotenv()

VECTOR_STORE_PATH = "data/vector_store"

def build_vector_store(pdf_path):
    """Reads a PDF, chunks it, and saves it into a searchable Vector Database."""
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text: return None
        
    chunks = chunk_text(raw_text)
    print(f"Loaded {len(chunks)} chunks. Vectorizing...")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma.from_texts(
        texts=chunks, 
        embedding=embeddings,
        persist_directory=VECTOR_STORE_PATH
    )
    return vector_store

def get_retriever():
    """Loads the saved database so we can search it."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma(
        persist_directory=VECTOR_STORE_PATH, 
        embedding_function=embeddings
    )
    return vector_store.as_retriever(search_kwargs={"k": 3})

def ask_contract_question(question):
    """Searches the document and asks Gemini to answer based ONLY on those findings."""
    
    # 1. Initialize the AI (Temperature 0 means it will be factual, not creative)
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
    
    # 2. Prompt Engineering: Give the AI strict rules
    system_prompt = (
        "You are an expert legal and technical assistant. "
        "Use ONLY the following pieces of retrieved context to answer the user's question. "
        "If the answer is not in the context, strictly reply with: 'I cannot find the answer in the provided document.' "
        "Do not make up information.\n\n"
        "Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # 3. Build the RAG Pipeline (Search -> Format Context -> Prompt -> LLM)
    retriever = get_retriever()
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # 4. Execute the chain
    print(f"\nThinking about: '{question}'...")
    answer = rag_chain.invoke(question)
    
    return answer

# --- Test Block ---
if __name__ == "__main__":
    print("--- Testing the Full AI Pipeline ---")
    
    # Let's test it with the PDF you already vectorized earlier!
    test_question = "What is the formula to encrypt a character?"
    
    try:
        answer = ask_contract_question(test_question)
        print("\n🤖 AI Assistant says:")
        print("=" * 50)
        print(answer)
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Error connecting to the AI: {e}")
        print("Did you make sure your .env file has exactly: GOOGLE_API_KEY=\"your_key_here\" ?")