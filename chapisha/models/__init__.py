import sys
try:
	assert sys.version_info >= (3,7)
except AssertionError:
	from chapisha.models.metadata import DublinCoreMetadata, WorkMetadata, Contributor, ContributorRoles
	from chapisha.models.matter import MatterPartition, FrontMatter, BodyMatter, BackMatter, Matter
else:
	from .metadata import DublinCoreMetadata, WorkMetadata, Contributor, ContributorRoles
	from .matter import MatterPartition, FrontMatter, BodyMatter, BackMatter, Matter