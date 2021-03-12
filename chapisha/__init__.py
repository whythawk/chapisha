import sys
try:
    assert sys.version_info >= (3,7)
except AssertionError:
    from chapisha.helpers import coreio
    from chapisha.helpers.updatezipfile import UpdateZipFile
    from chapisha.create.create import CreateWork
    from chapisha.models.metadata import DublinCoreMetadata, WorkMetadata, Contributor, ContributorRoles
    from chapisha.models.matter import MatterPartition, FrontMatter, BodyMatter, BackMatter, Matter
else:
    from .helpers import coreio
    from .helpers.updatezipfile import UpdateZipFile
    from .create.create import CreateWork
    from .models.metadata import DublinCoreMetadata, WorkMetadata, Contributor, ContributorRoles
    from .models.matter import MatterPartition, FrontMatter, BodyMatter, BackMatter, Matter

__version__ = '0.2.0'
