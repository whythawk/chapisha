from enum import Enum
from typing import Union, Optional
from pydantic import BaseModel, Field, root_validator

class MatterPartition(str, Enum):
    """
    EPUBs consist of three major partitions: Front Matter, Body Matter, and Back Matter.
    
    See: https://standardebooks.org/manual/1.3.1/3-the-structure-of-an-ebook
    """
    front = "frontmatter"
    body = "bodymatter"
    back = "backmatter"
    
class FrontMatter(str, Enum):
    """
    Front matter is material that appears before the main content of the work. It includes 
    such items as a dedication, an epigraph, an introduction, and so on.
    """
    cover = "cover"
    titlepage = "titlepage"
    imprint = "imprint"
    dedication = "dedication"
    epigraph = "epigraph"
    acknowledgements = "acknowledgements"
    foreword = "foreword"
    preface = "preface"
    introduction = "introduction"
    toc = "toc"
    
class BodyMatter(str, Enum):
    """
    The body matter is the main content of the book. It is typically divided into chapters, 
    or in the case of a collection, individual stories, poems, or articles. It may be structured 
    at the highest level into larger divisions such as volumes or parts.
    
    If is body matter, and no type is specified, defaults to chapter ...
    """
    prologue = "prologue"
    epilogue = "epilogue"
    
class BackMatter(str, Enum):
    """
    Back matter is material which follows the main content, but could be separated from the main 
    content. It might include endnotes, an appendix, an afterword, a colophon, and so on.
    """
    afterword = "afterword"
    illustrations = "illustrations"
    endnotes = "endnotes"
    colophon = "colophon"
    copyright = "copyright"
    
class Matter(BaseModel):
    """
    Specific attributes of a matter object. Includes one partition, and one of Front, Body or 
    Back matter.
    """
    partition: MatterPartition = Field(..., description="Major partition for the work.")
    content: Optional[Union[FrontMatter, BodyMatter, BackMatter]] = Field(None, description="Material to be included in the work. If none provided, is a chapter by default.")
    title: Optional[str] = Field(None, description="Matter title. If none provided, takes the term for the matter content type. Must be provided if a chapter.")

    @root_validator
    def assure_matter_is_related(cls, values):
        p, c, t = values.get("partition"), values.get("content"), values.get("title")
        if c is None:
            assert p == MatterPartition.body
            assert t is not None
        if p == p.front:
            assert isinstance(c, FrontMatter)
        if p == p.back:
            assert isinstance(c, BackMatter)
        if p == p.body and c is not None:
            assert isinstance(c, BodyMatter)
        return values