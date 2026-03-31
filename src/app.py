import streamlit as st
import os
import shutil  # <-- NEW: Imported to handle deleting old databases

# Import our backend functions
from rag import build_vector_store, ask_contract_question

# 1. Page Configuration
st.set_page_config(page_title="Legal AI", page_icon="⚖️", layout="centered")

st.title("⚖️ AI Legal Contract Analyzer")
st.markdown("Upload a PDF to extract names, dates, and clauses using AI.")

# 2. Sidebar: File Upload
with st.sidebar:
    st.header("📂 Document Upload")
    uploaded_file = st.file_uploader("Upload your PDF contract", type=["pdf"])
    
    if uploaded_file:
        # Create directory if it doesn't exist
        os.makedirs("data/contracts", exist_ok=True)
        file_path = os.path.join("data/contracts", uploaded_file.name)
        
        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Build/Update the Vector Database
        # We use a session state check so it doesn't re-index every time you click a button
        if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            with st.spinner("Analyzing document structure..."):
                
                # --- NEW: Wipe the old database before building a new one ---
                vector_db_path = "data/vector_store"
                if os.path.exists(vector_db_path):
                    shutil.rmtree(vector_db_path)
                # ----------------------------------------------------------
                
                build_vector_store(file_path)
                st.session_state.last_uploaded = uploaded_file.name
                
                # Clear chat history when a new document is uploaded
                st.session_state.messages = []
                
            st.success("Analysis Complete!")
        
        st.divider()
        st.info("💡 **Try asking:**\n- Who are the parties involved?\n- What is the termination period?\n- Is there a non-compete clause?")

# 3. Chat History Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Chat Logic
if prompt := st.chat_input("Ask a question about the document..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    
    # Generate Chat Transcript for Memory
    chat_transcript = ""
    for msg in st.session_state.messages:
        role = "User" if msg["role"] == "user" else "AI"
        chat_transcript += f"{role}: {msg['content']}\n"

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Reviewing document..."):
            try:
                answer = ask_contract_question(prompt, chat_transcript)
                
                st.markdown(answer)
                
                # Save to history
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error("⚠️ Make sure the document is finished processing in the sidebar.")
                st.info("If the error persists, try re-uploading the file.")
                print(f"Detailed Error: {e}")