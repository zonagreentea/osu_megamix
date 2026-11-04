import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from security_homework import unpack_homework


class HomeworkSecurityTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make_archive(self, entries, valid_integrity=True):
        archive = self.root / "test.homework"
        h = hashlib.sha256()

        for name, data in sorted(entries.items()):
            h.update(name.encode("utf-8") + b"\0" + data)

        digest = h.hexdigest() if valid_integrity else "invalid"

        with zipfile.ZipFile(archive, "w") as zf:
            for name, data in entries.items():
                zf.writestr(name, data)
            zf.writestr("INTEGRITY", digest)

        return archive

    def test_valid_archive(self):
        archive = self.make_archive({
            "homework.json": b'{"name":"Test","format_version":1,"entry":"main.py"}',
            "main.py": b'print("hello")',
        })

        destination = self.root / "output"
        unpack_homework(archive, destination)

        self.assertTrue((destination / "main.py").exists())

    def test_corrupt_archive_leaves_no_files(self):
        archive = self.make_archive(
            {"main.py": b"hello"},
            valid_integrity=False,
        )

        destination = self.root / "output"

        with self.assertRaises(ValueError):
            unpack_homework(archive, destination)

        self.assertFalse(destination.exists())

    def test_path_traversal_rejected(self):
        archive = self.make_archive({"../escape.txt": b"bad"})
        destination = self.root / "output"

        with self.assertRaises(ValueError):
            unpack_homework(archive, destination)

        self.assertFalse((self.root / "escape.txt").exists())

    def test_existing_destination_protected(self):
        archive = self.make_archive({"main.py": b"hello"})
        destination = self.root / "output"
        destination.mkdir()

        marker = destination / "important.txt"
        marker.write_text("preserve")

        with self.assertRaises(FileExistsError):
            unpack_homework(archive, destination)

        self.assertEqual(marker.read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
