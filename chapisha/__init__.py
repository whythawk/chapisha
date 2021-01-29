import sys
try:
    assert sys.version_info >= (3,7)
except AssertionError:
    from chapisha.helpers import common
    from chapisha.create.create import CreateWork
else:
    from .helpers import common
    from .create.create import CreateWork
__version__ = '0.1.0'
sys.path.append('../..')
sys.path.append('..')  # << Is needed; Otherwise not found within Sphinx
