"""
===============================================================
LIA EmployX

Prompt Manager

Carga y administra los prompts del sistema.

Autor:
LIA EmployX Team
===============================================================
"""

from __future__ import annotations

from pathlib import Path

from backend.ai.config import PROMPTS_DIR


class PromptManager:

    """
    Administrador de prompts.
    """

    def __init__(self):

        self.root = Path(PROMPTS_DIR)

    # ----------------------------------------------------------

    def load(

        self,

        category: str,

        prompt_name: str

    ) -> str:

        """
        Carga un prompt desde disco.

        Ejemplo

        load("cv","extract_profile")
        """

        file = (

            self.root

            / category

            / f"{prompt_name}.md"

        )

        if not file.exists():

            raise FileNotFoundError(

                f"No existe el prompt:\n{file}"

            )

        return file.read_text(

            encoding="utf-8"

        )

    # ----------------------------------------------------------

    def exists(

        self,

        category,

        prompt_name

    ):

        file = (

            self.root

            / category

            / f"{prompt_name}.md"

        )

        return file.exists()

    # ----------------------------------------------------------

    def save(

        self,

        category,

        prompt_name,

        content

    ):

        folder = self.root / category

        folder.mkdir(

            parents=True,

            exist_ok=True

        )

        file = folder / f"{prompt_name}.md"

        file.write_text(

            content,

            encoding="utf-8"

        )

    # ----------------------------------------------------------

    def list_categories(self):

        categories = []

        for folder in self.root.iterdir():

            if folder.is_dir():

                categories.append(folder.name)

        return sorted(categories)

    # ----------------------------------------------------------

    def list_prompts(

        self,

        category

    ):

        folder = self.root / category

        if not folder.exists():

            return []

        prompts = []

        for file in folder.glob("*.md"):

            prompts.append(file.stem)

        return sorted(prompts)

    # ----------------------------------------------------------

    def info(self):

        return {

            "root": str(self.root),

            "categories": self.list_categories()

        }


if __name__ == "__main__":

    manager = PromptManager()

    print(manager.info())