# backend/app/utils.py
import re
from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    """
    Normalize URL by adding protocol and cleaning up format
    
    Rules:
    - Accept //img.xx/.. → auto prepend https:
    - Accept img.xx/... without protocol → auto prepend https://
    - Remove extra whitespace and escape chars
    - Return clean URL
    """
    if not url or not isinstance(url, str):
        return ""
    
    # Clean whitespace and escape characters
    url = url.strip()
    url = url.replace('\n', '').replace('\r', '').replace('\t', '')
    
    if not url:
        return ""
    
    # Handle protocol-relative URLs (//domain.com/path)
    if url.startswith('//'):
        url = 'https:' + url
    
    # Handle URLs without protocol
    elif not url.startswith(('http://', 'https://')):
        # Check if it looks like a domain
        if '.' in url and not url.startswith('/'):
            url = 'https://' + url
        else:
            # Relative path, can't normalize properly
            return url
    
    try:
        # Parse and reconstruct URL to ensure it's well-formed
        parsed = urlparse(url)
        
        # Ensure we have a valid scheme
        if not parsed.scheme:
            parsed = parsed._replace(scheme='https')
        
        # Reconstruct the URL
        normalized = urlunparse(parsed)
        return normalized
        
    except Exception:
        # If parsing fails, return original cleaned URL
        return url

def is_valid_youtube_id(video_id: str) -> bool:
    """Check if string is a valid YouTube video ID"""
    if not video_id or len(video_id) != 11:
        return False
    
    # YouTube video IDs are 11 characters, alphanumeric plus - and _
    pattern = r'^[a-zA-Z0-9_-]{11}$'
    return bool(re.match(pattern, video_id))

def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats"""
    if not url:
        return ""
    
    # Already just an ID
    if is_valid_youtube_id(url):
        return url
    
    # Common YouTube URL patterns
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return ""