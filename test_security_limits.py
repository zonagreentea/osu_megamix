import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import security_homework


class ExtractionLimitTests(unittest.TestCase):

    def test_total_size_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "large.homework"

            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("main.py", b"1234567890")
                zf.writestr("INTEGRITY", "unused")

            with patch.object(security_homework, "MAX_TOTAL_SIZE", 5):
                with self.assertRaises(ValueError):
                    security_homework.unpack_homework(
                        archive, root / "output"
                    )

            self.assertFalse((root / "output").exists())

    def test_individual_file_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "large.homework"

            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("main.py", b"1234567890")
                zf.writestr("INTEGRITY", "unused")

            with patch.object(security_homework, "MAX_FILE_SIZE", 5):
                with self.assertRaises(ValueError):
                    security_homework.unpack_homework(
                        archive, root / "output"
                    )

            self.assertFalse((root / "output").exists())


if __name__ == "__main__":
    unittest.main()
