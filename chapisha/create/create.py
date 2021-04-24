"""
.. module:: create
  :synopsis: Import a Word `docx` document, define its metadata, cover and rights, and publish it as an EPUB3.

.. moduleauthor:: Gavin Chait <github.com/turukawa>

CreateWork
==========

Publish a standards compliant EPUB3 creative work from a source Microsoft Word `docx` document, and define its 
metadata, cover and publishing rights. Currently does not support `odt` since `Pandoc` seems to lose any embedded
graphics.

.. note:: This process will overwrite any existing EPUB3 file of the same name, if it already exists.

Workflow
--------

There are two main publication approaches, stateless and non-stateless. A non-stateless approach assumes you may be 
starting each step discretely (perhaps via a set of one-time network calls). The second maintains state, so you can
complete the process in one step.


The *stateless* publication process runs as follows:

* Set the working directory on creation,
* Define and validate the metadata required for the creative work,
* Copy the `docx` file to import into the working directory,
* Copy the cover image to import into the working directory,
* Define and add any contributors, such as cover artist,
* Update the creative work's publication rights,
* Add in an optional dedication,
* Build the creative work,
* Validate the work is EPUB3 standards compliant.

The objective of this workflow is to support what may be a stateless process i.e. the individual steps first bring all
the data required to produce the creative work into a project directory, and then produces it. State does not need
to be maintained between steps.

The *non-stateless* process runs as follows:

* Define and validate the metadata required for the creative work,
* Supply the `docx` file as a base64 string,
* Copy the cover image as a base64 string,
* Add in an optional dedication,
* Build the creative work,
* Validate the work is EPUB3 standards compliant.

The objective in a non-stateless workflow is to minimise disruption, and store the minimum amount of information. Only
the epub itself will be saved, and then only because Pandoc does not support a memory-only epub build.

Build your work
---------------

Import **Chapisha** and create a work:

.. code-block:: python

    from chapisha.create import CreateWork

    work = CreateWork(directory)

Where `directory` is the complete path to where you would like the EPUB created. If you want a stateless workflow, 
set the `stateless` boolean to `True`. If you already have the `metadata` (perhaps via a web form), you can skip 
several steps and pick up again for setting the files and images.

.. code-block:: python

    from chapisha.create import CreateWork

    work = CreateWork(directory, metadata=metadata, stateless=True)

Set metadata
^^^^^^^^^^^^

`Dublin Core <https://www.dublincore.org/specifications/dublin-core/dces/>`_ is a vocabulary of fifteen properties for 
use in resource description. Four of them - `title`, `identifier`, `language` and `rights` - are required. The 
`language` code is defined by the `ISO 679-1 <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_ standard 
(e.g. `en` for English, or `fr` for French).

Metadata properties:

* `identifier`: UUID, DOI or ISBN of the creative work. A UUID will be generated if not included.
* `title`: Name given to the creative work.
* `language`: Specify the language of the creative work. Two letter code defined by ISO 639-1.
* `creator`: Name of a person, organisation, etc. responsible for the creation of the work. May be more than one.
* `work_uri`: The URI for your creative work.
* `contributor`: Name of a person, organisation, etc. that played a secondary role - such as an editor - in the creation of the work. May be more than one.
* `date`: The publication date of the creative work. Provide in ISO format, YYYY-MM-DD.
* `subject`: The subject, or tag, of the creative work. May be more than one.
* `publisher`: Name of a person, organisation, etc.  responsible for making the creative work available.
* `publisher_uri`: The URI for the publisher of your creative work.
* `rights`: A short, single-sentence statement of copyright and publication terms for the creative work, e.g. 'All rights reserved.' or 'Attribution-NonCommercial-ShareAlike 4.0 International.'
* `long_rights`: Lengthier description and information about copyright held in and over the creative work. Formatted as you wish it to appear.
* `description`: A short, single-sentence summary of the creative work.
* `long_description`: The pitch, or jacket-cover, description of the creative work.

Create a paired dictionary of these properties. As example:

.. code-block:: python

    METADATA = {
        "identifier": "isbn:9780993191459",
        "title": "Usan Abasi's Lament",
        "description": "Years after the events of \"Lament for the Fallen\", Isaiah tells of the myth of Usan Abasi, who was punished by the Sky God to spend eternity in the form of a brass bowl and imprisoned within a vast termite mountain. Now the ceremony which ensures that Usan Abasi remains dormant has failed, and his ancient evil awakes. A free, stand-alone short-story set in the city of Ewuru and linking \"Lament for the Fallen\" to a forthcoming novel.",
        "language": "en",
        "creator": ["Gavin Chait"],
        "rights": "All rights reserved.",
        "long_rights": ["The right of the creator to be identified as the author of the Work has been asserted by them in accordance with the Copyright, Designs and Patents Act 1988. This creator supports copyright. Copyright gives creators space to explore and provides for their long-term ability to sustain themselves from their work. Thank you for buying this work and for complying with copyright laws by not reproducing, scanning, or distributing any part of it without permission. Your support will contribute to future works by the creator."],
        "publisher": "Qwyre Publishing",
        "publisher_uri": "https://qwyre.com",
        "work-uri": "https://gavinchait.com",
        "date": "2017-07-23",
        "subject": ["science fiction", "african mythology"]
    }

Set the metadata:

.. code-block:: python

    work.set_metadata(METADATA)

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

Where `source` is any of the complete path to the source `docx` file, a `bytes` file import, or a `base64` string.

Set cover
^^^^^^^^^

There is, unfortunately, no standardisation on the image size, dimensions or resolution required for an EPUB. However,
a recommendation is an image (`.jpeg`, `.jpg` or `.png`) of 1,600 by 2,400 pixels, and less than 5Mb is size. You will
need to create your image (or have someone create it for you) exactly as you wish it to appear on the cover. Nothing
will be added, removed, or changed.

Please also ensure you have the appropriate rights to use the image on your cover. There are more than sufficient 
services providing openly-licenced, or even public domain, work for you to use. 

.. note:: You can optionally add the image contributor details here, or on the next step. Do not do it in both or the contributor information will be repeated.

Example code:

.. code-block:: python

    CONTRIBUTOR = {
        "role": "artist", 
        "name": "Rodd Halstead", 
        "terms": "Cover image 'Red Maple Fruit (Samara)' photograph. All rights reserved. Used under licence.", 
        "year": "2006"
    }

    work.set_cover(source, contributor=CONTRIBUTOR)

Where `source` is the complete path to the image file, a `bytes` file import, or a `base64` string.

Add contributors
^^^^^^^^^^^^^^^^

You may have numerous contributors you wish to acknowledge. Fields are:

* `role`: Contributor identity, based on a specified list of `artist`, `editor` or `translator`.
* `name`: Name of a person, organisation, etc. that played a secondary role - such as an editor - in the creation of the work.
* `terms`: Information about copyright held by the rights-holder in and over their contribution to the creative work. Formatted as you wish it to appear.
* `year`: The year of the contribution or publication of the contributor's work.

Example code:

.. code-block:: python

    CONTRIBUTOR = {
        "role": "artist", 
        "name": "Rodd Halstead", 
        "terms": "Cover image 'Red Maple Fruit (Samara)' photograph. All rights reserved. Used under licence.", 
        "year": "2006"
    }

    work.add_contributor(CONTRIBUTOR)

`add_contributor` as many times as you have people or organisations to acknowledge.

Set rights
^^^^^^^^^^

This refers to the `long_rights` you can set, and which you may wish to adjust for presentation on the colophon page.
There are obviously a broad range of rights with which you can release your creative work. Here are two examples which
you can modify as you require.

* Commercial copyright with all rights reserved:

    The right of the creator to be identified as the author of the Work has been asserted by them in 
    accordance with the Copyright, Designs and Patents Act 1988. This creator supports copyright. Copyright 
    gives creators space to explore and provides for their long-term ability to sustain themselves from 
    their work. Thank you for buying this work and for complying with copyright laws by not reproducing, 
    scanning, or distributing any part of it without permission. Your support will contribute to future 
    works by the creator.

* Commercial copyright but licenced for distribution under Attribution-NonCommercial-ShareAlike 4.0 International (`CC BY-NC-SA 4.0 <https://creativecommons.org/licenses/by-nc-sa/4.0/>`_):

    You are free to copy and redistribute the Work in any medium or format, and remix, transform, and build 
    upon the Work. The creator cannot revoke these freedoms as long as you follow the license terms.
    
    In return: You may not use the material for commercial purposes. You must give appropriate credit, provide 
    a link to this license, and indicate if changes were made. You may do so in any reasonable manner, but not
    in any way that suggests the creator endorses you or your use. If you remix, transform, or build upon the 
    material, you must distribute your contributions under the same license as the original. You may not apply 
    legal terms or technological measures that legally restrict others from doing anything the license 
    permits.

Example code:

.. code-block:: python

    RIGHTS = [
        "You are free to copy and redistribute the Work in any medium or format, and remix, transform, and build upon the Work. The creator cannot revoke these freedoms as long as you follow the license terms.",
        "In return: You may not use the material for commercial purposes. You must give appropriate credit, provide a link to this license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the creator endorses you or your use. If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original. You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits."
    ]

    work.set_rights(RIGHTS)

Rights terms can be one line of text, or several. If several, each line must be provided as a separate term in a `list`.

Set dedication
^^^^^^^^^^^^^^

Most creators have a dedication for their work in mind - usually to apologise for all the late nights and impoverishing
returns on their creative efforts.

This is optional, but you can include a dedication page. Each item in the list will be set on a different paragraph.

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
from bs4 import BeautifulSoup
from epubcheck import EpubCheck
from typing import Optional, Literal, List
from urllib.parse import urlparse
from pathlib import Path
import os
import re
import base64
import filetype

from ..models.metadata import WorkMetadata, Contributor
from ..models.matter import Matter, MatterPartition
from ..helpers import pages, formats, coreio as _c
from ..helpers.updatezipfile import UpdateZipFile

class CreateWork:
    """
    Publish a standards compliant EPUB3 creative work from a source Microsoft Word `docx` document, and
    define its metadata, cover and publishing rights.

    If the EPUB file already exists, then publishing this work will overwrite it.

    On instantiation, checks `directory` to see if `DEFAULT_METADATA_SETTINGS` is present, loading the required data,
    or replacing with specified defaults.
    """

    def __init__(self, 
                 directory: Optional[str] = None, 
                 metadata: Optional[WorkMetadata] = None, 
                 stateless: bool = False):
        """
        Initialise the CreateWork class.

        Parameters
        ----------
        directory: str
            A directory path where you would like to save your work.
        metadata: WorkMetadata
            A model defined by a dictionary of terms.
        stateless: bool
            Whether your workflow is stateless (default False).
        """
        self.stateless = stateless
        self.directory = Path(directory)
        if self.stateless:
            _c.check_path(self.directory)
        # Load metadata settings, if exists
        try:
            _c.check_source(self.directory / _c.DEFAULT_METADATA_SETTINGS)
            self.metadata = WorkMetadata(_c.load_json(self.directory / _c.DEFAULT_METADATA_SETTINGS))
            self.work_name = self.directory.name # Since will be `.../work-name/`
        except FileNotFoundError:
            self.metadata = None
            self.work_name = None
        # Construct the metadata, if it is provided
        if metadata:
            if isinstance(metadata, WorkMetadata):
                metadata = metadata.dict()
            self.set_metadata(metadata)
        self.source_path = _c.get_helper_path() / "data" 
        # Set default cover and work bytes
        self.work = None
        self.cover = None
        self.dedication = None

    ############################################################################
    # GATHER WORKING DATA
    ############################################################################

    def get_metadata_schema(self) -> dict:
        """
        Return the standard Dublin Core schema permitted for the EPUB3 standard.

        Returns
        -------
        dict
        """
        return self.metadata.schema()

    def set_metadata(self, metadata: WorkMetadata) -> bool:
        """
        Validate metadata values for the permitted Dublin Core schema terms, along with additional metadata. The full
        schema, with descriptions, and requirements, is listed by `get_metadata_schema`.

        .. note:: The terms `identifier`, `title`, `creator`, `rights` and `language` are required. A random UUID will be assigned if none is provided.

        Parameters
        ----------
        metadata: WorkMetadata
            A model defined by a dictionary of terms.

        Returns
        -------
        bool
        """
        # Dict snake_case fields need to be hyphenated for import
        # This as a result of alias names in model
        if isinstance(metadata, dict):
            for k in [k for k in metadata.keys()]:
                hyphenated = "-".join(k.split("_"))
                metadata[hyphenated] = metadata.pop(k)
            # Rename 'isodate' if it exists
            if "isodate" in metadata:
                metadata["date"] = metadata.pop("isodate")
            # Fix "long-rights" if needed
            if "long-rights" in metadata:
                metadata["long-rights"] = formats.get_text_paragraphs(metadata["long-rights"])
        # Create a temporary WorkMetadata model to hold updated metadata
        updated_metadata = WorkMetadata(**metadata)
        # And update the original data
        # https://fastapi.tiangolo.com/tutorial/body-updates/#partial-updates-with-patch
        if self.metadata:
            self.metadata = self.metadata.copy(update=updated_metadata.dict(exclude_unset=True))
        else:
            self.metadata = updated_metadata
        work_name = "-".join(["".join([e for e in w if e.isalnum()]) 
                               for w in self.metadata.title.lower().split(" ")])
        # Set the working directory, if it isn't already, and save metadata there
        if not self.work_name:
            self.work_name = work_name
            self.directory = self.directory / work_name
        # If stateless, save the metadata to the working folder
        if self.stateless:
            _c.check_path(self.directory)
            _c.save_json(self.metadata.dict(by_alias=True), self.directory / _c.DEFAULT_METADATA_SETTINGS, overwrite=True)
        return True

    def _get_validated_bytes(self, 
                             source: [Path, bytes], 
                             base_type: Optional[List[Literal["cover", "work"]]] = None) -> bytes:
        """
        Validate a source file, and return a bytes version.

        Parameters
        ----------
        source: Path, bytes or base64 string
            Filename to open, base64 string, or bytes from an opened file
        base_type: Optional, str
            Must be one of "cover" or "work" for interpreting base64 mime type

        Raises
        ------
        PermissionError: if metadata not yet validated.
        FileNotFoundError: if the source is not valid.

        Returns
        -------
        bytes
        """
        if not self.metadata:
            e = "`set_metadata` before setting source document."
            raise PermissionError(e)
        if isinstance(source, Path):
            try:
                _c.check_source(source)
                with open(source, "rb") as f:
                    source = f.read()
            except FileNotFoundError:
                e = F"`{source}` is not a valid file source."
                raise FileNotFoundError(e)
        if isinstance(source, str) and base_type:
            # Base64 string, remove any provided mime type
            source_type = re.search(_c.DEFAULT_BASE64_TYPES[base_type], source)
            if source_type:
                source = source.replace(source_type.group(0), "")
            source = base64.b64decode(source)
        if not isinstance(source, bytes):
            e = F"File is not valid."
            raise FileNotFoundError(e)
        return source

    def set_document(self, source: [Path, bytes, str]):
        """
        Import source `docx` document and, if stateless, save to the working directory. If you're finding errors in 
        the build step, it could be you need to convert your base64 string to "utf-8" (`source.decode("utf-8")`).

        Parameters
        ----------
        source: Path, bytes, or str
            Filename to open, bytes from an opened file, or a base64 string

        Raises
        ------
        PermissionError: if metadata not yet validated.
        FileNotFoundError: if the source is not valid.
        """
        if not self.work_name or not self.metadata:
            e = "`set_metadata` before setting source document."
            raise PermissionError(e)
        source = self._get_validated_bytes(source, base_type = "work")
        if self.stateless:
            with open(self.directory / F"{self.work_name}.docx", "wb") as w:
                w.write(source)
        else:
            self.work = source

    def set_cover(self, 
                  source: [Path, bytes],
                  contributor: Optional[Contributor] = None):
        """
        Import cover image and, if stateless, save to the working directory, along with any rights and contributor 
        information. If you're finding errors in the build step, it could be you need to convert your base64 string to 
        "utf-8" (`source.decode("utf-8")`).

        Parameters
        ----------
        source: Path or bytes
            Filename to open, including path, or bytes for file
        contributor: Contributor
            Optional, string indicating contributor name for cover image.

        Raises
        ------
        PermissionError: if metadata not yet validated.
        FileNotFoundError: if the source is not valid.
        """
        if not self.work_name or not self.metadata:
            e = "`set_metadata` before setting cover."
            raise PermissionError(e)
        # Cover contributor
        if contributor: 
            if self.metadata.contributor is None:
                self.metadata.contributor = []
            self.metadata.contributor.append(Contributor(**contributor))
        # Cover image
        source = self._get_validated_bytes(source, base_type = "cover")
        if self.stateless:
            kind = filetype.guess(source).extension
            with open(self.directory / F"cover.{kind}", "wb") as w:
                w.write(source)
            _c.save_json(self.metadata.dict(by_alias=True), 
                                            self.directory / _c.DEFAULT_METADATA_SETTINGS, 
                                            overwrite=True)
        else:
            self.cover = source

    def add_contributor(self, contributor: Contributor):
        """
        Add a contributor to the list of those supporting the creation of the work. `contributor` is defined as a dict:
        
        .. code-block:: python

            contributor = {
                "role": "artist",
                "name": "Great Artist",
                "year": "2021",
                "terms": "Public Domain."
            }

        Parameters
        ----------
        contributor: Contributor
            Include the types of contributor who supported the creation of the work. `role`: `artist`, `editor`, `translator`.

        Raises
        ------
        PermissionError: if metadata not yet validated.
        """
        if not self.work_name or not self.metadata:
            e = "`set_metadata` before adding contributors, or add the contributors when you set the metadata."
            raise PermissionError(e)
        if self.metadata.contributor is None:
            self.metadata.contributor = []
        self.metadata.contributor.append(Contributor(**contributor))
        _c.save_json(self.metadata.dict(by_alias=True), self.directory / _c.DEFAULT_METADATA_SETTINGS, overwrite=True)

    def set_dedication(self, dedication: [str, list[str]]):
        """
        Set dedication page for creative work. Provide as a string, unless it is on multiple paragraphs.
        
        Parameters
        ----------
        dedication: str or list of str
            Provide as a string, or list of strings for multiple paragraphs.
        
        """
        if not self.work_name or not self.metadata:
            e = "`set_metadata` before setting dedication."
            raise PermissionError(e)
        self.dedication = pages.create_dedication_xhtml(dedication)
        if self.stateless:
            with open(self.directory / F"dedication.xhtml", "w") as w:
                w.write(self.dedication)

    def set_rights(self, rights: [str, list[str]]):
        """
        Set publication `long_rights` for creative work. Provide as a string, or list of strings if it is on multiple 
        paragraphs.

        There are multiple appropriate rights, and two examples are below. Modify as you require.

        * Commercial copyright with all rights reserved:

            The right of the creator to be identified as the author of the Work has been asserted by them in 
            accordance with the Copyright, Designs and Patents Act 1988. This creator supports copyright. Copyright 
            gives creators space to explore and provides for their long-term ability to sustain themselves from 
            their work. Thank you for buying this work and for complying with copyright laws by not reproducing, 
            scanning, or distributing any part of it without permission. Your support will contribute to future 
            works by the creator.
        
        * Commercial copyright but licenced for distribution under Attribution-NonCommercial-ShareAlike 4.0 International (`CC BY-NC-SA 4.0 <https://creativecommons.org/licenses/by-nc-sa/4.0/>`_):

            You are free to copy and redistribute the Work in any medium or format, and remix, transform, and build 
            upon the Work. The creator cannot revoke these freedoms as long as you follow the license terms.
            
            In return: You may not use the material for commercial purposes. You must give appropriate credit, provide 
            a link to this license, and indicate if changes were made. You may do so in any reasonable manner, but not
            in any way that suggests the creator endorses you or your use. If you remix, transform, or build upon the 
            material, you must distribute your contributions under the same license as the original. You may not apply 
            legal terms or technological measures that legally restrict others from doing anything the license 
            permits.

        Parameters
        ----------
        rights: str or list of str
            Provide as a string, or list of strings for multiple paragraphs.
        """
        if not self.work_name or not self.metadata:
            e = "`set_metadata` before setting rights."
            raise PermissionError(e)
        if isinstance(rights, str):
            rights = [rights]
        self.metadata.long_rights = rights
        _c.save_json(self.metadata.dict(by_alias=True), self.directory / _c.DEFAULT_METADATA_SETTINGS, overwrite=True)

    ############################################################################
    # BUILD CREATIVE WORK
    ############################################################################

    def build(self):
        """
        Automatically build the creative work as a standards compliant EPUB3. Save to the root directory.
        """
        if not self.work_name or not self.metadata:
            e = "`set_metadata` before building creative work."
            raise PermissionError(e)
        epub_path = self.directory.parent / F"{self.work_name}.epub"
        # Generate the initial creative content using Pandoc
        # pypandoc can't handle PosixPaths ...
        if self.stateless:
            pypandoc.convert_file(str(self.directory / F"{self.work_name}.docx"), 
                                  format="docx",
                                  to="epub3",
                                  outputfile=str(epub_path))
        else:
            # Maybe one day Pandoc can return an epub object and we won't save the interim file
            pypandoc.convert_text(self.work, 
                                  format="docx",
                                  to="epub3",
                                  outputfile=str(epub_path))
        # Generate the epub version
        with UpdateZipFile(epub_path, "a") as w:
            # REMOVES
            REMOVES = ["EPUB/styles/stylesheet1.css", "EPUB/text/title_page.xhtml", "EPUB/nav.xhtml"]
            # DEFAULT COMPONENTS
            DEFAULT = [(self.source_path / "css" / "core.css", "EPUB/css/core.css"),
                    (self.source_path / "images" / "logo.svg", "EPUB/images/logo.svg"),
                    (self.source_path / "xhtml" / "onix.xml", "EPUB/onix.xml"),
                    (self.source_path / "xhtml" / "container.xml", "META-INF/container.xml")]
            for default_file, write_file in DEFAULT:
                w.write(default_file, write_file)
            # DEFAULT FONTS
            for f in os.listdir(self.source_path / "fonts"):
                w.write(self.source_path / "fonts" / f, F"EPUB/fonts/{f}")
            # ADD titlepage.xhtml
            w.writestr("EPUB/text/titlepage.xhtml", pages.create_titlepage_xhtml(self.metadata))
            # ADD colophon.xhtml
            w.writestr("EPUB/text/colophon.xhtml", pages.create_colophon_xhtml(self.metadata))
            # ADD cover.img
            if self.stateless:
                for image_path in [self.directory / F"cover.{t}" for t in ["jpg", "jpeg", "png", "gif", "svg"]]:
                    if image_path.exists():
                        w.write(image_path, F"EPUB/images/{image_path.name}")
            elif self.cover:
                t = filetype.guess(self.cover).extension
                w.writestr(F"EPUB/images/cover.{t}", self.cover)
            # GET DEDICATION and CHAPTERS
            spine = []
            # check if the path to dedication exists, if it does, add it to the work and spine
            if (self.directory / "dedication.xhtml").exists() or self.dedication:
                if self.dedication: 
                    w.writestr("EPUB/text/dedication.xhtml", self.dedication)
                else:
                    w.write(self.directory / "dedication.xhtml", "EPUB/text/dedication.xhtml")
                spine = [Matter(partition="frontmatter", content="dedication", title="Dedication")]
            CHAPTERS = [f for f in w.namelist() if f.startswith("EPUB/text/ch")]
            CHAPTERS.sort()
            self.metadata.word_count = 0
            for chapter in CHAPTERS:
                file_as = F"EPUB/text/chapter-{chapter.split('.')[0][-1]}.xhtml"
                try:
                    chapter_xml = w.read(chapter)
                except KeyError:
                    continue
                if file_as != chapter:
                    # If delete and then re-add same file, causes ZipFile confusion
                    REMOVES.append(chapter)
                # Restructure chapter xml into standard format
                chapter_xml = pages.restructure_chapter(chapter_xml)
                chapter_title = chapter_xml.title.string
                # Count the words (XHTML and HTML treated differently by BeautifulSoup, so first extract `section`)
                words = BeautifulSoup(str(chapter_xml.section), "lxml").get_text()
                self.metadata.word_count += len(words.replace("\n", " ").replace("  ", " ").strip().split())
                w.writestr(file_as, str(chapter_xml))
                spine.append(Matter(partition=MatterPartition.body, title=chapter_title))
            # PANDOC MAY STILL ADD IMAGES FOUND IN THE WORK WHICH WE NEED TO DISCOVER AND ADD TO THE MANIFEST
            # NOTE, these are not only to be added to the manifest, but the folder renamed as well
            image_manifest = [f.replace("EPUB/", "") for f in w.namelist() if f.startswith("EPUB/images/")]
            for img in [f for f in w.namelist() if f.startswith("EPUB/media/")]:
                REMOVES.append(img)
                new_img = img.replace("/media/", "/images/")
                try:
                    old_img = w.read(img)
                    w.writestr(new_img, old_img)
                except KeyError:
                    continue
                image_manifest.append(new_img.replace("EPUB/", ""))
            # ADD content.opf
            w.writestr("EPUB/content.opf", pages.create_content_opf(self.metadata, image_manifest, spine))
            # ADD toc.ncx
            w.writestr("EPUB/toc.ncx", pages.create_toc_ncx(self.metadata, spine))
            # ADD toc.xhtml
            w.writestr("EPUB/toc.xhtml", pages.create_toc_xhtml(self.metadata, spine))
            # PERFORM REMOVES
            for remove in REMOVES:
                try:
                    w.remove_file(remove)
                except KeyError:
                    continue

    def validate(self) -> bool:
        """
        Validate the creative work as a standards compliant EPUB3.
        """
        epub_path = self.directory.parent / F"{self.work_name}.epub"
        _c.check_source(epub_path)
        result = EpubCheck(epub_path)
        return result.valid