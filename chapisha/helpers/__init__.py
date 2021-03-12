import sys
try:
	assert sys.version_info >= (3,7)
except AssertionError:
	from chapisha.helpers import coreio
	from chapisha.helpers.updatezipfile import UpdateZipFile
else:
	from . import coreio
	from .updatezipfile import UpdateZipFile
