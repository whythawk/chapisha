import sys
try:
	assert sys.version_info >= (3,7)
except AssertionError:
	from chapisha.helpers import common
else:
	from . import common
