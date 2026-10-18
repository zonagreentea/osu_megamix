import json
import tempfile
import unittest
from pathlib import Path

import homework


class ProductionHomeworkSecurityTests(unittest.TestCase):

    def test_pack_unpack_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            source.mkdir()

            (source / "homework.json").write_text(
                json.dumps({
                    "name": "Fictional Game",
                    "format_version": 1,
                    "entry": "main.py",
                }),
                encoding="utf-8",
            )
            (source / "main.py").write_text(
                'print("hello")',
                encoding="utf-8",
            )

            archive = root / "game.homework"
            destination = root / "unpacked"

            homework.pack_homework(source, archive)
            result = homework.unpack_homework(archive, destination)

            self.assertEqual(result, destination)
            self.assertTrue((destination / "main.py").exists())
            self.assertEqual(
                (destination / "main.py").read_text(encoding="utf-8"),
                'print("hello")',
            )

    def test_existing_destination_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            source.mkdir()
            (source / "main.py").write_text("hello", encoding="utf-8")
            archive = root / "game.homework"
            homework.pack_homework(source, archive)
            destination = root / "existing"
            destination.mkdir()
            marker = destination / "important.txt"
            marker.write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                homework.unpack_homework(archive, destination)
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
