"""
Miscellaneous tools for supporting core functionality.
"""
import json
import sys, re
import copy
import hashlib
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path, PurePath
from typing import Optional, Union, List, Dict, Any
import locale
try:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except locale.Error:
    # Readthedocs has a problem, but difficult to replicate
    locale.setlocale(locale.LC_ALL, "")

# https://github.com/python/typing/issues/182
JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]

###################################################################################################
### Path management
###################################################################################################

DEFAULT_PROJECT_SETTINGS = "chapisha_settings.json"
DEFAULT_STYLES_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_FONT_DIRECTORY = DEFAULT_STYLES_DIRECTORY / "fonts"
DEFAULT_STYLE_SHEET = DEFAULT_STYLES_DIRECTORY / "css" / "stylesheet.css"
DEFAULT_METADATA_SCHEMA = str(DEFAULT_STYLES_DIRECTORY / "json" / "dublin_core.json")

def get_helper_path():
    """
    Get the Chapisha helper path. Used, usually, when needing template resources in the helpers folder.
    """
    return Path(__file__).resolve().parent

def check_path(directory: str):
    """
    Check whether the path at a given directory exists. If not, create it.

    Parameters
    ----------
    directory: str
        Complete directory address as a string.
    """
    Path(directory).mkdir(parents=True, exist_ok=True)

def check_source(source: str) -> bool:
    """
    Check whether a source file exists.

    Parameters
    ----------
    source: str
        Complete directory and file address as a string.

    Returns
    -------
    bool
    """
    if Path(source).exists():
        return True
    else:
        e = F"Source at `{source}` not found."
        raise FileNotFoundError(e)

def check_uri(source: str) -> bool:
    """
    Check whether a given source URI exists.

    Parameters
    ----------
    source: str
        Source URI.

    Returns
    -------
    bool
    """
    # https://stackoverflow.com/a/38020041
    try:
        result = urlparse(source)
        return all([result.scheme, result.netloc])
    except:
        return False

###################################################################################################
### JSON, Schema and Action get and set
###################################################################################################

def load_json(source: str) -> dict:
    """
    Load and return a JSON file, if it exists.

    Paramaters
    ----------
    source: str
        Filename to open, including path

    Raises
    ------
    JSONDecoderError if not a valid json file
    FileNotFoundError if not a valid source

    Returns
    -------
    dict
    """
    check_source(source)
    with open(source, "r") as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError:
            e = F"File at `{source}` not valid json."
            raise json.decoder.JSONDecodeError(e)

def save_json(data: dict, source: str, overwrite: Optional[bool]=False) -> bool:
    """
    Save a dictionary as a json file. Return `False` if file `source` already exists and not
    `overwrite`.

    Parameters
    ----------
    data: dict
        Dictionary to be saved
    source: str
        Filename to open, including path
    overwrite: bool
        True to overwrite existing file

    Returns
    -------
    bool
        True if saved, False if already exists without `overwrite`
    """
    if Path(source).exists() and not overwrite:
        e = F"`{source}` already exists. Set `overwrite` to `True`."
        raise FileExistsError(e)
    with open(source, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True, default=str)
    return True

def get_metadata_schema(source: str = DEFAULT_METADATA_SCHEMA) -> dict:
    """
    Return the standard Dublin Core schema permitted for the EPUB3 standard.
    """
    return load_json(source)

def get_metadata_settings(source: str = DEFAULT_METADATA_SCHEMA) -> dict:
    """
    Produce a dictionary of Dublin Core metadata terms defined in `source`. Return as::

        {
            "term": bool,
        }

    Where `True` means must be unique (one value) and `False` is non-unique (may be repeated).

    Parameters
    ----------
    source: str
        Filename to open, including path

    Returns
    -------
    dict
    """
    metadata = {}
    schema = load_json(source)
    for term in schema["fields"]:
        metadata.update({term["name"]: term["unique"]})
    return metadata

def get_work_settings(directory: Optional[str] = None) -> dict:
    """
    Return a dictionary of current settings for the creative work project resources. If it does not exist, return 
    default settings and structure.

    Parameters
    ----------
    directory: str
        Directory path to open

    Returns
    -------
    dict
    """
    try:
        check_source(directory + DEFAULT_PROJECT_SETTINGS)
        return load_json(directory + DEFAULT_PROJECT_SETTINGS)
    except FileNotFoundError:
        return {
            "work_link": None,
            "metadata": {
                "terms": [],
                "title": None,
                "description": None,
                "creator": [],
                "validated": False
            },
            "files": {
                "docx": None,
                "cover": None,
                "rights": None,
                "dedication": None
            },
            "rights": {
                "work": None,
                "cover": None,
                "terms": [],
                "file": None
            },
            "pages": {
                "cover": None,
                "dedication": []
            }
        }

###################################################################################################
### XHTML and Text Templates
###################################################################################################

XHTML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <meta charset="utf-8" />
    <meta name="Generator" content="Chapisha"/>
    <title></title>
    <link href="css/stylesheet.css" rel="stylesheet" type="text/css"/>
</head>
<body epub:type="bodymatter">
<section id="section" class="epigrams"></section>
<div class="pagebreak"></div>
</body>
</html>"""

def get_rights_template_list(
            creator: [str, list[str]], 
            year: Optional[str] = None, 
            work_uri: Optional[str] = None,
            publisher: Optional[str] = None,
            publisher_uri: Optional[str] = None,
            cover_rights: Optional[str] = None,
            rights: bool = True) -> list[str, list[str]]:
    """
    Create the minimal list of terms to present on the rights page of a creative work. 

    Parameters
    ----------
    creator: str or list of str
        Full name/s of creators to be credited as rights holders.
    year: str
        Publication year
    work_uri: str
        URI to the creator/s' website
    publisher: str
        Publisher for the work (Optional)
    publisher_uri: str
        URI to the publisher's website (Optional)
    cover_rights: str
        Text for publication rights for cover image (Optional)
    rights: bool
        True for copyright, False for Attribution-NonCommercial-ShareAlike

    Returns
    -------
    list of str
    """
    if not year:
        year = datetime.now().year
    pn_author = "author"
    pn_this = "This author"
    pn_support = "supports"
    if isinstance(creator, list):
        if len(creator) > 1:
            creator = " &amp; ".join([", ".join(creator[:-1]), creator[-1]])
            pn_author = "authors"
            pn_this = "These authors"
            pn_support = "support"
        else:
            creator = creator[0]
    # Create list of terms for template
    template = []
    if publisher: template.append(publisher)
    if check_uri(publisher_uri):
        template.append(publisher_uri)
    if "qwyre" not in publisher.lower():
        template.append("This EPUB created with Chapisha.")
    template.append(["images/logo.png", "Qwyre Publishing Logo"])
    template.append(F"First published in {year}")
    if rights:
        template.append(F"Copyright {creator}, {year}")
        if cover_rights:
            template.append(cover_rights)
        template.append("PT Sans and PT Serif fonts are SIL Open Font License.")
        template.append(F"The right of {creator} to be identified as the {pn_author.title()} of the Work has been asserted by them in accordance with the Copyright, Designs and Patents Act 1988. {pn_this} {pn_support} copyright. Copyright gives creators space to explore and provides for their long-term ability to sustain themselves from their work. Thank you for buying this work and for complying with copyright laws by not reproducing, scanning, or distributing any part of it without permission. Your support will contribute to future works by {pn_this.lower()}.")
    else:
        template.append(F"Copyright {creator}, {year}. Licenced under Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).")
        if cover_rights:
            template.append(cover_rights)
        template.append("PT Sans and PT Serif fonts are SIL Open Font License.")
        template.extend([
                F"You are free to copy and redistribute the Work in any medium or format, and remix, transform, and build upon the Work. The {pn_author.title()} cannot revoke these freedoms as long as you follow the license terms.",
                F"In return: You may not use the material for commercial purposes. You must give appropriate credit, provide a link to this license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the {pn_author.title()} endorses you or your use. If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original. You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits."
            ]
        )
    template.extend(
        ["This is a work of fiction and, except in the case of historical fact, any resemblance to actual persons, living or dead, is purely coincidental.",
        "Every effort has been made to obtain the necessary permissions with reference to copyright material, both illustrative and quoted. We apologise for any omissions in this respect and will be pleased to make appropriate acknowledgements in any future edition."]
    )
    if check_uri(work_uri):
        template.append(work_uri)
    return template