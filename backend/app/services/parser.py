import io, requests
from bs4 import BeautifulSoup
import PyPDF2
from docx import Document
import logging

logger = logging.getLogger(__name__)
_H = {"User-Agent": "Mozilla/5.0 (compatible; TermShieldBot/1.0)"}

def parse_pdf(data: bytes) -> str:
    try:
        r = PyPDF2.PdfReader(io.BytesIO(data))
        return clean_text("\n".join(p.extract_text() or "" for p in r.pages))
    except Exception as e: raise ValueError(f"PDF parse failed: {e}")

def parse_docx(data: bytes) -> str:
    try:
        doc = Document(io.BytesIO(data))
        return clean_text("\n".join(p.text for p in doc.paragraphs if p.text.strip()))
    except Exception as e: raise ValueError(f"DOCX parse failed: {e}")

def parse_url(url: str) -> str:
    try:
        r = requests.get(url, headers=_H, timeout=20); r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for t in soup(["script","style","nav","footer","header","aside","form"]): t.decompose()
        main = soup.find("main") or soup.find("article") or soup.find("body")
        return clean_text((main or soup).get_text("\n", strip=True))
    except Exception as e: raise ValueError(f"URL scrape failed: {e}")

def clean_text(text: str) -> str:
    return "\n".join(ln.strip() for ln in text.splitlines() if ln.strip())
