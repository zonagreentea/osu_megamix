import unittest
import zipfile
from pathlib import Path

from test_security_homework import HomeworkSecurityTests
from security_homework import unpack_homework


class AdditionalSecurityTests(HomeworkSecurityTests):

    def test_windows_path_traversal_rejected(self):
        archive = self.make_archive({
            r"..\escape.txt": b"bad"
        })

        with self.assertRaises(ValueError):
            unpack_homework(archive, self.root / "output")

    def test_windows_reserved_filename_rejected(self):
        archive = self.make_archive({
            "CON.txt": b"bad"
        })

        with self.assertRaises(ValueError):
            unpack_homework(archive, self.root / "output")

    def test_duplicate_archive_entries_rejected(self):
        archive = self.root / "duplicate.homework"

        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("main.py", b"first")
            zf.writestr("main.py", b"second")

        with self.assertRaises(ValueError):
            unpack_homework(archive, self.root / "output")


if __name__ == "__main__":
    unittest.main()
