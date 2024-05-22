"""
Page format and support tools.
"""

from PIL import ImageDraw, ImageFont, Image
import re
from . import coreio as _c

DIRECTORY = _c.get_helper_path() / "data" / "fonts"
TITLEPAGE_FONT = "PT-Serif.ttf"
TITLEPAGE_HEIGHT = 700
TITLEPAGE_WIDTH = 1000  # Relatively generous margin
TITLE_SIZE = 70  # Approx 90px / 1.333 conversion factor
AUTHOR_SIZE = 58  # Approx 75px / 1.333 conversion factor


def get_text_rows(text: str, font_size: int = TITLE_SIZE) -> list[str]:
    """
    Return a given text as rows of text which fit the title page plate width for a given font size (in pts).

    Parameters
    ----------
    text: str
        The text string for splitting into rows
    font_size: int
        Font size in pts. Defaults to TITLE_SIZE.

    Returns
    -------
    list of str
    """
    rows = 1
    word_list = text.split(" ")
    font = ImageFont.truetype(str(DIRECTORY / TITLEPAGE_FONT), font_size)
    fits_titlepage_width = False
    while not fits_titlepage_width:
        # Create individual text rows
        fitted_rows = len(word_list) // rows
        start, end = 0, fitted_rows
        text_rows = []
        while end < rows * fitted_rows:
            # get the size of the text
            text_rows.append(" ".join(word_list[start:end]))
            start += fitted_rows
            end += fitted_rows
        if word_list[start:]:
            text_rows.append(" ".join(word_list[start:]))
        # Check title rows fit
        max_width = 0
        for phrase in text_rows:
            word_image = Image.new("RGBA", (0, 0), (255, 255, 255, 0))
            draw = ImageDraw.Draw(word_image)
            word_width = draw.textlength(phrase, font=font)
            if word_width > max_width:
                max_width = word_width
        if max_width > TITLEPAGE_WIDTH:
            # Increment the number of rows and start again
            rows += 1
            continue
        # It worked
        fits_titlepage_width = True
    return text_rows


def get_text_paragraphs(text: str) -> list[str]:
    """
    Return a given text as a list of paragraphs.

    Parameters
    ----------
    text: str
        The text string for splitting into paragraphs

    Returns
    -------
    list of str
    """
    # https://stackoverflow.com/a/64863601/295606
    if text:
        if isinstance(text, list):
            text = "\n".join(text)
        NEWLINES_RE = re.compile(r"\n{1,}")
        text = text.strip("\n")  # remove leading and trailing "\n"
        return [p.strip() for p in NEWLINES_RE.split(text) if p.strip()]
    return []
