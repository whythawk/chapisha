from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
from epubcheck import EpubCheck

from chapisha.helpers.updatezipfile import UpdateZipFile
from chapisha.models.metadata import DublinCoreMetadata, WorkMetadata, ContributorRoles
from chapisha.helpers import coreio as _c


class ReviewWork:
    """
    Review a standards compliant EPUB3 creative work from a source `epub`, and extract its metadata and components.

    Parameters:
        source: A source directory path for the work.

    Example:
        Review a work as follows:

        ```python
        from chapisha.review import ReviewWork

        work = ReviewWork(source)
        ```
    """

    def __init__(self, source: str | Path):
        self.metadata = None
        self.source = source
        if isinstance(source, str):
            self.source = Path(source)

    def replace_image(self, source: str | Path, replace: str):
        if isinstance(source, str):
            source = Path(source)
        # Open the epub
        with UpdateZipFile(self.source, "a") as w:
            # Replace the file in `/images`
            w.write(source, f"EPUB/images/{source.name}")
            w.remove_file(f"EPUB/images/{replace}")
            # Update the manifest
            opf_xml = w.read("EPUB/content.opf")
            opf_xml = BeautifulSoup(opf_xml.decode("utf-8"), features="xml")
            opf_xml.manifest.find_all("item")
            original_image_manifest_xml = str(opf_xml.find(id=replace))
            image_manifest_xml = ""
            media_type = source.name.split(".")[-1]
            if media_type == "svg":
                media_type = "svg+xml"
            if media_type == "jpg":
                media_type = "jpeg"
            image_manifest_xml += (
                f'<item href="images/{source.name}" id="{source.name}" media-type="image/{media_type}"/>\n'
            )
            opf_xml = str(opf_xml).replace(str(original_image_manifest_xml), image_manifest_xml)
            w.writestr("EPUB/content.opf", opf_xml)
            # Process in the text
            for chapter in [f for f in w.namelist() if f.startswith("EPUB/text/")]:
                try:
                    chapter_xml = w.read(chapter)
                except KeyError:
                    continue
                chapter_xml = BeautifulSoup(chapter_xml.decode("utf-8"), features="xml")
                has_replaced = False
                for img in chapter_xml.find_all("img"):
                    if img["src"].endswith(replace):
                        print(replace, source.name)
                        has_replaced = True
                        img["src"] = img["src"].replace(replace, source.name)
                if has_replaced:
                    chapter_xml.smooth()
                    w.writestr(chapter, str(chapter_xml))

    def get_metadata(self) -> WorkMetadata:
        response = {}
        with UpdateZipFile(self.source, "a") as w:
            # DublinCore
            container_xml = w.read("META-INF/container.xml")
            container_xml = BeautifulSoup(container_xml.decode("utf-8"), features="xml")
            opf_xml = w.read(container_xml.rootfile["full-path"])
            opf_xml = BeautifulSoup(opf_xml.decode("utf-8"), features="xml")
            for dc in [k if not v.alias else v.alias for k, v in DublinCoreMetadata.model_fields.items()]:
                if dc not in ["creator", "contributor", "subject"]:
                    text = opf_xml.find(f"dc:{dc}")
                    if text:
                        response[dc] = text.text
                else:
                    texts = opf_xml.find_all(f"dc:{dc}")
                    if dc != "contributor":
                        response[dc] = [t.text for t in texts]
                    else:
                        response[dc] = []
                        for t in texts:
                            role = ContributorRoles.from_text(t.get("id"))
                            if role:
                                response[dc].append({"role": role, "name": t.text})
            # Wordcount
            self.metadata = WorkMetadata(**response)
            self.metadata.word_count = 0
            chapters = []
            for i in [i.get("idref") for i in opf_xml.spine.find_all("itemref") if i.get("idref")]:
                chapters.extend([n for n in w.namelist() if i in n])
            for chapter in chapters:
                try:
                    chapter_xml = w.read(chapter)
                except KeyError:
                    continue
                words = BeautifulSoup(chapter_xml.decode("utf-8"), features="xml").section.get_text()
                self.metadata.word_count += len(words.replace("\n", " ").replace("  ", " ").strip().split())
        return self.metadata

    def get_thumbnail(self, size: tuple[int, int] = (147, 235)) -> Image.Image | None:
        with UpdateZipFile(self.source, "a") as w:
            # DublinCore
            container_xml = w.read("META-INF/container.xml")
            container_xml = BeautifulSoup(container_xml.decode("utf-8"), features="xml")
            opf_xml = w.read(container_xml.rootfile["full-path"])
            opf_xml = BeautifulSoup(opf_xml.decode("utf-8"), features="xml")
            cover = opf_xml.find(attrs={"properties" : "cover-image"})
            if cover and cover.get("href"):
                path = cover.get("href")
                directory = container_xml.rootfile["full-path"].split("/")
                if len(directory) > 1:
                    path = f"{"/".join(directory[:-1])}/{path}"
                # https://stackoverflow.com/a/33167468/295606
                thumb = Image.open(w.open(path))
                thumb.thumbnail(size, Image.Resampling.LANCZOS)
                return thumb
        return None

    def validate(self) -> bool:
        """
        Validate the creative work as a standards compliant EPUB3.

        Returns:
            Boolean `True` if validates.
        """
        _c.check_source(self.source)
        result = EpubCheck(self.source)
        return result.valid
