import io
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from docx import Document


def load_from_url(url):
    res = requests.get(url, timeout=15)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)


def load_text(text):
    return text.strip() if text else ""


def load_from_file(file):
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file.file.read()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(file.file.read()))
        return "\n".join(p.text for p in doc.paragraphs)

    elif filename.endswith(".txt"):
        return file.file.read().decode("utf-8")

    else:
        return None
