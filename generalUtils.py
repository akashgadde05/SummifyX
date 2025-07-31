from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from gtts import gTTS
import base64
import re
import os
import tempfile
from typing import List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_TOKENS = 6000
MIN_CHUNK_SIZE = 500
MAX_CHUNK_SIZE = 2000
CHUNK_OVERLAP = 300

def estimate_tokens(text: str) -> int:
    """
    More accurate token estimation for different types of content
    """
    if not text:
        return 0
    
    # Different estimation ratios for different content types
    # Technical content tends to have more tokens per character
    words = len(text.split())
    chars = len(text)
    
    # Use a more conservative estimate: average of word-based and char-based
    word_based_tokens = words * 1.3  # Average 1.3 tokens per word
    char_based_tokens = chars / 3.5  # Average 3.5 characters per token
    
    return int((word_based_tokens + char_based_tokens) / 2)

def chunk_documents(docs: List, content_type: str = "general") -> List:
    """
    Enhanced document chunking with content-type awareness
    """
    try:
        # Adjust chunk size based on content type
        if content_type == "technical":
            chunk_size = MIN_CHUNK_SIZE
            chunk_overlap = 200
        elif content_type == "narrative":
            chunk_size = MAX_CHUNK_SIZE
            chunk_overlap = CHUNK_OVERLAP
        else:
            chunk_size = 1200
            chunk_overlap = 250
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(docs)
        
        # Filter out very small chunks
        split_docs = [doc for doc in split_docs if len(doc.page_content.strip()) > 50]
        
        logger.info(f"Created {len(split_docs)} chunks from {len(docs)} documents")
        return split_docs
        
    except Exception as e:
        logger.error(f"Error in document chunking: {e}")
        return docs  # Return original docs if chunking fails

def detect_content_type(docs: List) -> str:
    """
    Detect content type to optimize processing
    """
    if not docs:
        return "general"
    
    # Combine all text for analysis
    full_text = " ".join(doc.page_content for doc in docs[:3])  # Sample first few docs
    text_lower = full_text.lower()
    
    # Technical content indicators
    technical_indicators = [
        'algorithm', 'function', 'method', 'class', 'variable', 'data structure',
        'implementation', 'code', 'programming', 'software', 'api', 'database',
        'framework', 'library', 'python', 'javascript', 'java', 'c++', 'sql'
    ]
    
    # Narrative content indicators
    narrative_indicators = [
        'story', 'character', 'plot', 'narrative', 'chapter', 'scene',
        'dialogue', 'protagonist', 'antagonist', 'setting', 'theme'
    ]
    
    technical_score = sum(1 for indicator in technical_indicators if indicator in text_lower)
    narrative_score = sum(1 for indicator in narrative_indicators if indicator in text_lower)
    
    if technical_score > narrative_score and technical_score > 3:
        return "technical"
    elif narrative_score > technical_score and narrative_score > 2:
        return "narrative"
    else:
        return "general"

def create_enhanced_prompts(content_type: str) -> Tuple[PromptTemplate, PromptTemplate]:
    """
    Create content-type specific prompts for better summarization
    """
    if content_type == "technical":
        stuff_template = '''
        Create a comprehensive technical summary of the following content.
        
        Structure your summary as follows:
        1. **Title**: Create a clear, descriptive title
        2. **Overview**: Brief introduction explaining what this content covers
        3. **Key Concepts**: List and explain the main technical concepts, methods, or algorithms
        4. **Important Details**: Highlight critical technical details, specifications, or implementation notes
        5. **Conclusion**: Summarize the main takeaways and practical applications
        
        Focus on technical accuracy and include specific terminology.
        
        Content: {text}
        '''
        
        map_template = '''
        Summarize this technical content section, focusing on:
        - Key technical concepts and methods
        - Important specifications or parameters
        - Critical implementation details
        - Any algorithms or processes described
        
        Content: {text}
        '''
        
        combine_template = '''
        Create a comprehensive technical summary from these section summaries.
        
        Structure as:
        **Title**: [Descriptive technical title]
        **Overview**: [What this covers technically]
        **Key Technical Concepts**: 
        • [List main concepts with brief explanations]
        **Implementation Details**: 
        • [Important technical specifications]
        **Conclusion**: [Main technical takeaways and applications]
        
        Section summaries: {text}
        '''
        
    elif content_type == "narrative":
        stuff_template = '''
        Create an engaging summary of this narrative content.
        
        Structure your summary as follows:
        1. **Title**: Create an engaging title that captures the essence
        2. **Introduction**: Set the context and main theme
        3. **Key Points**: Main events, characters, or story elements in chronological order
        4. **Important Themes**: Central themes, messages, or lessons
        5. **Conclusion**: How it concludes and the overall impact
        
        Maintain the narrative flow and emotional tone.
        
        Content: {text}
        '''
        
        map_template = '''
        Summarize this narrative section, preserving:
        - Key events or developments
        - Important character interactions
        - Significant plot points or themes
        - Emotional tone and context
        
        Content: {text}
        '''
        
        combine_template = '''
        Create a cohesive narrative summary from these section summaries.
        
        Structure as:
        **Title**: [Engaging title]
        **Introduction**: [Context and setting]
        **Story Development**: 
        • [Key events in order]
        **Main Themes**: 
        • [Central themes and messages]
        **Conclusion**: [Resolution and impact]
        
        Section summaries: {text}
        '''
        
    else:  # general content
        stuff_template = '''
        Create a comprehensive and well-structured summary of the following content.
        
        Format your response as:
        1. **Title**: Create a clear, descriptive title
        2. **Introduction**: Brief overview of the main topic and purpose
        3. **Key Points**: 
           • Main ideas and important information organized logically
           • Use bullet points for clarity
        4. **Important Details**: 
           • Significant facts, figures, or examples
           • Any actionable items or recommendations
        5. **Conclusion**: Summarize the main takeaways and significance
        
        Ensure the summary is informative, well-organized, and captures the essential information.
        
        Content: {text}
        '''
        
        map_template = '''
        Create a concise summary of this content section, focusing on:
        - Main ideas and key information
        - Important facts or data points
        - Any conclusions or recommendations
        
        Keep it clear and informative.
        
        Content: {text}
        '''
        
        combine_template = '''
        Create a comprehensive final summary from these section summaries.
        
        Structure as:
        **Title**: [Clear descriptive title]
        **Introduction**: [Overview of the topic]
        **Key Information**: 
        • [Main points organized logically]
        **Important Details**: 
        • [Significant facts and insights]
        **Conclusion**: [Main takeaways and significance]
        
        Section summaries: {text}
        '''
    
    stuff_prompt = PromptTemplate(input_variables=['text'], template=stuff_template)
    map_prompt = PromptTemplate(input_variables=['text'], template=map_template)
    combine_prompt = PromptTemplate(input_variables=['text'], template=combine_template)
    
    return stuff_prompt, map_prompt, combine_prompt

def summarize_chain(docs: List, llm, max_retries: int = 3):
    """
    Enhanced summarization with content-type detection and error handling
    """
    if not docs:
        raise ValueError("No documents provided for summarization")
    
    # Clean documents
    docs = [doc for doc in docs if doc.page_content.strip()]
    if not docs:
        raise ValueError("All documents are empty")
    
    # Detect content type
    content_type = detect_content_type(docs)
    logger.info(f"Detected content type: {content_type}")
    
    # Calculate total tokens
    total_text = " ".join(doc.page_content for doc in docs)
    total_tokens = estimate_tokens(total_text)
    logger.info(f"Estimated tokens: {total_tokens}")
    
    # Get appropriate prompts
    stuff_prompt, map_prompt, combine_prompt = create_enhanced_prompts(content_type)
    
    for attempt in range(max_retries):
        try:
            if total_tokens < MAX_TOKENS:
                logger.info("Using 'stuff' chain for summarization")
                chain = load_summarize_chain(llm, chain_type="stuff", prompt=stuff_prompt)
                result = chain.run(docs)
            else:
                logger.info("Using 'map_reduce' chain for summarization")
                chunked_docs = chunk_documents(docs, content_type)
                chain = load_summarize_chain(
                    llm, 
                    chain_type="map_reduce", 
                    map_prompt=map_prompt, 
                    combine_prompt=combine_prompt
                )
                result = chain.run(chunked_docs)
            
            # Validate result
            if not result or len(result.strip()) < 50:
                raise ValueError("Generated summary is too short")
            
            return result.strip()
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"Failed to generate summary after {max_retries} attempts: {e}")
    
    return "Summary generation failed after multiple attempts."

def clean_text_for_audio(text: str) -> str:
    """
    Enhanced text cleaning for better audio generation
    """
    if not text:
        return ""
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'#{1,6}\s*(.*)', r'\1', text)  # Headers
    text = re.sub(r'`(.*?)`', r'\1', text)        # Code
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text) # Links
    
    # Clean up special characters
    text = re.sub(r'[#*_>`\-•]', '', text)
    text = re.sub(r'^\s*[\d]+\.\s*', '', text, flags=re.MULTILINE)  # Numbered lists
    text = re.sub(r'^\s*[•\-]\s*', '', text, flags=re.MULTILINE)   # Bullet points
    
    # Fix sentence structure
    text = re.sub(r'(?<=[^\.\!\?])\n', '. ', text)  # Add periods
    text = re.sub(r'\n+', ' ', text)                 # Flatten newlines
    text = re.sub(r'\s{2,}', ' ', text)              # Remove extra spaces
    
    # Fix common abbreviations for better pronunciation
    abbreviations = {
        'API': 'A P I',
        'URL': 'U R L',
        'HTML': 'H T M L',
        'CSS': 'C S S',
        'JS': 'JavaScript',
        'AI': 'A I',
        'ML': 'Machine Learning',
        'NLP': 'Natural Language Processing',
        'PDF': 'P D F',
        'CEO': 'C E O',
        'CTO': 'C T O',
        'USA': 'United States',
        'UK': 'United Kingdom'
    }
    
    for abbrev, replacement in abbreviations.items():
        text = re.sub(r'\b' + abbrev + r'\b', replacement, text, flags=re.IGNORECASE)
    
    return text.strip()

def generate_audio(summary_text: str, lang: str = "en", slow: bool = False) -> Tuple[bytes, str]:
    """
    Enhanced audio generation with better error handling and quality
    """
    try:
        if not summary_text or not summary_text.strip():
            raise ValueError("No text provided for audio generation")
        
        # Clean text for better audio
        cleaned_text = clean_text_for_audio(summary_text)
        
        if len(cleaned_text) > 5000:  # gTTS has character limits
            logger.warning("Text is very long, truncating for audio generation")
            cleaned_text = cleaned_text[:4800] + "... Summary continues in text format."
        
        # Generate audio
        logger.info(f"Generating audio for {len(cleaned_text)} characters")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts = gTTS(text=cleaned_text, lang=lang, slow=slow)
            tts.save(temp_file.name)
            
            # Read the generated audio file
            with open(temp_file.name, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temporary file
            os.unlink(temp_file.name)
        
        if not audio_bytes:
            raise ValueError("Failed to generate audio data")
        
        # Encode to base64
        b64 = base64.b64encode(audio_bytes).decode()
        
        logger.info(f"Successfully generated audio: {len(audio_bytes)} bytes")
        return audio_bytes, b64
        
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        # Create a fallback minimal audio or return None
        try:
            # Try with a shorter text as fallback
            fallback_text = "Audio generation encountered an error. Please download the text summary."
            tts = gTTS(text=fallback_text, lang=lang)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                tts.save(temp_file.name)
                with open(temp_file.name, 'rb') as f:
                    audio_bytes = f.read()
                os.unlink(temp_file.name)
                
            b64 = base64.b64encode(audio_bytes).decode()
            return audio_bytes, b64
            
        except:
            # If all else fails, raise the original error
            raise RuntimeError(f"Audio generation failed: {e}")

def validate_summary_quality(summary: str) -> Tuple[bool, str]:
    """
    Validate the quality of generated summary
    """
    if not summary or not isinstance(summary, str):
        return False, "Summary is empty or invalid"
    
    summary = summary.strip()
    
    if len(summary) < 100:
        return False, "Summary is too short"
    
    if len(summary) > 10000:
        return False, "Summary is too long"
    
    # Check for proper structure
    if not any(marker in summary.lower() for marker in ['title', 'introduction', 'conclusion', 'key', 'main']):
        return False, "Summary lacks proper structure"
    
    # Check for meaningful content
    word_count = len(summary.split())
    if word_count < 50:
        return False, "Summary has too few words"
    
    return True, "Summary quality is acceptable"
