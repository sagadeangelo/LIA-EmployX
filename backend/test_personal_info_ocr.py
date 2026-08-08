from pathlib import Path

import easyocr

from backend.modules.cv.builders.personal_info_builder import PersonalInfoBuilder


IMAGE_PATH = Path("debug_docx_media/image1.png")


def main() -> None:
    print("=" * 60)
    print("PERSONAL INFO OCR TEST")
    print("=" * 60)

    reader = easyocr.Reader(["en", "es"], gpu=False)

    results = reader.readtext(str(IMAGE_PATH))

    ocr_lines = [text.strip() for _, text, confidence in results if text.strip()]

    ocr_text = "\n".join(ocr_lines)

    print("\n--- OCR TEXT ---")
    print(ocr_text)

    builder = PersonalInfoBuilder()
    result = builder.build(ocr_text)

    print("\n--- BUILDER RESULT ---")
    print(result.data)

    print("\n--- CONFIDENCE ---")
    print(result.confidence)

    print("\n--- WARNINGS ---")
    for warning in result.warnings:
        print("-", warning)

    print("\n--- JSON ---")
    print(result.data.model_dump(mode="json"))


if __name__ == "__main__":
    main()