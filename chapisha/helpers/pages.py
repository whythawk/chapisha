"""
Standardised XML page creation tools.
"""
import datetime
import zoneinfo
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from typing import Optional

from . import coreio as _c
from .updatezipfile import UpdateZipFile
from ..models.metadata import WorkMetadata, ContributorRoles
from ..models.matter import MatterPartition, FrontMatter, BodyMatter, BackMatter, Matter

DATA_PATH = _c.get_helper_path() / "data" 
DEFAULT_CHAPTER = "chapter-template.xhtml"
DEFAULT_TITLEPAGE = "titlepage.xhtml"
DEFAULT_CONTENT_OPF = "content.opf"
DEFAULT_TOC_NCX = "toc.ncx"
DEFAULT_TOC_XHTML = "toc.xhtml"
DEFAULT_COLOPHON_XHTML = "colophon.xhtml"
DEFAULT_DEDICATION_XHTML = "dedication.xhtml"

def restructure_chapter(source: bytes):
    """
    Given an xml source, restructure the content into the default chapter xhtml format.

    Parameters
    ----------
    source: bytes
        Chapter xhtml as bytes.

    Returns
    -------
    Beautifulsoup xhtml.
    """
    if not isinstance(source, bytes):
        e = "Source is not of type `bytes`."
        raise TypeError(e)
    source = BeautifulSoup(source.decode("utf-8"), "lxml")
    # rename `media` folder to `images`
    for img in source.find_all("img"):
        img["src"] = img["src"].replace("../media/", "../images/")
    with open(DATA_PATH / "xhtml" / DEFAULT_CHAPTER, "r+", encoding="utf-8") as dc:
        chapter = BeautifulSoup(dc.read(), "lxml")
        chapter.section.contents = source.section.contents
        chapter.title.contents = source.title.contents
        chapter.smooth()
    return chapter

def create_titlepage_xhtml(metadata: WorkMetadata) -> str:
    """
    Load the default `titlepage.xhtml` file, and generate the required terms for the creative work. Return xhtml as a string.
    
    Parameters
    ----------
    metadata: WorkMetadata
        All the terms for updating the work, not all compulsory

    Returns
    -------
    str: svg response for `titlepage.xhtml` as a str.
    """
    with open(DATA_PATH / "xhtml" / DEFAULT_TITLEPAGE, "r+", encoding="utf-8") as xhtml_file:
        xml_txt = xhtml_file.read()
        # Title
        xml_txt = xml_txt.replace("WORK_TITLE", metadata.title)
        # Author/s
        creator = metadata.creator
        if isinstance(creator, list):
            if len(creator) > 1:
                creator = " &amp; ".join([", ".join(creator[:-1]), creator[-1]])
            else:
                creator = creator[0]
        xml_txt = xml_txt.replace('<text class="author" x="700" y="290">WORK_AUTHOR</text>',
                                  F'<text class="author" x="700" y="290">{creator}</text>')
    return xml_txt

def create_content_opf(metadata: WorkMetadata, image_manifest: list[str], spine: list[Matter]) -> str:
    """
    Load the default `content.opf` file, and generate the required terms for the creative work. Return xhtml as a string.
    
    Parameters
    ----------
    metadata: WorkMetadata
        All the terms for updating the work, not all compulsory
    manifest: list of str
        Complete resource manifest for the work, derived from `ZipFile.namelist()`
    spine: list of Matter
        Spine and guide list of Matter, with `dedication` at 0, if present

    Returns
    -------
    str: xhtml response for `content.opf` as a str.
    """
    with open(DATA_PATH / "xhtml" / DEFAULT_CONTENT_OPF, "r+", encoding="utf-8") as opf_file:
        opf_xml = opf_file.read()
        ################################################################################################################
        # METADATA
        ################################################################################################################
        # dc:identifier
        opf_xml = opf_xml.replace('<dc:identifier id="uid"></dc:identifier>', 
                                  F'<dc:identifier id="uid">{metadata.identifier}</dc:identifier>')
        # dc:date
        opf_xml = opf_xml.replace('<dc:date></dc:date>', 
                                  F'<dc:date>{metadata.isodate.isoformat().split("T")[0]}T00:00:00Z</dc:date>')
        # meta dcterms:modified date.now
        opf_xml = opf_xml.replace('<meta property="dcterms:modified"></meta>', 
                                  F'<meta property="dcterms:modified">{datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Paris")).isoformat("T", "seconds").split("+")[0]}Z</meta>')
        # dc:rights
        opf_xml = opf_xml.replace('<dc:rights></dc:rights>',
                                  F'<dc:rights>{metadata.rights[0]} For full license information see the Colophon file included at the end of this ebook.</dc:rights>')
        # dc:publisher
        if metadata.publisher:
            opf_xml = opf_xml.replace('<meta property="se:url.homepage" refines="#generator">https://github.com/whythawk/chapisha</meta>', 
                                      F'''<meta property="se:url.homepage" refines="#generator">https://github.com/whythawk/chapisha</meta>\n\t\t<dc:publisher id="publisher">{metadata.publisher}</dc:publisher>\n\t\t<meta property="file-as" refines="#publisher">{metadata.publisher}</meta>''')
        # dc:title
        opf_xml = opf_xml.replace('<dc:title id="title"></dc:title>\n\t\t<meta property="file-as" refines="#title"></meta>', 
                                  F'<dc:title id="title">{metadata.title}</dc:title>\n\t\t<meta property="file-as" refines="#title">{metadata.title}</meta>')
        # dc:subject
        subject_xml = ""
        if len(metadata.subject):
            for i, subject in enumerate(metadata.subject):
                subject_xml += F'\t\t<dc:subject id="subject-{i+1}">{subject}</dc:subject>\n'
        opf_xml = opf_xml.replace('\t\t<dc:subject id="subject-1"></dc:subject>\n', 
                                  subject_xml)
        # dc:description
        description_xml = ""
        if metadata.description:
            description_xml = F'<dc:description id="description">{metadata.description}</dc:description>'
        opf_xml = opf_xml.replace('<dc:description id="description"></dc:description>', 
                                  description_xml)
        # meta long-description
        long_description_xml = ""
        if metadata.long_description:
            long_description_xml = F'<meta id="long-description" property="se:long-description" refines="#description">{metadata.long_description}</meta>'
        opf_xml = opf_xml.replace('<meta id="long-description" property="se:long-description" refines="#description"></meta>', 
                                  long_description_xml)
        # dc:language
        opf_xml = opf_xml.replace('<dc:language></dc:language>', 
                                  F'<dc:language>{metadata.language}</dc:language>')
        # meta word-count
        word_count_xml = ""
        if metadata.word_count:
            word_count_xml = F'<meta property="se:word-count">{metadata.word_count}</meta>'
        opf_xml = opf_xml.replace('<meta property="se:word-count"></meta>', 
                                  word_count_xml)
        # dc:creator
        creator_xml = ""
        for i, creator in enumerate(metadata.creator):
            creator_xml += F'\t\t<dc:creator id="author-{i+1}">{creator}</dc:creator>\n'
        opf_xml = opf_xml.replace('\t\t<dc:creator id="author"></dc:creator>\n', 
                                  creator_xml)
        # dc:contributor
        contributor_xml = ""
        if len(metadata.contributor):
            for i, contributor in enumerate(metadata.contributor):
                contributor_xml += F'\t\t<dc:contributor id="{contributor.id_}-{i+1}">{contributor.name}</dc:contributor>\n'
        opf_xml = opf_xml.replace('\t\t<dc:contributor id="artist"></dc:contributor>\n', 
                                  contributor_xml)
        ################################################################################################################
        # MANIFEST
        ################################################################################################################
        # IMAGES
        image_manifest_xml = ""
        for img in image_manifest:
            media_type = img.split(".")[-1]
            if media_type == "svg": media_type = "svg+xml"
            if media_type == "jpg": media_type = "jpeg"
            if "cover." in img:
                image_manifest_xml += F'\t\t<item href="{img}" id="{img.replace("images/","")}" media-type="image/{media_type}" properties="cover-image"/>\n'
            else:
                image_manifest_xml += F'\t\t<item href="{img}" id="{img.replace("images/","")}" media-type="image/{media_type}"/>\n'
        opf_xml = opf_xml.replace('\t\t<item href="images/titlepage.png" id="titlepage.png" media-type="image/png"/>\n', 
                                  image_manifest_xml)
        # CHAPTERS
        chapter_manifest_xml = ""
        spine_xml = ""
        chapter = 1
        for matter in spine:
            if matter.content == FrontMatter.dedication:
                chapter_manifest_xml += '\t\t<item href="text/dedication.xhtml" id="dedication.xhtml" media-type="application/xhtml+xml"/>\n'
                spine_xml += '\t\t<itemref idref="dedication.xhtml"/>\n'
            if matter.partition == MatterPartition.body:
                chapter_manifest_xml += F'\t\t<item href="text/chapter-{chapter}.xhtml" id="chapter-{chapter}.xhtml" media-type="application/xhtml+xml"/>\n'
                spine_xml += F'\t\t<itemref idref="chapter-{chapter}.xhtml"/>\n'
                chapter += 1
        opf_xml = opf_xml.replace('\t\t<item href="text/chapter-1.xhtml" id="chapter-1.xhtml" media-type="application/xhtml+xml"/>\n',
                                  chapter_manifest_xml)
        opf_xml = opf_xml.replace('\t\t<itemref idref="chapter-1.xhtml"/>\n',
                                  spine_xml)
    return opf_xml

def create_toc_ncx(metadata: WorkMetadata, spine: list[Matter]) -> str:
    """
    Load the default `toc.ncx` file, and generate the required terms for the creative work. Return xhtml as a string.
    
    Parameters
    ----------
    metadata: WorkMetadata
        All the terms for updating the work, not all compulsory
    spine: list of Matter
        Spine and guide list of Matter, with `dedication` at 0, if present

    Returns
    -------
    str: xhtml response for `toc.ncx` as a str.
    """
    with open(DATA_PATH / "xhtml" / DEFAULT_TOC_NCX, "r+", encoding="utf-8") as toc_file:
        toc_xml = toc_file.read()
        ################################################################################################################
        # METADATA
        ################################################################################################################
        # dc:identifier
        toc_xml = toc_xml.replace('<meta content="" name="dtb:uid"/>', 
                                  F'<meta name="dtb:uid" content="{metadata.identifier}"/>')
        ################################################################################################################
        # NAVMAP
        ################################################################################################################
        navpoint = """\t\t<navPoint id="navpoint-{}" playOrder="{}">\n\t\t\t<navLabel>\n\t\t\t\t<text>{}</text>\n\t\t\t</navLabel>\n\t\t\t<content src="text/{}.xhtml"/>\n\t\t</navPoint>\n"""
        navmap_xml = ""
        navcount = 1
        chapter = 1
        # Add Titlepage
        navmap_xml += navpoint.format(navcount, navcount, "Title page", "titlepage")
        for matter in spine:
            navcount += 1
            if matter.content == FrontMatter.dedication:
                navmap_xml += navpoint.format(navcount, navcount, matter.title, "dedication")
            if matter.partition == MatterPartition.body:
                navmap_xml += navpoint.format(navcount, navcount, matter.title, F"chapter-{chapter}")
                chapter += 1
        # Add Colophon
        navmap_xml += navpoint.format(navcount+1, navcount+1, "Colophon", "colophon")
        toc_xml = toc_xml.replace(navpoint.format(1, 1, "Title page", "titlepage"),
                                  navmap_xml)
    return toc_xml

def create_toc_xhtml(metadata: WorkMetadata, spine: list[Matter]) -> str:
    """
    Load the default `toc.xhtml` file, and generate the required terms for the creative work. Return xhtml as a string.
    
    Parameters
    ----------
    metadata: WorkMetadata
        All the terms for updating the work, not all compulsory
    spine: list of Matter
        Spine and guide list of Matter, with `dedication` at 0, if present

    Returns
    -------
    str: xhtml response for `toc.xhtml` as a str.
    """
    with open(DATA_PATH / "xhtml" / DEFAULT_TOC_XHTML, "r+", encoding="utf-8") as toc_file:
        toc_xml = toc_file.read()
        # Table of Contents
        toc_xhtml = ""
        chapter = 1
        for matter in spine:
            if matter.content == FrontMatter.dedication:
                toc_xhtml += F'\t\t\t\t<li>\n\t\t\t\t\t<a href="text/dedication.xhtml">{matter.title}</a>\n\t\t\t\t</li>\n'
            if matter.partition == MatterPartition.body:
                toc_xhtml += F'\t\t\t\t<li>\n\t\t\t\t\t<a href="text/chapter-{chapter}.xhtml">{matter.title}</a>\n\t\t\t\t</li>\n'
                chapter += 1
        toc_xml = toc_xml.replace('\t\t\t\t<li>\n\t\t\t\t\t<a href="text/chapter-1.xhtml"></a>\n\t\t\t\t</li>\n',
                                  toc_xhtml)
        # Landmark Title
        toc_xml = toc_xml.replace('<a href="text/chapter-1.xhtml" epub:type="bodymatter z3998:fiction">WORK_TITLE</a>',
                                  F'<a href="text/chapter-1.xhtml" epub:type="bodymatter z3998:fiction">{metadata.title}</a>')
    return toc_xml

def create_colophon_xhtml(metadata: WorkMetadata) -> str:
    """
    Load the default `colophon.xhtml` file, and generate the required terms for the creative work. Return xhtml as a string.
    
    Parameters
    ----------
    metadata: WorkMetadata
        All the terms for updating the work, not all compulsory

    Returns
    -------
    str: xhtml response for `colophon.xhtml` as a str.
    """
    with open(DATA_PATH / "xhtml" / DEFAULT_COLOPHON_XHTML, "r+", encoding="utf-8") as xml_file:
        xml_txt = xml_file.read()
        # Set title
        xml_txt = xml_txt.replace("WORK_TITLE", metadata.title.upper())
        # Set author/s
        creator = metadata.creator
        if isinstance(creator, list):
            if len(creator) > 1:
                creator = " &amp; ".join([", ".join(creator[:-1]), creator[-1]])
            else:
                creator = creator[0]
        xml_txt = xml_txt.replace("AUTHOR, YEAR.", F"{creator}, {metadata.isodate.year}.")
        # Set author url
        xml_url = ""
        if metadata.work_uri:
            xml_url = F'<p><a href="{metadata.work_uri}">{urlparse(metadata.work_uri).netloc}</a><br/></p>'
        xml_txt = xml_txt.replace('<p><a href="AUTHOR_URL">AUTHOR_URL</a><br/></p>', xml_url)
        # Set publication rights
        xml_rights = ""
        for p in metadata.rights:
            xml_rights += F"\t\t\t<p>{p}</p>\n"
        xml_txt = xml_txt.replace("\t\t\t<p>PUBLICATION_RIGHTS</p>\n", xml_rights)
        # Set publisher and publisher url
        xml_pub = ""
        if metadata.publisher:
            xml_pub = F"<p><br/>Published by {metadata.publisher}.</p>"
        if metadata.publisher_uri:
            xml_pub = F'<p><br/>Published by <a href="{metadata.publisher_uri}">{metadata.publisher}</a>.</p>'
        xml_txt = xml_txt.replace("<p><br/>Published by PUBLISHER.</p>", xml_pub)
        # Set contributors
        xml_ctrb = ""
        for ctrb in metadata.contributor:
            # If ctrb.year is None, then use work year
            if not ctrb.year:
                ctrb.year = metadata.isodate.year
            xml_ctrb += F"<p>{ctrb.id_.capitalize()} contribution is copyright (c) {ctrb.name}, {ctrb.year}. {ctrb.terms}</p>"
        xml_txt = xml_txt.replace("<p>CONTRIBUTORS</p>", xml_ctrb)
    return xml_txt

def create_dedication_xhtml(dedication: [str, list[str]]) -> str:
    """
    Load the default `dedication.xhtml` file, and generate the required terms for the creative work. Return xhtml as a string.
    
    Parameters
    ----------
    dedication: str or list of str
            Provide as a string, or list of strings for multiple paragraphs.

    Returns
    -------
    str: xhtml response for `dedication.xhtml` as a str.
    """
    if isinstance(dedication, str):
        dedication = [dedication]
    with open(DATA_PATH / "xhtml" / DEFAULT_DEDICATION_XHTML, "r+", encoding="utf-8") as xml_file:
        xml_txt = xml_file.read()
        ddctn_xml = ""
        for p in dedication:
            ddctn_xml += F"\t\t\t<p>{p}</p>\n"
        xml_txt = xml_txt.replace("\t\t\tDEDICATION\n", ddctn_xml)
    return xml_txt