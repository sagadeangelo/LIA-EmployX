from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile


class FileStorage:
    """
    Generic storage service.

    Responsible only for:

    - Creating upload folders
    - Saving uploaded files
    - Deleting files
    - Returning file paths

    It DOES NOT know anything about CVs.
    """

    def __init__(self, root_folder: str = "backend/storage/uploads") -> None:
        self.root = Path(root_folder)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, file: UploadFile) -> Path:
        """
        Save an uploaded file using a unique filename.
        """

        extension = Path(file.filename).suffix.lower()

        filename = f"{uuid.uuid4().hex}{extension}"

        destination = self.root / filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return destination

    def delete(self, path: Path) -> None:
        """
        Delete a stored file.
        """

        if path.exists():
            path.unlink()

    def exists(self, path: Path) -> bool:
        """
        Check if a file exists.
        """

        return path.exists()

    def get_size(self, path: Path) -> int:
        """
        Return file size in bytes.
        """

        return path.stat().st_size

    def absolute_path(self, path: Path) -> Path:
        """
        Return absolute path.
        """

        return path.resolve()