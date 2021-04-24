from datetime import date
from uuid import UUID, uuid4
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

def get_urn():
    # Helper class to convert str to callable - we don't need the UUID object
    return uuid4().urn

class ContributorRoles(str, Enum):
    """
    List of terms for the contributor roles.
    """
    artist = "artist"
    editor = "editor"
    translator = "translator"

class Contributor(BaseModel):
    """
    Specific types of contributor who supported the creation of the work. Includes, as `role`: `artist`, `editor`, `translator`.
    """
    role: ContributorRoles = Field(..., description="Contributor identity, based on a specified list of terms.")
    name: str = Field(..., description="Name of a person, organisation, etc. that played a secondary role - such as an editor - in the creation of the work.")
    terms: str = Field(..., description="Information about copyright held by the rights-holder and their terms-of-use for their contribution to the creative work. Formatted as you wish it to appear.")
    year: str = Field(None, description="The year of the contribution or publication of the contributor's work.")

class DublinCoreMetadata(BaseModel):
    """
    Dublin Core parsing model for EPUB3 field compliance.
    """
    # https://pydantic-docs.helpmanual.io/usage/schema/#field-customisation
    identifier: str = Field(default_factory=get_urn,
                            description="UUID, DOI or ISBN of the creative work. A UUID will be generated if not included.")
    title: str = Field(..., description="Name given to the creative work.")
    language: str = Field(default="en", 
                          description="Specify the language of the creative work. Two letter code defined by ISO 639-1.")
    rights: str = Field(default="All rights reserved.", 
                        description="A short, single-sentence statement of copyright and publication terms for the creative work, e.g. 'All rights reserved.' or 'Attribution-NonCommercial-ShareAlike 4.0 International.'")
    description: str = Field(None, description="A short, single-sentence summary of the creative work.")
    creator: list[str] = Field(..., description="Name of a person, organisation, etc. responsible for the creation of the work. May be more than one.")
    contributor: list[Contributor] = Field(None, description="Name of a person, organisation, etc. that played a secondary role - such as an editor - in the creation of the work. May be more than one.")
    isodate: date = Field(default_factory=date.today, alias="date", 
                          description="The publication date of the creative work. Provide in ISO format, YYYY-MM-DD.")
    subject: list[str] = Field(None, description="The subject, or tag, of the creative work. May be more than one.")
    publisher: str = Field(None, description="Name of a person, organisation, etc.  responsible for making the creative work available.")
        
class WorkMetadata(DublinCoreMetadata):
    """
    Dublin Core parsing model for EPUB3 field compliance. Extends the StandardModel to provide additional optional
    properties to be included.
    """
    long_description: Optional[str] = Field(None, alias="long-description", 
                                            description="The pitch, or jacket-cover, description of the creative work.")
    long_rights: Optional[list[str]] = Field(None, alias="long-rights",
                                             description="Information about copyright held in and over the creative work. Formatted as you wish it to appear.")
    work_uri: Optional[HttpUrl] = Field(None, alias="work-uri", 
                                        description="The URI for your creative work.")
    publisher_uri: Optional[HttpUrl] = Field(None, alias="publisher-uri", 
                                             description="The URI for the publisher of your creative work.")
    word_count: Optional[int] = Field(None, alias="word-count",
                                      description="Total word count of your creative work.")
