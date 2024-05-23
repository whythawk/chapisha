#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import os
import shutil
import base64

from chapisha import __version__
from chapisha import CreateWork

DIRECTORY = Path(__file__).resolve().parent / "data"
TEST_DIRECTORY = Path(__file__).resolve().parent / "_test"
DOCUMENT = DIRECTORY / "usan-abasis-lament.docx"
COVER = DIRECTORY / "cover.jpg"
METADATA_FULL = {
    "identifier": "isbn:9780993191459",
    "title": "Usan Abasi's Lament",
    "description": 'Years after the events of "Lament for the Fallen", Isaiah tells of the myth of Usan Abasi, who was punished by the Sky God to spend eternity in the form of a brass bowl and imprisoned within a vast termite mountain. Now the ceremony which ensures that Usan Abasi remains dormant has failed, and his ancient evil awakes. A free, stand-alone short-story set in the city of Ewuru and linking "Lament for the Fallen" to a forthcoming novel.',
    "language": "en",
    "creator": ["Gavin Chait"],
    "rights": "Attribution-NonCommercial-ShareAlike 4.0 International.",
    "publisher": "Qwyre Publishing",
    "publisher_uri": "https://qwyre.com",
    "work-uri": "https://gavinchait.com",
    "date": "2017-07-23",
    "subject": ["science fiction", "african mythology"],
}
METADATA_PARTIAL = {
    "title": "Usan Abasi's Lament",
    "creator": ["Gavin Chait"],
    "rights": "Attribution-NonCommercial-ShareAlike 4.0 International.",
}
CONTRIBUTOR = {
    "role": "artist",
    "name": "Rodd Halstead",
    "terms": "Cover image 'Red Maple Fruit (Samara)' photograph. All rights reserved. Used under licence.",
    "year": "2006",
}
RIGHTS = [
    "You are free to copy and redistribute the Work in any medium or format, and remix, transform, and build upon the Work. The creator cannot revoke these freedoms as long as you follow the license terms.",
    "In return: You may not use the material for commercial purposes. You must give appropriate credit, provide a link to this license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the creator endorses you or your use. If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original. You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.",
]
DEDICATION = ["For those who leave.", "For those who remain.", "For the wings and tail.", "But most, for her"]
DEDICATION_STRING = "\nFor those who leave.\n\nFor those who remain.\n"


def _delete_temporary_path() -> bool:
    # Try to remove the tree; if it fails, throw an error using try...except.
    # https://stackoverflow.com/a/42641792/295606
    try:
        shutil.rmtree(str(TEST_DIRECTORY))
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return True


def _get_temporary_path(tmp_path: Path | None = None) -> Path:
    if os.getenv("GITHUB_ACTIONS"):
        _delete_temporary_path()
        Path(TEST_DIRECTORY).mkdir(parents=True, exist_ok=True)
        return TEST_DIRECTORY
    return tmp_path


class TestCreateWork:

    def test_version(self):
        assert __version__ == "0.5.2"
        assert Path(DOCUMENT).exists()

    def test_stateless_build(self, tmp_path):
        # tmp_path = _get_temporary_path(tmp_path)
        work = CreateWork(tmp_path, stateless=True)
        work.set_metadata(METADATA_FULL)
        work.set_document(DOCUMENT)
        work.set_cover(COVER)
        work.add_contributor(CONTRIBUTOR)
        work.set_dedication(DEDICATION)
        work.set_rights(RIGHTS)
        assert Path(work.directory / f"{work.work_name}.docx").exists()
        work.build()
        assert work.validate()
        # assert _delete_temporary_path()

    def test_partial_non_stateless_build(self, tmp_path):
        # tmp_path = _get_temporary_path(tmp_path)
        work = CreateWork(tmp_path)
        work.set_metadata(METADATA_PARTIAL)
        with open(DOCUMENT, "rb") as d:
            work_text = base64.b64encode(d.read()).decode("utf-8")
        work.set_document(work_text)
        with open(COVER, "rb") as d:
            cover_img = base64.b64encode(d.read()).decode("utf-8")
        work.set_cover(cover_img)
        work.set_dedication(DEDICATION_STRING)
        work.build()
        assert work.validate()
        # assert _delete_temporary_path()
