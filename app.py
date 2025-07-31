import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import UnstructuredURLLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain.chains.summarize import load_summarize_chain
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter # New import
import validators
import os
import base64
from PIL import Image
import time
from ytUtils import get_transcript_as_document, validate_youtube_url

# --- Utility Functions ---
def summarize_chain(docs, llm, chain_type="stuff"):
    """
    Generates a detailed summary from a list of documents.
    Supports 'stuff' for single-chunk documents and 'map_reduce' for multi-chunk documents.
    """
    if chain_type == "stuff":
        prompt_template = """
        Provide a detailed summary of the following content. The summary should be:
        - Comprehensive yet concise, capturing all key points, concepts, and arguments.
        - Well-structured with clear headings, bullet points, or numbered lists to organize the information.
        - Easy to read and understand for someone unfamiliar with the topic.

        CONTENT:
        {text}

        DETAILED SUMMARY:
        """
        prompt = PromptTemplate.from_template(prompt_template)
        chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
        return chain.run(docs)
    elif chain_type == "map_reduce":
        # For larger documents, summarize each chunk and then combine the summaries.
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        return chain.run(docs)
    else:
        raise ValueError(f"Invalid chain_type: {chain_type}")

def generate_quiz_chain(docs, llm):
    """Generates a practice quiz from a list of documents."""
    prompt_template = """
    Based on the following content, generate a practice quiz with 5-7 multiple-choice questions.
    For each question, provide four options (A, B, C, D) and clearly indicate the correct answer.
    The questions should cover the main concepts and key details from the text.

    CONTENT:
    {text}

    PRACTICE QUIZ:
    """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    return chain.run(docs)

def generate_audio(text):
    """Placeholder for audio generation. Returns dummy data."""
    # In a real app, this would call a Text-to-Speech API
    dummy_audio_bytes = b"dummy_audio_data"
    b64_audio = base64.b64encode(dummy_audio_bytes).decode()
    return dummy_audio_bytes, b64_audio

# --- Streamlit App Code ---
st.set_page_config(
    page_title="Zummary - AI Content Tools",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    .input-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    .output-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border-left: 5px solid #667eea;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: transform 0.3s ease;
        width: 100%;
        height: 60px;
        font-size: 1.1rem;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'llm' not in st.session_state:
    st.session_state.llm = None

# --- Sidebar for API Key ---
st.sidebar.header("🔑 API Configuration")
st.sidebar.markdown("Enter your Groq API key to activate the app. You can get a free key from [GroqCloud](https://console.groq.com/keys).")
groq_api_key = st.sidebar.text_input("Groq API Key", type="password")

# --- Main App Logic ---
st.markdown("""
<div class="main-header">
    <h1>🎯 Zummary</h1>
    <p>AI-Powered Content Tools: Summaries, Quizzes & More</p>
</div>
""", unsafe_allow_html=True)

if not groq_api_key:
    st.warning("Please enter your Groq API key in the sidebar to get started.", icon="👈")
    st.stop()
    
# Initialize LLM only if the key is present and the LLM isn't already in session state
if 'llm' not in st.session_state or st.session_state.llm is None:
    st.session_state.llm = ChatGroq(
        api_key=groq_api_key,
        model_name="gemma2-9b-it" 
    )

llm = st.session_state.llm

st.markdown("### Choose Your Content Type")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎥</div>
        <div class="feature-title">YouTube Videos</div>
        <div class="feature-desc">Extract and summarize video transcripts</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Summarize YouTube", key="youtube_btn"):
        st.session_state.mode = "youtube"
        st.rerun()

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🌐</div>
        <div class="feature-title">Web Articles</div>
        <div class="feature-desc">Analyze and summarize content from any URL</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Summarize Website", key="web_btn"):
        st.session_state.mode = "web"
        st.rerun()

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📄</div>
        <div class="feature-title">PDF Documents</div>
        <div class="feature-desc">Upload and process PDF files with text extraction</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Summarize PDF", key="pdf_btn"):
        st.session_state.mode = "pdf"
        st.rerun()

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">✍️</div>
        <div class="feature-title">Practice Quiz</div>
        <div class="feature-desc">Generate a quiz from your notes or any text</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Quiz", key="quiz_btn"):
        st.session_state.mode = "quiz"
        st.rerun()

# --- Processing Logic for Each Mode ---
if st.session_state.mode == "quiz":
    st.markdown("### ✍️ Practice Quiz Generator")
    with st.container(border=True):
        st.markdown("**Paste your text, article, or notes below to generate a quiz.**")
        text_input = st.text_area("Text for Quiz:", height=250, placeholder="Paste your content here...")
        
        if st.button("🎯 Generate Practice Quiz", key="process_quiz"):
            if text_input.strip():
                try:
                    with st.spinner("🧠 Generating your quiz..."):
                        docs = [Document(page_content=text_input)]
                        quiz_output = generate_quiz_chain(docs, llm)

                    st.markdown('<div class="output-container">', unsafe_allow_html=True)
                    st.markdown("### 📝 Your Practice Quiz")
                    st.markdown(quiz_output)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error generating quiz: {str(e)}")
            else:
                st.warning("Please paste some text to generate a quiz from.")

elif st.session_state.mode == "youtube":
    st.markdown("### 🎥 YouTube Video Summarizer")
    with st.container(border=True):
        st.markdown("**Enter YouTube Video URL**")
        url = st.text_input("", placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ", key="youtube_url")
        
        if st.button("🎯 Generate Summary", key="process_youtube"):
            is_valid_url, error_message = validate_youtube_url(url)
            if is_valid_url:
                try:
                    with st.spinner("🔄 Fetching transcript and summarizing..."):
                        docs = get_transcript_as_document(url)
                        
                        if docs:
                            output_summary = summarize_chain(docs, llm)
                            st.markdown('<div class="output-container">', unsafe_allow_html=True)
                            st.markdown("### 📋 Summary")
                            st.markdown(output_summary)
                            st.markdown('</div>', unsafe_allow_html=True)
                except RuntimeError as e:
                    st.error(f"❌ Error processing YouTube video: {str(e)}")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred while processing the video: {str(e)}")
            else:
                st.error(f"❌ Invalid YouTube URL: {error_message}")

elif st.session_state.mode == "web":
    st.markdown("### 🌐 Website Article Summarizer")
    with st.container(border=True):
        st.markdown("**Enter Website URL**")
        url = st.text_input("", placeholder="https://example.com/article", key="web_url")
        
        if st.button("🎯 Generate Summary", key="process_web"):
            if validators.url(url):
                try:
                    with st.spinner("🔄 Loading content and summarizing..."):
                        loader = UnstructuredURLLoader(urls=[url], ssl_verify=False, headers={"User-Agent": "Mozilla/5.0"})
                        docs = loader.load()
                        
                        if not docs or not docs[0].page_content.strip():
                            st.error("❌ Could not extract content from the URL. The page might be protected, require login, or use dynamic content that's hard to scrape.")
                        else:
                            output_summary = summarize_chain(docs, llm)
                            st.markdown('<div class="output-container">', unsafe_allow_html=True)
                            st.markdown("### 📋 Summary")
                            st.markdown(output_summary)
                            st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error processing website: {str(e)}. Please check the URL or try another.")
            else:
                st.error("❌ Please enter a valid URL.")

elif st.session_state.mode == "pdf":
    st.markdown("### 📄 PDF Document Summarizer")
    with st.container(border=True):
        st.markdown("**Upload PDF Files**")
        uploaded_files = st.file_uploader("", type="pdf", accept_multiple_files=True)
        
        if st.button("🎯 Generate Summary", key="process_pdf"):
            if uploaded_files:
                try:
                    with st.spinner("🔄 Processing PDFs and summarizing..."):
                        all_docs = []
                        for uploaded_file in uploaded_files:
                            temp_file_path = os.path.join(os.getcwd(), uploaded_file.name)
                            with open(temp_file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            loader = PyPDFLoader(temp_file_path)
                            all_docs.extend(loader.load())
                            os.remove(temp_file_path)
                        
                        if not all_docs:
                            st.error("❌ Could not extract text from the PDF files. They might be scanned images or contain no readable text.")
                        else:
                            # Use RecursiveCharacterTextSplitter to split large documents
                            text_splitter = RecursiveCharacterTextSplitter(
                                chunk_size=2000, 
                                chunk_overlap=100
                            )
                            split_docs = text_splitter.split_documents(all_docs)

                            # Now, pass the split documents and use the "map_reduce" chain
                            output_summary = summarize_chain(split_docs, llm, chain_type="map_reduce")
                            
                            st.markdown('<div class="output-container">', unsafe_allow_html=True)
                            st.markdown("### 📋 Summary")
                            st.markdown(output_summary)
                            st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}. Please ensure the PDF is not corrupted or try another.")
            else:
                st.warning("Please upload at least one PDF file.")

if st.session_state.mode:
    st.markdown("---")
    if st.button("🔄 Select Another Tool", key="reset"):
        st.session_state.mode = None
        st.rerun()
        
