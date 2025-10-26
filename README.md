# 🎯 SummifyX - Enhanced AI Content Summarizer

![SummifyX Logo](summify_logo.jpg)

SummifyX is a powerful, AI-driven content summarization application built with Streamlit. It intelligently processes and summarizes content from YouTube videos, web articles, and PDF documents, providing both text and audio outputs with downloadable formats.

## ✨ New Features & Enhancements

### 🎨 **Enhanced UI/UX**
- **Modern Design**: Beautiful gradient-based interface with hover effects
- **Card-based Layout**: Intuitive content type selection with visual cards
- **Progress Indicators**: Real-time progress bars for all operations
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Interactive Elements**: Smooth animations and transitions

### 🛠️ **Improved Functionality**
- **Smart Content Detection**: Automatically detects content type (technical, narrative, general)
- **Enhanced Error Handling**: Comprehensive error messages with helpful suggestions
- **Multiple Fallback Methods**: YouTube transcript fetching with 4 different fallback strategies
- **Better Text Processing**: Improved cleaning and formatting for better summaries
- **Audio Quality**: Enhanced text-to-speech with better pronunciation handling

### 🔧 **Technical Improvements**
- **Robust URL Parsing**: Enhanced YouTube URL validation supporting all formats
- **Token Management**: Intelligent chunking based on content type
- **Content-Aware Prompts**: Different summarization strategies for different content types
- **Better SSL Handling**: Improved web scraping with flexible SSL verification
- **Memory Management**: Proper cleanup of temporary files

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🎥 **YouTube Summarization** | Extract and summarize video transcripts with multiple fallback methods |
| 🌐 **Web Article Processing** | Intelligent web scraping with content extraction |
| 📄 **PDF Document Analysis** | Multi-file PDF processing with text extraction |
| 🎧 **Audio Generation** | High-quality text-to-speech with pronunciation optimization |
| 📱 **Responsive UI** | Modern, mobile-friendly interface |
| 📥 **Download Options** | Both text and audio formats available |
| 🧠 **AI-Powered** | Content-aware summarization using advanced LLM |
| 🔄 **Smart Chunking** | Automatic content-type detection and processing |

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit with custom CSS
- **AI/ML**: LangChain + Groq (Gemma2-9b-it)
- **Text-to-Speech**: Google Text-to-Speech (gTTS)
- **Document Processing**: PyPDF, Unstructured
- **Web Scraping**: Requests, BeautifulSoup
- **YouTube**: YouTube Transcript API with proxy support

---

## ⚡ Quick Start

### 1. **Clone the Repository**
```bash
git clone https://github.com/your-username/SummifyX-Enhanced.git
cd SummifyX-Enhanced
```

### 2. **Set Up Virtual Environment** (Recommended)
```bash
# Create virtual environment
python -m venv summifyx_env

# Activate it
# On Windows:
summifyx_env\Scripts\activate
# On macOS/Linux:
source summifyx_env/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Configure API Keys**

Create a `.streamlit/secrets.toml` file:
```toml
LANGCHAIN_API_KEY = "your_langchain_api_key_here"
GROQ_API_KEY = "your_groq_api_key_here"

# Optional: For YouTube proxy (if needed)
proxy_username = "your_proxy_username"
proxy_password = "your_proxy_password"
```

**Where to get API keys:**
- **Groq API**: Sign up at [console.groq.com](https://console.groq.com)
- **LangChain API**: Get it from [smith.langchain.com](https://smith.langchain.com)

### 5. **Run the Application**
```bash
streamlit run APP.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📖 Usage Guide

### 🎥 YouTube Video Summarization
1. Click "Summarize YouTube Video"
2. Paste any YouTube URL format:
   - `https://www.youtube.com/watch?v=VIDEO_ID`
   - `https://youtu.be/VIDEO_ID`
   - `https://youtube.com/embed/VIDEO_ID`
3. Click "Generate Summary"
4. Get structured summary with audio

### 🌐 Website Article Summarization
1. Select "Summarize Website"
2. Enter the article URL
3. The system will extract and process the content
4. Download text and audio summaries

### 📄 PDF Document Processing
1. Choose "Summarize PDF"
2. Upload single or multiple PDF files
3. System processes all files together
4. Get comprehensive summary with audio

---

## 🔧 Configuration Options

### Content Types
The system automatically detects and optimizes for:
- **Technical Content**: Programming, documentation, research papers
- **Narrative Content**: Stories, articles, blogs
- **General Content**: Mixed or standard informational content

### Audio Settings
- **Language**: Default English (`en`)
- **Speed**: Normal speed (can be adjusted in code)
- **Format**: MP3 with optimized compression

### Processing Limits
- **Max Tokens**: 6,000 tokens per processing session
- **PDF Size**: No strict limit, but larger files take longer
- **Audio Length**: Automatically truncated if text > 5,000 characters

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 🎥 YouTube Issues

**Problem**: "No transcript available"
**Solutions**:
- Ensure the video has captions/subtitles enabled
- Try a different video with manual captions
- Check if the video is public and not region-restricted

**Problem**: "Video unavailable"
**Solutions**:
- Verify the video URL is correct and complete
- Ensure the video is public
- Try copying the URL directly from YouTube

#### 🌐 Website Issues

**Problem**: "SSL Certificate error"
**Solutions**:
- The website has security restrictions
- Try a different article from the same site
- Some corporate/academic sites block automated access

**Problem**: "Access denied"
**Solutions**:
- Website is blocking automated requests
- Try articles from news sites or blogs
- Avoid sites with aggressive bot protection

#### 📄 PDF Issues

**Problem**: "Could not extract text"
**Solutions**:
- Ensure PDF contains selectable text (not scanned images)
- Check if PDF is password-protected
- Try with a smaller PDF file first

#### 🎧 Audio Issues

**Problem**: "Audio generation failed"
**Solutions**:
- Check internet connection for gTTS
- Text might be too long (auto-truncated)
- Try generating summary again

#### 🔑 API Issues

**Problem**: "API keys not found"
**Solutions**:
- Verify `secrets.toml` file exists in `.streamlit/` folder
- Check API key format and validity
- Ensure no extra spaces or quotes in keys

**Problem**: "Rate limiting"
**Solutions**:
- Wait 5-10 minutes before retrying
- Groq has generous free limits, but they exist
- Consider upgrading API plan for heavy usage

---

## 🔒 Security & Privacy

- **No Data Storage**: Summaries are not stored permanently
- **Temporary Files**: Automatically cleaned up after processing
- **API Keys**: Stored securely in Streamlit secrets
- **Privacy**: No personal data collection or tracking

---

## 🚀 Deployment

### Local Development
```bash
streamlit run APP.py
```

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to [share.streamlit.io](https://share.streamlit.io)
3. Add secrets in Streamlit Cloud dashboard
4. Deploy automatically

### Docker (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "APP.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 📊 Performance Tips

### For Better Speed
- Use shorter content when possible
- PDF processing is fastest, YouTube can be slower
- Multiple PDFs are processed efficiently together

### For Better Summaries
- Ensure source content is well-structured
- Technical content gets specialized processing
- Longer content gets map-reduce processing for better results

### For Reliable YouTube Processing
- Use videos with manual captions when possible
- Educational and news content typically works best
- Avoid very long videos (>2 hours) for faster processing

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit changes**: `git commit -m 'Add AmazingFeature'`
4. **Push to branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain** for the powerful LLM framework
- **Groq** for fast inference with Gemma models
- **Streamlit** for the excellent web framework
- **Google** for the Text-to-Speech service
- **YouTube Transcript API** for transcript access

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/SummifyX-Enhanced/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/SummifyX-Enhanced/discussions)
- **Email**: akashgadde05@gmail.com

---

## 🔄 Changelog

### v2.0.0 (Current)
- ✨ Complete UI redesign with modern interface
- 🛠️ Enhanced error handling and user feedback
- 🎥 Improved YouTube processing with multiple fallbacks
- 🧠 Content-type aware summarization
- 🎧 Better audio generation and cleanup
- 📱 Mobile-responsive design
- 🔧 Better configuration management

### v1.0.0
- 🎉 Initial release
- 🎥 YouTube summarization
- 🌐 Web article processing
- 📄 PDF document support
- 🎧 Basic audio generation

---

**Made with ❤️ by [AKASH GADDE](https://github.com/akashgadde05)**

*Star ⭐ this repository if you found it helpful!*
