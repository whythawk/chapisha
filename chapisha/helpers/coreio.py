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
from typing import Optional, Union, Any
import locale
try:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except locale.Error:
    # Readthedocs has a problem, but difficult to replicate
    locale.setlocale(locale.LC_ALL, "")

# https://github.com/python/typing/issues/182
JSONType = Union[str, int, float, bool, None, dict[str, Any], list[Any]]

###################################################################################################
### Path management
###################################################################################################

DEFAULT_BASE64_TYPES = {
    "cover": "^data:image\/(png|jpe?g);base64,",
    "work": "data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,"
}
DEFAULT_METADATA_SETTINGS = "work_metadata.json"
DEFAULT_DATA_DIRECTORY = Path(__file__).resolve().parent / "data"

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

def save_json(data: dict, source: Path, overwrite: Optional[bool]=False) -> bool:
    """
    Save a dictionary as a json file. Return `False` if file `source` already exists and not
    `overwrite`.

    Parameters
    ----------
    data: dict
        Dictionary to be saved
    source: Path
        Path to filename to open
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