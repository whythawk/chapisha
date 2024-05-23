import pypandoc
from bs4 import BeautifulSoup
from epubcheck import EpubCheck
from typing import Optional, Literal, List
from pathlib import Path
import os
import re
import base64
import filetype

from chapisha.models.metadata import WorkMetadata, Contributor
from chapisha.models.matter import Matter, MatterPartition
from chapisha.helpers import pages, formats, coreio as _c
from chapisha.helpers.updatezipfile import UpdateZipFile


class CreateWork:
    """
    Publish a standards compliant EPUB3 creative work from a source Microsoft Word `docx` document, and
    define its metadata, cover and publishing rights.

    If the EPUB file already exists, then publishing this work will overwrite it.

    On instantiation, checks `directory` to see if `DEFAULT_METADATA_SETTINGS` is present, loading the required data,
    or replacing with specified defaults.

    Parameters:
        directory: A directory path where you would like to save your work.
        metadata: A model defined by a dictionary of terms.
        stateless: Whether your workflow is stateless (default False).

    Example:
        Create a new work as follows:

        ```python
        from chapisha.create import CreateWork

        work = CreateWork(directory, metadata=metadata, stateless=True)
        ```
    """

    def __init__(
        self, directory: Optional[str] = None, metadata: Optional[WorkMetadata] = None, stateless: bool = False
    ):
        self.stateless = stateless
        self.directory = Path(directory)
        if self.stateless:
            _c.check_path(self.directory)
        # Load metadata settings, if exists
        try:
            _c.check_source(self.directory / _c.DEFAULT_METADATA_SETTINGS)
            self.metadata = WorkMetadata(_c.load_json(self.directory / _c.DEFAULT_METADATA_SETTINGS))
            self.work_name = self.directory.name  # Since will be `.../work-name/`
        except FileNotFoundError:
            self.metadata = None
            self.work_name = None
        # Construct the metadata, if it is provided
        if metadata:
            if isinstance(metadata, WorkMetadata):
                metadata = metadata.model_dump()
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

        Returns:
            A dictionary definition of the metadata.
        """
        return self.metadata.model_json_schema()

    def set_metadata(self, metadata: WorkMetadata) -> bool:
        """
        Validate metadata values for the permitted Dublin Core schema terms, along with additional metadata. The full
        schema, with descriptions, and requirements, is listed by `get_metadata_schema`.

        !!! note
            The terms `identifier`, `title`, `creator`, `rights` and `language` are required. A random UUID will be assigned if none is provided.

        Parameters:
            metadata: A model defined by a dictionary of terms.

        Returns:
            Boolean response on acceptance.
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
            self.metadata = self.metadata.copy(update=updated_metadata.model_dump(exclude_unset=True))
        else:
            self.metadata = updated_metadata
        work_name = "-".join(["".join([e for e in w if e.isalnum()]) for w in self.metadata.title.lower().split(" ")])
        # Set the working directory, if it isn't already, and save metadata there
        if not self.work_name:
            self.work_name = work_name
            self.directory = self.directory / work_name
        # If stateless, save the metadata to the working folder
        if self.stateless:
            _c.check_path(self.directory)
            _c.save_json(
                self.metadata.model_dump(by_alias=True), self.directory / _c.DEFAULT_METADATA_SETTINGS, overwrite=True
            )
        return True

    def _get_validated_bytes(
        self, source: Path | bytes, base_type: Optional[List[Literal["cover", "work"]]] = None
    ) -> bytes:
        """
        Validate a source file, and return a bytes version.

        Parameters:
            source: Filename to open, base64 string, or bytes from an opened file
            base_type: Must be one of "cover" or "work" for interpreting base64 mime type

        Raises:
            PermissionError: if metadata not yet validated.
            FileNotFoundError: if the source is not valid.

        Returns:
            A bytes response.
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
                e = f"`{source}` is not a valid file source."
                raise FileNotFoundError(e)
        if isinstance(source, str) and base_type:
            # Base64 string, remove any provided mime type
            source_type = re.search(_c.DEFAULT_BASE64_TYPES[base_type], source)
            if source_type:
                source = source.replace(source_type.group(0), "")
            source = base64.b64decode(source)
        if not isinstance(source, bytes):
            e = "File is not valid."
            raise FileNotFoundError(e)
        return source

    def set_document(self, source: Path | bytes | str):
        """
        Import source `docx` document and, if stateless, save to the working directory. If you're finding errors in
        the build step, it could be you need to convert your base64 string to "utf-8" (`source.decode("utf-8")`).

        Parameters:
            source: Filename to open, bytes from an opened file, or a base64 string

        Raises:
            PermissionError: If metadata not yet validated.
            FileNotFoundError: If the source is not valid.
        """
        if not self.work_name or not self.metadata:
            e = "`set_metadata` before setting source document."
            raise PermissionError(e)
        source = self._get_validated_bytes(source, base_type="work")
        if self.stateless:
            with open(self.directory / f"{self.work_name}.docx", "wb") as w:
                w.write(source)
        else:
            self.work = source

    def set_cover(self, source: Path | bytes, contributor: Optional[Contributor] = None):
        """
        Import cover image and, if stateless, save to the working directory, along with any rights and contributor
        information. If you're finding errors in the build step, it could be you need to convert your base64 string to
        "utf-8" (`source.decode("utf-8")`).

        Parameters:
            source: Filename to open, including path, or bytes for file
            contributor:  Optional, string indicating contributor name for cover image.

        Raises:
            PermissionError: If metadata not yet validated.
            FileNotFoundError: If the source is not valid.
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
        source = self._get_validated_bytes(source, base_type="cover")
        if self.stateless:
            kind = filetype.guess(source).extension
            with open(self.directory / f"cover.{kind}", "wb") as w:
                w.write(source)
            _c.save_json(
                self.metadata.model_dump(by_alias=True), self.directory / _c.DEFAULT_METADATA_SETTINGS, overwrite=True
            )
        else:
            self.cover = source

    def add_contributor(self, contributor: Contributor):
        """
        Add a contributor to the list of those supporting the creation of the work. `contributor` is defined as a dict:

        !!! example
            ```python
            contributor = {
                "role": "artist",
                "name": "Great Artist",
                "year": "2021",
                "terms": "Public Domain."
            }
            ```

        Parameters:
            contributor: Include the types of contributor who supported the creation of the work. `role`: `artist`, `editor`, `translator`.

        Raises:
            PermissionError: if metadata not yet validated.
        """
        if not self.work_name or not self.metadata:
            e = "`set_metadata` before adding contributors, or add the contributors when you set the metadata."
            raise PermissionError(e)
        if self.metadata.contributor is None:
            self.metadata.contributor = []
        self.metadata.contributor.append(Contributor(**contributor))
        _c.save_json(
            self.metadata.model_dump(by_alias=True), self.directory / _c.DEFAULT_METADATA_SETTINGS, overwrite=True
        )

    def set_dedication(self, dedication: str | list[str]):
        """
        Set dedication page for creative work. Provide as a string, unless it is on multiple paragraphs.

        Parameters:
            dedication: Provide as a string, or list of strings for multiple paragraphs.
        """
        if not self.work_name or not self.metadata:
            e = "`set_metadata` before setting dedication."
            raise PermissionError(e)
        self.dedication = pages.create_dedication_xhtml(dedication)
        if self.stateless:
            with open(self.directory / "dedication.xhtml", "w") as w:
                w.write(self.dedication)

    def set_rights(self, rights: str | list[str]):
        """
        Set publication `long_rights` for creative work. Provide as a string, or list of strings if it is on multiple
        paragraphs.

        There are multiple appropriate rights, and two examples are below. Modify as you require.

        - Commercial copyright with all rights reserved:

            The right of the creator to be identified as the author of the Work has been asserted by them in
            accordance with the Copyright, Designs and Patents Act 1988. This creator supports copyright. Copyright
            gives creators space to explore and provides for their long-term ability to sustain themselves from
            their work. Thank you for buying this work and for complying with copyright laws by not reproducing,
            scanning, or distributing any part of it without permission. Your support will contribute to future
            works by the creator.

        - Commercial copyright but licenced for distribution under Attribution-NonCommercial-ShareAlike 4.0 International ([CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)):

            You are free to copy and redistribute the Work in any medium or format, and remix, transform, and build
            upon the Work. The creator cannot revoke these freedoms as long as you follow the license terms.

            In return: You may not use the material for commercial purposes. You must give appropriate credit, provide
            a link to this license, and indicate if changes were made. You may do so in any reasonable manner, but not
            in any way that suggests the creator endorses you or your use. If you remix, transform, or build upon the
            material, you must distribute your contributions under the same license as the original. You may not apply
            legal terms or technological measures that legally restrict others from doing anything the license
            permits.

        Parameters:
            rights: Provide as a string, or list of strings for multiple paragraphs.
        """
        if not self.work_name or not self.metadata:
            e = "`set_metadata` before setting rights."
            raise PermissionError(e)
        if isinstance(rights, str):
            rights = [rights]
        self.metadata.long_rights = rights
        _c.save_json(
            self.metadata.model_dump(by_alias=True), self.directory / _c.DEFAULT_METADATA_SETTINGS, overwrite=True
        )

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
        epub_path = self.directory.parent / f"{self.work_name}.epub"
        sandbox = True
        if os.getenv("GITHUB_ACTIONS"):
            # Specific case in testing Github Actions, problem with sandbox
            sandbox = False
        # Generate the initial creative content using Pandoc
        # pypandoc can't handle PosixPaths ...
        if self.stateless:
            pypandoc.convert_file(
                str(self.directory / f"{self.work_name}.docx"),
                format="docx",
                to="epub3",
                outputfile=str(epub_path),
                sandbox=sandbox,
            )
        else:
            # Maybe one day Pandoc can return an epub object and we won't save the interim file
            pypandoc.convert_text(self.work, format="docx", to="epub3", outputfile=str(epub_path), sandbox=sandbox)
        # Generate the epub version
        with UpdateZipFile(epub_path, "a") as w:
            # REMOVES
            REMOVES = ["EPUB/styles/stylesheet1.css", "EPUB/text/title_page.xhtml", "EPUB/nav.xhtml"]
            # DEFAULT COMPONENTS
            DEFAULT = [
                (self.source_path / "css" / "core.css", "EPUB/css/core.css"),
                (self.source_path / "images" / "logo.svg", "EPUB/images/logo.svg"),
                (self.source_path / "xhtml" / "onix.xml", "EPUB/onix.xml"),
                (self.source_path / "xhtml" / "container.xml", "META-INF/container.xml"),
            ]
            for default_file, write_file in DEFAULT:
                w.write(default_file, write_file)
            # DEFAULT FONTS
            for f in os.listdir(self.source_path / "fonts"):
                w.write(self.source_path / "fonts" / f, f"EPUB/fonts/{f}")
            # ADD titlepage.xhtml
            w.writestr("EPUB/text/titlepage.xhtml", pages.create_titlepage_xhtml(self.metadata))
            # ADD colophon.xhtml
            w.writestr("EPUB/text/colophon.xhtml", pages.create_colophon_xhtml(self.metadata))
            # ADD cover.img
            if self.stateless:
                for image_path in [self.directory / f"cover.{t}" for t in ["jpg", "jpeg", "png", "gif", "svg"]]:
                    if image_path.exists():
                        w.write(image_path, f"EPUB/images/{image_path.name}")
            elif self.cover:
                t = filetype.guess(self.cover).extension
                w.writestr(f"EPUB/images/cover.{t}", self.cover)
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
            for i, chapter in enumerate(CHAPTERS):
                file_as = f"EPUB/text/chapter-{chapter.split('.')[0][-1]}.xhtml"
                try:
                    chapter_xml = w.read(chapter)
                except KeyError:
                    continue
                if file_as != chapter:
                    # If delete and then re-add same file, causes ZipFile confusion
                    REMOVES.append(chapter)
                # Restructure chapter xml into standard format
                chapter_xml = pages.restructure_chapter(chapter_xml, str(i))
                chapter_title = chapter_xml.title.string
                # Count the words (XHTML and HTML treated differently by BeautifulSoup, so first extract `section`)
                words = BeautifulSoup(str(chapter_xml.section), features="xml").get_text()
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

        Returns:
            Boolean `True` if validates.
        """
        epub_path = self.directory.parent / f"{self.work_name}.epub"
        _c.check_source(epub_path)
        result = EpubCheck(epub_path)
        return result.valid
