"""
Page format and support tools. 

Source: https://github.com/standardebooks/tools/blob/master/se/formatting.py
"""

import regex

def get_word_count(xhtml: str) -> int:
    """
    Get the word count from an XHTML string.
    
    Parameters
    ----------
    xhtml: str
        A string of XHTML
        
    Returns
    -------
    int: The number of words in the XHTML string.
    """
    # Remove MathML
    xhtml = regex.sub(r"<(m:)?math.+?</(m:)?math>", " ", xhtml)
    # Remove HTML tags
    xhtml = regex.sub(r"<title>.+?</title>", " ", xhtml)
    xhtml = regex.sub(r"<.+?>", " ", xhtml, flags=regex.DOTALL)
    # Replace some formatting characters
    xhtml = regex.sub(r"[…–—― ‘’“”\{\}\(\)]", " ", xhtml, flags=regex.IGNORECASE | regex.DOTALL)
    # Remove word-connecting dashes, apostrophes, commas, and slashes (and/or), they count as a word boundry but they shouldn't
    xhtml = regex.sub(r"[\p{Letter}0-9][\-\'\,\.\/][\p{Letter}0-9]", "aa", xhtml, flags=regex.IGNORECASE | regex.DOTALL)
    # Replace sequential spaces with one space
    xhtml = regex.sub(r"\s+", " ", xhtml, flags=regex.IGNORECASE | regex.DOTALL)
    # Get the word count
    return len(regex.findall(r"\b\w+\b", xhtml, flags=regex.IGNORECASE | regex.DOTALL))