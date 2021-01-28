import sys
try:
	assert sys.version_info >= (3,7)
except AssertionError:
	from chapisha.create import CreateWork
else:
	from .create import CreateWork