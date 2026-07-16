"""
===============================================================
LIA EmployX

Base Reader

Clase base para todos los lectores de documentos.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from backend.modules.cv.engine.document_content import DocumentContent


class BaseReader(ABC):
    """
    Clase base para todos los Readers.

    Todos los lectores deben devolver un DocumentContent.
    """

    # ---------------------------------------------------------

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """
        Lista de extensiones soportadas.
        """
        pass

    # ---------------------------------------------------------

    def can_read(self, file_path) -> bool:
        """
        Indica si este Reader puede leer el archivo.
        """

        extension = Path(file_path).suffix.lower()

        return extension in self.supported_extensions

    # ---------------------------------------------------------

    @abstractmethod
    def read(self, file_path) -> DocumentContent:
        """
        Lee un archivo y devuelve un DocumentContent.
        """
        pass

    # ---------------------------------------------------------

    def validate(self, file_path):

        file_path = Path(file_path)

        if not file_path.exists():

            raise FileNotFoundError(file_path)

        if not self.can_read(file_path):

            raise ValueError(

                f"{self.__class__.__name__} "

                f"no soporta archivos "

                f"{file_path.suffix}"

            )

    # ---------------------------------------------------------

    def create_document(self, file_path):

        """
        Crea un DocumentContent con los datos básicos.
        """

        return DocumentContent.from_file(file_path)

    # ---------------------------------------------------------

    def __repr__(self):

        return (

            f"{self.__class__.__name__}"

            f"(extensions={self.supported_extensions})"

        )