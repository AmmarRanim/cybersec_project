"""
PDF Reader Utility — Extracts text from PDF files.

Usage:
    python pdf_reader.py <path_to_pdf>
    python pdf_reader.py <path_to_pdf> --start 5 --end 10   # pages 5-10 only
"""

import sys
import argparse

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed. Run: pip install pymupdf")
    sys.exit(1)


def read_pdf(path: str, start_page: int = 0, end_page: int = None) -> str:
    """Extract text from a PDF file."""
    doc = fitz.open(path)
    total = len(doc)
    end = min(end_page or total, total)
    text = ""
    for i in range(start_page, end):
        text += f"\n--- Page {i+1}/{total} ---\n"
        text += doc[i].get_text()
    doc.close()
    return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from PDF")
    parser.add_argument("path", help="Path to PDF file")
    parser.add_argument("--start", type=int, default=0, help="Start page (0-indexed)")
    parser.add_argument("--end", type=int, default=None, help="End page (exclusive)")
    args = parser.parse_args()

    text = read_pdf(args.path, args.start, args.end)
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)
