"""Safe extraction of osu!megamix homework archives."""

from pathlib import Path, PurePosixPath, PureWindowsPath
import hashlib
import os
import shutil
import stat
import tempfile
import zipfile

MAX_FILES = 10000
MAX_FILE_SIZE = 256 * 1024 * 1024
MAX_TOTAL_SIZE = 1024 * 1024 * 1024
INTEGRITY_FILENAME = "INTEGRITY"


def _safe_name(name):
    if not name or "\\" in name or "\x00" in name:
        return False
    if PurePosixPath(name).is_absolute():
        return False
    if PureWindowsPath(name).is_absolute():
        return False
    parts = name.rstrip("/").split("/")
    if any(part in ("", ".", "..") for part in parts):
        return False
    if any(":" in part for part in parts):
        return False
    if any(part.endswith((" ", ".")) for part in parts):
        return False
    if any(part.split(".")[0].upper() in {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    } for part in parts):
        return False
    return True


def unpack_homework(archive_file, dest_dir, verify=True):
    archive_file = Path(archive_file)
    dest_dir = Path(dest_dir)

    if dest_dir.exists() or dest_dir.is_symlink():
        raise FileExistsError(
            f"destination already exists: {dest_dir}"
        )

    with zipfile.ZipFile(archive_file, "r") as zf:
        infos = zf.infolist()

        if len(infos) > MAX_FILES:
            raise ValueError("too many archive entries")

        seen = set()
        total_size = 0

        for info in infos:
            name = info.filename

            if not _safe_name(name):
                raise ValueError(f"unsafe archive entry: {name}")

            normalized = name.rstrip("/")
            key = normalized.casefold()

            if key in seen:
                raise ValueError(f"duplicate archive entry: {name}")
            seen.add(key)

            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"symlink not allowed: {name}")

            if info.file_size > MAX_FILE_SIZE:
                raise ValueError(f"oversized archive entry: {name}")

            total_size += info.file_size
            if total_size > MAX_TOTAL_SIZE:
                raise ValueError("archive exceeds size limit")

        if verify and INTEGRITY_FILENAME not in zf.namelist():
            raise ValueError("missing integrity information")

        if verify:
            expected = zf.read(INTEGRITY_FILENAME).decode("utf-8").strip()
            h = hashlib.sha256()

            for info in sorted(infos, key=lambda x: x.filename):
                if info.filename == INTEGRITY_FILENAME or info.is_dir():
                    continue

                with zf.open(info) as source:
                    data = source.read(MAX_FILE_SIZE + 1)

                if len(data) > MAX_FILE_SIZE:
                    raise ValueError("archive entry exceeds size limit")

                h.update(info.filename.encode("utf-8") + b"\0" + data)

            if h.hexdigest() != expected:
                raise ValueError("integrity check failed")

        parent = dest_dir.parent.resolve()
        parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(
            prefix=".homework-",
            dir=parent
        ) as temp:
            staging = Path(temp) / "payload"
            staging.mkdir()

            for info in infos:
                target = staging.joinpath(*info.filename.rstrip("/").split("/"))

                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue

                target.parent.mkdir(parents=True, exist_ok=True)

                with zf.open(info) as source, open(target, "xb") as output:
                    shutil.copyfileobj(source, output)

            if dest_dir.exists() or dest_dir.is_symlink():
                raise FileExistsError("destination appeared during extraction")

            staging.rename(dest_dir)

    return dest_dir
