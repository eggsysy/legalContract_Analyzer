import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file safely."""
    print(f"Attempting to read: {pdf_path}")
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract text page by page
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except FileNotFoundError:
        print("Error: The file was not found. Check the path!")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def chunk_text(text, chunk_size=2000, chunk_overlap=400):
    """Splits the text into smaller, overlapping chunks."""
    # Recursive text splitting is a core RAG skill. 
    # It tries to split by paragraphs first, then sentences, keeping ideas intact.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    return chunks

# --- Test Block ---
# This code only runs if you execute this specific file directly
if __name__ == "__main__":
    # We will drop a sample PDF here in the next step
    target_pdf = "data/contracts/sample_nda.pdf"
    
    # Let's make sure the file exists first
    if os.path.exists(target_pdf):
        print("Extracting text...")
        raw_text = extract_text_from_pdf(target_pdf)
        
        if raw_text:
            print(f"Success! Extracted {len(raw_text)} characters.")
            
            print("Chunking text...")
            contract_chunks = chunk_text(raw_text)
            
            print(f"Created {len(contract_chunks)} chunks.")
            print("\n--- Preview of Chunk 1 ---")
            print(contract_chunks[0])
    else:
        print(f"Waiting for a PDF. Please place a file at: {target_pdf}")