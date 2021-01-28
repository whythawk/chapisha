"""
.. module:: create
:synopsis: Import a Word `docx` document, define its metadata, cover and rights, and publish it as an EPUB3.

.. moduleauthor:: Gavin Chait <github.com/turukawa>

CreateWork
==========

Publish a standards compliant EPUB3 creative work from a source Microsoft Word `docx` document, and define its 
metadata, cover and publishing rights. 

.. note:: This process will overwrite any existing EPUB3 file of the same name, if it already exists.

Workflow
--------

The publication process runs as follows:

* Set the working directory on creation,
* Define and validate the metadata required for the creative work,
* Copy the `docx` file to import into the working directory,
* Copy the cover image to import into the working directory,
* Define the creative work's publication rights,
* Add in an optional dedication,
* Build the creative work,
* Validate the work is EPUB3 standards compliant.

The objective of the workflow is to support what may be a stateless process i.e. the individual steps first bring all
the data required to produce the creative work into a project directory, and then produces it. State does not need
to be maintained between steps.

Build your work
---------------

Import **Chapisha** and create a work:

.. code-block:: python

    from chapisha.create import CreateWork

    work = CreateWork(directory)

Where `directory` is the complete path to where you would like the EPUB created.

Set metadata
^^^^^^^^^^^^

`Dublin Core <https://www.dublincore.org/specifications/dublin-core/dces/>`_ is a vocabulary of fifteen properties for 
use in resource description. Three of them - `title`, `identifier` and `language` - are required. The `language` code
is defined by the `ISO 679-1 <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_ standard (e.g. `en` for English,
or `fr` for French).

The official properties:

* `identifier`: UUID, DOI or ISBN of the creative work. A UUID be generated if not included.
* `title`: Name given to the creative work.
* `language`: Specify the language of the creative work. Two letter code defined by ISO 639-1.
* `creator`: Name of a person, organisation, etc. responsible for the creation of the work. May be more than one.
* `contributor`: Name of a person, organisation, etc. that played a secondary role - such as an editor - in the creation of the work. May be more than one.
* `date`: The publication date of the creative work. Provide in ISO format, YYYY-MM-DD.
* `subject`: The subject, or tag, of the creative work. May be more than one.
* `publisher`: Name of a person, organisation, etc.  responsible for making the creative work available.
* `rights`: Information about copyright held in and over the creative work. Formatted as you wish it to appear.

In addition, you can provide a small number of properties to be included on the rights plate:

* `description`: The pitch, or jacket-cover, description of the creative work.
* `work_uri`: The URI for your creative work.
* `publisher_uri`: The URI for the publisher of your creative work.

Create a paired list of these properties, along with the value of each. As example:

.. code-block:: python

    [["term", "value"], ["term", "value"], ["term", "value"]]

e.g.:

.. code-block:: python

    [["title": "Our Memory Like Dust"], ["creator": "Gavin Chait"], ["identifier": "isbn:9780993191459"], ["date", "2017-07-28]]

Set the metadata:

.. code-block:: python

    work.set_metadata(metadata)

Set document
^^^^^^^^^^^^

Most writers still use `Microsoft Word <https://www.microsoft.com/en-us/microsoft-365/word>`_ as their default work tool.
There are certainly other word processors, but this is the one most people will work with if they intend to be 
professionally published as publishers still expect Word `docx` files for editing and markup.

**Chapisha** will create your cover, rights and dedication pages, as well as the table of contents. Your `docx` file 
must contain **only** the creative content you wish included in that table of contents. Your document must also be 
correctly marked up to ensure proper chapter creation. 

EPUB documents will be read on multiple and diverse electronic devices. Don't have any expectations for page 
number-dependant formatting. Instead:

* Each chapter must have a title, formatted as `Heading 1`, with lower-level headings formatted for each heading type.
* There must be no title page, contents, or anything else. Chapter 1 starts at the top of the first line of the document.
* Page numbers and other page-specific information will be lost.
* Fonts or typographic formats and alignment will be lost, although `bold` and `italics` will be maintained.
* Images will be maintained.

Once the work is built you can enhance its styling. However, there are still limits in the EPUB3 standard in comparison
to a printed work.

.. code-block:: python

    work.set_document(source)

Where `source` is the complete path to the source `docx` file.

Set cover
^^^^^^^^^

There is, unfortunately, no standardisation on the image size, dimensions or resolution required for an EPUB. However,
a recommendation is an image (`.jpeg`, `.jpg` or `.png`) of 1,600 by 2,400 pixels, and less than 5Mb is size. You will
need to create your image (or have someone create it for you) exactly as you wish it to appear on the cover. Nothing
will be added, removed, or changed.

Please also ensure you have the appropriate rights to use the image on your cover. There are more than sufficient 
services providing openly-licenced, or even public domain, work for you to use. 

Include the exact phrasing of the rights information as you set the cover.

.. code-block:: python

    work.set_cover(source, rights="Cover image copyright .....")

Where `source` is the complete path to the image file.

Set rights
^^^^^^^^^^

There are obviously a broad range of rights with which you can release your creative work. For the moment, **Chapisha**
supports only two of these:

* Commercial copyright with all rights reserved.
* Commercial copyright but licenced for distribution under Attribution-NonCommercial-ShareAlike 4.0 International (`CC BY-NC-SA 4.0 <https://creativecommons.org/licenses/by-nc-sa/4.0/>`_).

.. code-block:: python

    work.set_rights(rights=False)

Where `True` is all rights reserved, and `False` is CC BY-NC-SA 4.0.

Set dedication
^^^^^^^^^^^^^^

Most creators have a dedication for their work in mind - usually to apologise for all the late nights and impoverishing
returns on their creative efforts.

This is optional, but you can include a dedication page.

.. code-block:: python

    dedication = [
        "For those who leave.",
        "For those who remain.",
        "For the wings and tail.",
        "But most, for her"
    ]
    work.set_dedication(dedication)

The dedication can be one line of text, or several. If several, each line must be provided as a separate term in a `list`.

Build
^^^^^

The build function is straightforward. Once everything is in place:

.. code-block:: python

    work.build()

You will find your EPUB in the directory you specified.

Validate
^^^^^^^^

If you have any doubts as to whether your EPUB is standards compliant, run the validation. This tests the `epub` file
against the standards maintained by the `DAISY Consortium <http://validator.idpf.org/>`_. You can check the file online
at that link. It's the same test.

.. code-block:: python

    work.validate()

Output will be `True` or `False`.
"""

import pypandoc
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from epubcheck import EpubCheck
from typing import Optional
from urllib.parse import urlparse
from pathlib import Path
import os

from chapisha.helpers import common as _c

class CreateWork:
    """
    Publish a standards compliant EPUB3 creative work from a source Microsoft Word `docx` document, and
    define its metadata, cover and publishing rights.

    If the EPUB file already exists, then publishing this work will overwrite it.

    On instantiation, checks `directory` to see if `chapisha_settings.json` is present, loading the required data,
    or replacing with specified defaults.
    """

    def __init__(self, directory: Optional[str] = None):
        self.directory = directory
        if self.directory[-1] != "/": self.directory + "/"
        _c.check_path(self.directory)
        # Load settings file, if it exists
        self.s = _c.get_work_settings(self.directory)
        self.work = None
        # Defaults
        self.default_fonts_directory = str(_c.DEFAULT_FONT_DIRECTORY)
        self.default_styles = str(_c.DEFAULT_STYLE_SHEET)

    ############################################################################
    # GATHER WORKING DATA
    ############################################################################

    def get_metadata_schema(self):
        """
        Return the standard Dublin Core schema permitted for the EPUB3 standard.
        """
        return _c.get_metadata_schema()

    def set_metadata(self, metadata: Optional[list[list[str]]] = None) -> bool:
        """
        Validate metadata values for the permitted Dublin Core schema terms. Provide the terms as a list of the form:

        .. code-block:: python

            [["term", "value"], ["term", "value"], ["term", "value"]]

        e.g.:

        .. code-block:: python

            [["title": "Our Memory Like Dust"], ["creator": "Gavin Chait"], ["identifier": "isbn:9780993191459"]]

        Alternative, special-case, metadata that can be included in addition to Dublin Core, are:

        * `description`: The pitch, or jacket-cover, description of the creative work
        * `work_uri`: The URI for your creative work
        * `publisher_uri`: The URI for the publisher of your creative work

        .. note:: The terms `identifier`, `title` and `language` are required. Language can be guessed from the Docx, and a random UUID will be assigned if none is provided. A missing title will trigger an exception.

        Parameters
        ----------
        metadata: list of list of str
            List of term, value pairs.

        Raises
        ------
        KeyError: if missing title

        Returns
        -------
        bool
        """
        if not metadata and self.s["metadata"]["validated"]:
            return True
        metadata_settings = _c.get_metadata_settings()
        uniques = []
        for k, v in metadata:
            if k in metadata_settings:
                if metadata_settings[k] and k in uniques:
                    # Must be unique
                    e = F"Duplicated metadata term for `{k}`. Must be unique."
                    raise KeyError(e)
                uniques.append(k)
            elif k in ["description", "work_uri", "publisher_uri"]:
                # Terms used elsewhere
                self.s["metadata"].update({k: v})
            else:
                e = F"Unknown metadata term `{k}`. `get_metadata_schema()` for permitted terms."
                raise KeyError(e)
            if k in ["title", "date", "publisher", "language"]: 
                self.s["metadata"].update({k: v})
            if k == "creator": 
                self.s["metadata"]["creator"].append(v)
        if not self.s["metadata"]["title"]:
            e = "No `title` provided in metadata."
            raise KeyError(e)
        self.s["work_link"] = "-".join(["".join([e for e in w if e.isalnum()]) 
                                for w in self.s["metadata"]["title"].lower().split(" ")])
        self.s["metadata"]["terms"] = metadata
        self.s["metadata"].update({"validated": True})
        # Set the working director to `work_link`, if it isn't already, and save settings there
        self.directory = F"{self.directory}{self.s['work_link']}/"
        _c.check_path(self.directory)
        _c.save_json(self.s, self.directory + _c.DEFAULT_PROJECT_SETTINGS, overwrite=True)
        return True

    def _get_validated_bytes(self, source: str) -> bytes:
        """
        Validate a source file, and return a bytes version.

        Parameters
        ----------
        source: str
            Filename to open, including path

        Raises
        ------
        PermissionError: if metadata not yet validated.
        FileNotFoundError: if the source is not valid.

        Returns
        -------
        bytes
        """
        if not self.s["metadata"]["validated"]:
            e = "`set_metadata` before setting source document."
            raise PermissionError(e)
        if isinstance(source, str):
            try:
                _c.check_source(source)
                with open(source, "rb") as f:
                    source = f.read()
            except FileNotFoundError:
                e = F"`{source}` is not a valid file source."
                raise FileNotFoundError(e)
        if not isinstance(source, bytes):
            e = F"File is not valid."
            raise FileNotFoundError(e)
        return source

    def set_document(self, source: str):
        """
        Import source `docx` document and save to the working directory..

        Parameters
        ----------
        source: str or bytes
            Filename to open, including path

        Raises
        ------
        PermissionError: if metadata not yet validated.
        FileNotFoundError: if the source is not valid.
        """
        source = self._get_validated_bytes(source)
        with open(self.directory + F"{self.s['work_link']}.docx", "wb") as w:
            w.write(source)
        self.s["files"].update({"docx": F"{self.s['work_link']}.docx"})
        _c.save_json(self.s, self.directory + _c.DEFAULT_PROJECT_SETTINGS, overwrite=True)

    def set_cover(self, 
                source: str,
                rights: Optional[str] = None):
        """
        Import cover image and save to the working directory, along with any rights information.

        Parameters
        ----------
        source: str or bytes
            Filename to open, including path, or bytes for file
        filetype: str
            Image filetype, e.g. `jpg` or `png`
        rights: str
            Optional, text indicating attribution and rights for cover image.

        Raises
        ------
        PermissionError: if metadata not yet validated.
        FileNotFoundError: if the source is not valid.
        """
        if not self.s["metadata"]["validated"]:
            e = "`set_metadata` before setting cover."
            raise PermissionError(e)
        filetype = source.split(".")[-1]
        source = self._get_validated_bytes(source)
        with open(self.directory + F"cover.{filetype}", "wb") as w:
            w.write(source)
        self.s["files"].update({"cover": F"cover.{filetype}"})
        if rights: self.s["rights"].update({"cover": rights})
        _c.save_json(self.s, self.directory + _c.DEFAULT_PROJECT_SETTINGS, overwrite=True)

    def set_rights(self, rights: bool = True):
        """
        Set copyright page for creative work. Default rights are all rights reserved (copyright). May choose
        to licence the work as Creative Commons under Attribution-NonCommercial-ShareAlike 4.0 International 
        (CC BY-NC-SA 4.0).
        
        Parameters
        ----------
        rights: bool
            True if copyright, False if Creative Commons (CC BY-NC-SA 4.0)
        
        """
        if not self.s["metadata"]["validated"]:
            e = "`set_metadata` before setting rights."
            raise PermissionError(e)
        kwargs = {"rights": rights}
        if self.s["metadata"].get("date"):
            kwargs.update({"year": self.s["metadata"]["date"].split("-")[0]})
        if self.s["rights"].get("cover"):
            kwargs.update({"cover_rights": self.s["rights"]["cover"]})
        for extra in ["creator", "publisher", "publisher_uri", "work_uri"]:
            if self.s["metadata"].get(extra):
                kwargs.update({extra: self.s["metadata"][extra]})
        terms = _c.get_rights_template_list(**kwargs)
        soup = BeautifulSoup(_c.XHTML_TEMPLATE, "lxml")
        soup.title.string = self.s["metadata"]["title"]
        for text in terms:
            # https://stackoverflow.com/a/23975648/295606
            if isinstance(text, list) and len(text) == 2:
                # Is an image reference
                html = F"<p class='first center'><img src='{text[0]}' title='{text[1]}' class='logo center' /></p>"
            else:
                # Text or link
                html = F"<p class='first center'>{text}</p>"
                if _c.check_uri(text):
                    html = F"<p class='first center'><a href='{text}'>{urlparse(text).netloc}</a></p>"
            snippet = BeautifulSoup(html, "lxml").p.extract()
            soup.section.append(snippet)
        with open(self.directory + F"rights.xhtml", "w") as w:
            w.write(soup.prettify(formatter="html"))

    def set_dedication(self, dedication: [str, list[str]]):
        """
        Set dedication page for creative work. Provide as a string, unless it is on multiple paragraphs.
        
        Parameters
        ----------
        dedication: str or list of str
            Provide as a string, or list of strings for multiple paragraphs.
        
        """
        if not self.s["metadata"]["validated"]:
            e = "`set_metadata` before setting dedication."
            raise PermissionError(e)
        soup = BeautifulSoup(_c.XHTML_TEMPLATE, "lxml")
        soup.title.string = self.s["metadata"]["title"]
        if isinstance(dedication, str):
            dedication = [dedication]
        for text in dedication:
            html = F"<p class='first center'><i>{text}</i></p>"
            snippet = BeautifulSoup(html, "lxml").p.extract()
            soup.section.append(snippet)
        with open(self.directory + F"dedication.xhtml", "w") as w:
            w.write(soup.prettify(formatter="html"))

    ############################################################################
    # BUILD CREATIVE WORK
    ############################################################################

    def _build_metadata(self):
        """
        Set values for the permitted Dublin Core schema terms.
        """
        dublin_core = list(_c.get_metadata_settings().keys())
        for k, v in self.s["metadata"]["terms"]:
            if k not in dublin_core: continue
            if k in ["identifier", "title", "language", "creator"]:
                if k == "identifier": 
                    if v[:4].lower() == "isbn":
                        self.work.IDENTIFIER_ID = "ISBN"
                    self.work.set_identifier(v)
                if k == "title": 
                    self.work.set_title(v)
                if k == "language": 
                    self.work.set_language(v)
                if k == "creator": 
                    self.work.add_author(v)
            else:
                self.work.add_metadata("DC", k, v)

    def build(self):
        """
        Automatically build the creative work as a standards compliant EPUB3. Save to the root directory.
        """
        root_path = str(Path(self.directory).parent)
        work_path = F"{root_path}/{self.s['work_link']}.epub"
        if not self.s["metadata"]["validated"]:
            e = "`set_metadata` before building creative work."
            raise PermissionError(e)
        # Generate the initial creative content using Pandoc
        with open(self.directory + "data.xml", "w") as xml:
            for k, v in self.s["metadata"]["terms"]:
                xml.write(F"<dc:{k}>{v}</dc:{k}>\n")
        extra_args=[
            F"--epub-metadata={self.directory}data.xml",
            "--toc"
        ]
        pypandoc.convert_file(self.directory + self.s["files"]["docx"], 
                    format="docx+styles",
                    to="epub3", 
                    extra_args=extra_args,
                    outputfile=work_path)
        # Generate the epub version
        spine = []
        resource_path = str(_c.get_helper_path())
        source = epub.read_epub(work_path)
        self.work = epub.EpubBook()
        self._build_metadata()
        creator = self.s["metadata"]["creator"]
        if isinstance(creator, list):
            if len(creator) > 1:
                creator = " &amp; ".join([", ".join(creator[:-1]), creator[-1]])
                pn_author = "authors"
                pn_this = "These authors"
                pn_support = "support"
            else:
                creator = creator[0]
        work_title = F"{self.s['metadata']['title']} by {creator}"
        # Add stylesheet
        default_css = epub.EpubItem(uid="stylesheet", 
                                    file_name="css/stylesheet.css", 
                                    media_type="text/css", 
                                    content=open(resource_path + "/css/stylesheet.css", "rb").read())
        self.work.add_item(default_css)
        # Add cover image
        try:
            _c.check_source(self.directory + self.s["files"]["cover"])
            self.work.set_cover(self.s["files"]["cover"], open(self.directory + self.s["files"]["cover"], "rb").read())
            spine.append("cover")
        except FileNotFoundError:
            pass
        # Add copyright plate
        try:
            _c.check_source(self.directory + "rights.xhtml")
            copyright = epub.EpubHtml(title=work_title, file_name="copyright.xhtml")
            copyright.content = open(self.directory + "rights.xhtml", "rb").read()
            copyright.set_language(self.s["metadata"]["language"])
            copyright.add_item(default_css)
            self.work.add_item(copyright)
            spine.append(copyright)
        except FileNotFoundError:
            pass
        # Add dedication plate - if it exists
        try:
            _c.check_source(self.directory + "dedication.xhtml")
            dedication = epub.EpubHtml(title=work_title, file_name="dedication.xhtml")
            dedication.content = open(self.directory + "dedication.xhtml", "rb").read()
            dedication.set_language(self.s["metadata"]["language"])
            dedication.add_item(default_css)
            self.work.add_item(dedication)
            spine.append(dedication)
        except FileNotFoundError:
            pass
        # Add default Chapisha/Qwyre logo
        logo = epub.EpubImage()
        logo.file_name = "images/logo.png"
        logo.media_type = "image/png"
        logo.content = open(resource_path + "/images/logo.png", "rb").read()
        self.work.add_item(logo)
        # Add default fonts
        for fontfile in os.listdir(resource_path + "/fonts"):
            font = epub.EpubItem()
            font.file_name = "fonts/" + fontfile
            font.media_type = "font/ttf"
            font.content = open(resource_path + "/fonts/" + fontfile, "rb").read()
            self.work.add_item(font)
        # Add all chapters from source
        spine.append("nav")
        toc = []
        chapter_num = 1
        for item in source.get_items():
            if item.get_type() in [ebooklib.ITEM_DOCUMENT, ebooklib.ITEM_IMAGE]:
                # Remove pandoc's folder structure
                item_file = item.get_name().split("/")[-1]
                if item_file == "nav.xhtml":
                    continue
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                chapter_content = item.get_body_content()
                soup = BeautifulSoup(chapter_content, "lxml")
                try:
                    chapter_title = soup.h1.text
                except AttributeError:
                    # isn't a chapter
                    continue
                # Create chapter
                chapter_id = F"chapter_{str(chapter_num)}"
                chapter_num += 1
                chapter = epub.EpubHtml(title=F"{chapter_title} - {self.s['metadata']['title']}", file_name=item_file)
                chapter.content = chapter_content
                chapter.set_language(self.s["metadata"]["language"])
                chapter.add_item(default_css)
                self.work.add_item(chapter)
                spine.append(chapter)
                toc.append(epub.Link(item_file, chapter_title, chapter_id))
            if item.get_type() == ebooklib.ITEM_IMAGE:
                item_image = epub.EpubImage()
                item_image.file_name = "images/" + item_file
                item_image.media_type = item.media_type
                item_image.content = item.get_content()
                self.work.add_item(item_image)
        # Create table of contents and navigation
        self.work.toc = tuple(toc)
        self.work.add_item(epub.EpubNcx())
        self.work.add_item(epub.EpubNav())
        self.work.spine = spine
        # Complete the build
        epub.write_epub(work_path, self.work)

    def validate(self) -> bool:
        """
        Validate the creative work as a standards compliant EPUB3.
        """
        root_path = str(Path(self.directory).parent)
        source = F"{root_path}/{self.s['work_link']}.epub"
        _c.check_source(source)
        result = EpubCheck(source)
        return result.valid