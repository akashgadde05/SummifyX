import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import UnstructuredURLLoader, PyPDFLoader
from generalUtils import summarize_chain, generate_audio    # helper functions for generating summary and audio
from ytUtils import get_transcript_as_document              # helper function for fetching transcript of YT vidoes
import validators
import os
from dotenv import load_dotenv
import base64
from PIL import Image

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
groq_api_key = st.secrets["GROQ_API_KEY"]

# App title and description
## App logo
img = Image.open("summify_logo.jpg")
col1, col2, col3, col4, col5 = st.columns(5)
with col3:
    st.image(img)

st.markdown("""
<div style="text-align:center;">
    <h1 style="margin-top:10px;">Summarize Text On the Go!</h1>
    <p style="color:yellow;">From Long to Short — SummarizeX Delivers It All!-
                        BY AKASH GADDE</p>
</div>
""", unsafe_allow_html=True)

# Initializing LLM 
llm = ChatGroq(model="gemma2-9b-it", groq_api_key=groq_api_key)

if "mode" not in st.session_state:
    st.session_state.mode = None

# Button logic
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🎥 YouTube Video Summary"):
        st.session_state.mode = "youtube"
with col2:
    if st.button("🌐 Website URL Summary"):
        st.session_state.mode = "web"
with col3:
    if st.button("📄 PDF Summary"):
        st.session_state.mode = "pdf"


# Based on selected mode
if st.session_state.mode == "youtube":
    url = st.text_input("Enter YouTube Video URL:")
    if url:
        if not validators.url(url) or "youtube.com" not in url:
            st.error("Please enter a valid & complete YouTube URL.")
        else:
            try:
                with st.spinner("Loading and summarizing video..."):
                    docs = get_transcript_as_document(url)
                    output_summary = summarize_chain(docs, llm)     

                    # Generating audio for summary
                    audio_data, b64 = generate_audio(output_summary)
                    st.audio(audio_data, format="audio/mp3")
                    st.markdown(f'<div style="text-align: right;"><a href="data:audio/mp3;base64,{b64}" download="summary.mp3">Download Audio Summary</a></div>',unsafe_allow_html=True)
                    
                    st.write("Summary:")
                    st.success(output_summary)
                    
                    # Creating Download link
                    b64 = base64.b64encode(output_summary.encode()).decode()
                    st.markdown(f'<div style="text-align: right;"><a href="data:file/txt;base64,{b64}" download="summary.txt">Download Text Summary</a></div>',unsafe_allow_html=True)

            except Exception as e:
                st.exception(f"Exception: {e}")

elif st.session_state.mode == "web":
    url = st.text_input("Enter Website URL:")
    if url:
        if not validators.url(url) or "youtube.com" in url:
            st.error("Please enter a valid and complete website URL.")
        else:
            try:
                with st.spinner("Loading and summarizing webpage..."):
                    loader = UnstructuredURLLoader(
                        urls=[url],
                        ssl_verify=True,
                        headers={
                            "User-Agent": (
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/115.0.0.0 Safari/537.36"
                            )
                        }
                    )
                    docs = loader.load()
                    output_summary = summarize_chain(docs, llm)

                    audio_data, b64 = generate_audio(output_summary)
                    st.audio(audio_data, format="audio/mp3")
                    st.markdown(f'<div style="text-align: right;"><a href="data:audio/mp3;base64,{b64}" download="summary.mp3">Download Audio Summary</a></div>',unsafe_allow_html=True)

                st.write("Summary: \n")
                st.success(output_summary)

                b64 = base64.b64encode(output_summary.encode()).decode()
                st.markdown(f'<div style="text-align: right;"><a href="data:file/txt;base64,{b64}" download="summary.txt">Download Text Summary</a></div>',unsafe_allow_html=True)

            except Exception as e:
                st.exception(f"Exception: {e}")

elif st.session_state.mode == "pdf":
    uploaded_files = st.file_uploader("Upload a PDF file", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        try:
            with st.spinner("Loading and summarizing PDF..."):
                documents = []
                for uploaded_file in uploaded_files:
                    temppdf = f"./temp.pdf"
                    with open(temppdf, "wb") as file:
                        file.write(uploaded_file.getvalue())
                        file_name = uploaded_file.name

                    loader = PyPDFLoader(temppdf)
                    docs = loader.load()
                    documents.extend(docs)
                    os.remove(temppdf)
           
                output_summary = summarize_chain(docs, llm)

                audio_data, b64 = generate_audio(output_summary)
                st.audio(audio_data, format="audio/mp3")
                st.markdown(f'<div style="text-align: right;"><a href="data:audio/mp3;base64,{b64}" download="summary.mp3">Download Audio Summary</a></div>',unsafe_allow_html=True)

                st.write("Summary: \n")
                st.success(output_summary)

                b64 = base64.b64encode(output_summary.encode()).decode()
                st.markdown(f'<div style="text-align: right;"><a href="data:file/txt;base64,{b64}" download="summary.txt">Download Text Summary</a></div>',unsafe_allow_html=True)

        except Exception as e: 
            st.exception(f"Exception: {e}")
