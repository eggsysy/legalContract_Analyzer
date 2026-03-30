import streamlit as st
import os

# Import our backend functions!
from rag import build_vector_store, ask_contract_question

# Set up the page layout
st.set_page_config(page_title="AI Contract Analyzer", page_icon="⚖️", layout="centered")

st.title("⚖️ AI Legal Contract Analyzer")
st.markdown("Upload a PDF document and ask questions. The AI will extract the answers directly from the text.")

# --- SIDEBAR: File Upload ---
with st.sidebar:
    st.header("📂 Document Upload")
    uploaded_file = st.file_uploader("Upload your PDF contract here", type=["pdf"])
    
    if uploaded_file is not None:
        # Save the uploaded file to our data folder
        file_path = f"data/contracts/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Build the database
        with st.spinner("Analyzing document and building vector database..."):
            build_vector_store(file_path)
        st.success("Database built! You can now ask questions.")
        st.divider()
        st.info("💡 **Pro Tip:** Ask things like 'What is the termination clause?' or 'Who are the parties involved?'")

# --- MAIN PAGE: Chat Interface ---
# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a question about the document..."):
    # 1. Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Searching document..."):
            try:
                # Call the backend we built!
                answer = ask_contract_question(prompt)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error("⚠️ Please upload a document in the sidebar first!")
                print(f"Error: {e}")