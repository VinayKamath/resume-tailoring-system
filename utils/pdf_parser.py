from io import BytesIO
from pathlib import Path
import re

from pypdf import PdfReader


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[^\S\r\n]+", " ", text)   # collapse extra spaces
    text = re.sub(r"\n{3,}", "\n\n", text)    # limit blank lines
    text = "\n".join(line.strip() for line in text.splitlines())
    text = "\n".join(line for line in text.splitlines() if line)
    return text.strip()


def extract_text_from_pdf(pdf_file):
    try:
        if isinstance(pdf_file, (str, Path)):
            reader = PdfReader(str(pdf_file))
        else:
            reader = PdfReader(BytesIO(pdf_file))

        pages_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

        combined_text = "\n".join(pages_text)
        return clean_text(combined_text)

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""