from pathlib import Path

from chapisha import __version__
from chapisha import CreateWork

DIRECTORY = str(Path(__file__).resolve().parent)
DOCUMENT = DIRECTORY + "/data/Usan Abasi’s Lament - ebook.docx"
COVER = DIRECTORY + "/data/cover.jpg"
METADATA = [['title', "Usan Abasi's Lament"],
 ['description',
  'Years after the events of "Lament for the Fallen", Isaiah tells of the myth of Usan Abasi, who was punished by the Sky God to spend eternity in the form of a brass bowl and imprisoned within a vast termite mountain. Now the ceremony which ensures that Usan Abasi remains dormant has failed, and his ancient evil awakes. A free, stand-alone short-story set in the city of Ewuru and linking "Lament for the Fallen" to a forthcoming novel.'],
 ['creator', 'Gavin Chait'],
 ['work_uri', 'https://gavinchait.com'],
 ['language', 'en'],
 ['date', '2017-07-23'],
 ['rights', 'All rights reserved'],
 ['publisher', 'Qwyre Publishing'],
 ['publisher_uri', 'https://qwyre.com'],
 ['identifier', 'isbn_9780993191459'],
 ['subject', 'science fiction'],
 ['subject', 'african mythology']]
DEDICATION = [
    "For those who leave.",
    "For those who remain.",
    "For the wings and tail.",
    "But most, for her"
]

class TestCreateWork:

    def test_version(self):
        assert __version__ == '0.1.0'

    def test_build(self, tmpdir):
        work = CreateWork(str(tmpdir))
        work.set_metadata(METADATA)
        work.set_document(DOCUMENT)
        work.set_cover(COVER, rights="Cover image copyright Rodd Halstead.")
        work.set_rights(rights=False)
        work.set_dedication(DEDICATION)
        work.build()
        assert work.validate()

