import os
import tempfile
from zipfile import ZipFile, ZIP_STORED, ZipInfo

# https://bugs.python.org/issue38633
import shutil
from typing import Optional
from pathlib import Path


class UpdateZipFile(ZipFile):
    """
    Extended ZipFile methods for updating an existing EPUB, including:

    - `writestr` and `write` to update or add new files to the archive,
    - `remove_file` to remove a file from the archive.

    !!! example
        ```python
        with UpdateWork("path_to_work", "a") as w:
            # E.g. writing an updated nav.xhtml
            w.writestr("EPUB/text/nav.xhtml", soup.prettify(formatter="html"))
        ```

    Upon  __exit__ (if updates were applied) a new zip file will override the exiting one
    with the updates.

    Derived from [@OrWeis](https://stackoverflow.com/a/35435548/295606) & updated for Python 3
    Also, [source](https://github.com/python/cpython/blob/3.9/Lib/zipfile.py).
    """

    class DeleteMarker:
        pass

    def __init__(
        self,
        file: str | bytes,
        mode: str = "a",
        compression: int = ZIP_STORED,
        allowZip64: bool = False,
        compresslevel: Optional[int] = None,
    ):
        """
        Initialise UpdateWork.

        Parameters:
            file: Either the path to the file, or a file-like object. If it is a path, the file will be opened and closed by ZipFile.
            mode: The mode can be either read 'r', write 'w', exclusive create 'x', or append 'a'.
            compression: ZIP_STORED (no compression), ZIP_DEFLATED (requires zlib), ZIP_BZIP2 (requires bz2) or ZIP_LZMA (requires lzma).
            allowZip64: If True ZipFile will create files with ZIP64 extensions when needed, otherwise it will raise an exception when this would be necessary.
            compresslevel:
                Default for the given compression type, or an integer specifying the level to pass to the compressor.
                When using ZIP_STORED or ZIP_LZMA this keyword has no effect. When using ZIP_DEFLATED integers 0 through 9 are accepted.
                When using ZIP_BZIP2 integers 1 through 9 are accepted.
        """
        super().__init__(file, mode=mode, compression=compression, allowZip64=allowZip64, compresslevel=compresslevel)
        # track file to override in zip
        self._replace = {}
        # Whether the with statement was called
        self._allow_updates = False

    def writestr(self, zinfo_or_arcname: str | ZipInfo, data: str | bytes, compress_type: Optional[int] = None):
        """
        Write a file into the archive.

        Parameters:
            data:  The contents are 'data', which may be either a 'str' or a 'bytes' instance; if it is a 'str', it is encoded as UTF-8 first.
            zinfo_or_arcname:  Where, if str, is the name of the file in the archive.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        if isinstance(zinfo_or_arcname, ZipInfo):
            name = zinfo_or_arcname.filename
        else:
            name = zinfo_or_arcname
        # If the file exits, and needs to be overridden,
        # mark the entry, and create a temp-file for it
        # we allow this only if the with statement is used
        if self._allow_updates and name in self.namelist():
            temp_file = self._replace[name] = self._replace.get(name, tempfile.TemporaryFile())
            temp_file.write(data)
        # Otherwise just act normally
        else:
            super().writestr(zinfo_or_arcname, data, compress_type=compress_type)

    def write(
        self,
        filename: str,
        arcname: Optional[str] = None,
        compress_type: Optional[int] = None,
        compresslevel: Optional[int] = None,
    ):
        """
        Put the bytes from filename into the archive under the name arcname.

        Parameters:
            filename: Complete path to source file
            arcname: Name of destination file. If not provided, filename and arname are the same.
            compress_type: The numeric constant for an uncompressed archive member.
            compresslevel:
                Default for the given compression type, or an integer specifying the level to pass to the compressor.
                When using ZIP_STORED or ZIP_LZMA this keyword has no effect. When using ZIP_DEFLATED integers 0
                through 9 are accepted. When using ZIP_BZIP2 integers 1 through 9 are accepted.
        """
        arcname = arcname or filename
        # If the file exits, and needs to be overridden,
        # mark the entry, and create a temp-file for it
        # we allow this only if the with statement is used
        if self._allow_updates and arcname in self.namelist():
            temp_file = self._replace[arcname] = self._replace.get(arcname, tempfile.TemporaryFile())
            with open(filename, "rb") as source:
                shutil.copyfileobj(source, temp_file)
        # Otherwise just act normally
        else:
            super().write(filename, arcname=arcname, compress_type=compress_type, compresslevel=compresslevel)

    def remove_file(self, path: str | Path):
        """
        Delete an object from the archive.

        Parameters:
            path: str or Path
        """
        self._replace[path] = self.DeleteMarker()

    def __enter__(self):
        # Allow updates
        self._allow_updates = True
        return self

    def __exit__(self, type, value, traceback):
        # call base to close zip file, organically
        try:
            super().__exit__(type, value, traceback)
            if len(self._replace) > 0:
                self._rebuild_zip()
        finally:
            # In case rebuild zip failed,
            # be sure to still release all the temp files
            self._close_all_temp_files()
            self._allow_updates = False

    def _close_all_temp_files(self):
        for temp_file in self._replace.values():
            if hasattr(temp_file, "close"):
                temp_file.close()

    def _rebuild_zip(self):
        tempdir = tempfile.mkdtemp()
        try:
            temp_zip_path = os.path.join(tempdir, "new.zip")
            with ZipFile(self.filename, "r") as zip_read:
                # Create new zip with assigned properties
                with ZipFile(
                    temp_zip_path, "w", compression=self.compression, allowZip64=self._allowZip64
                ) as zip_write:
                    for item in zip_read.infolist():
                        # Check if the file should be replaced / or deleted
                        replacement = self._replace.get(item.filename, None)
                        # If marked for deletion, do not copy file to new zipfile
                        if isinstance(replacement, self.DeleteMarker):
                            del self._replace[item.filename]
                            continue
                        # If marked for replacement, copy temp_file, instead of old file
                        elif replacement is not None:
                            del self._replace[item.filename]
                            # Write replacement to archive,
                            # and then close it (deleting the temp file)
                            replacement.seek(0)
                            data = replacement.read()
                            replacement.close()
                        else:
                            data = zip_read.read(item.filename)
                        zip_write.writestr(item, data)
            # Override the archive with the updated one
            shutil.move(temp_zip_path, self.filename)
        finally:
            shutil.rmtree(tempdir)
