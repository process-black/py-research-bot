"""Generic text processing utilities."""


def chunk_text_at_line_breaks(text: str, max_length: int = 2800) -> list:
    """
    Split text into chunks at line breaks, staying under max_length.
    
    This function intelligently splits text by prioritizing natural break points:
    1. Line breaks (\n)
    2. Word boundaries (spaces)  
    3. Hard split as last resort
    
    Args:
        text: Text to split
        max_length: Maximum length per chunk (default 2800 for safety buffer)
        
    Returns:
        List of text chunks, each under max_length characters
        
    Example:
        >>> text = "Line 1\nLine 2\nVery long line that exceeds the limit..."
        >>> chunks = chunk_text_at_line_breaks(text, max_length=50)
        >>> len(chunks[0]) <= 50  # True
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    remaining_text = text
    
    while remaining_text:
        if len(remaining_text) <= max_length:
            chunks.append(remaining_text)
            break
            
        # Find the last line break before max_length
        chunk = remaining_text[:max_length]
        last_newline = chunk.rfind('\n')
        
        if last_newline > 0:
            # Split at the line break
            chunks.append(remaining_text[:last_newline])
            remaining_text = remaining_text[last_newline + 1:]
        else:
            # No line break found, split at word boundary
            last_space = chunk.rfind(' ')
            if last_space > 0:
                chunks.append(remaining_text[:last_space])
                remaining_text = remaining_text[last_space + 1:]
            else:
                # Last resort: hard split
                chunks.append(remaining_text[:max_length])
                remaining_text = remaining_text[max_length:]
    
    return chunks


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to max_length, adding suffix if truncated.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: String to append when truncated (default "...")
        
    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words
    """
    return len(text.split())


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text by collapsing multiple spaces/newlines.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    import re
    # Replace multiple whitespace with single space
    return re.sub(r'\s+', ' ', text).strip()