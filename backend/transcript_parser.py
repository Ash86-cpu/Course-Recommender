"""Pull the list of completed courses out of a transcript.

Transcripts come in many layouts, so this is a heuristic: any line that starts
with something shaped like a course code (two to five letters, then three or
four digits, e.g. "CS101", "ECMM 422") is treated as a course, and the words
after the code, up to the first number or grade-like token, are its title.
"""

import io
import re
from typing import Dict, List

import pdfplumber

COURSE_LINE = re.compile(
    r"^\s*(?P<code>[A-Z]{2,5}\s?\d{3,4}[A-Z]?)"   # course code
    r"[\s:\-\u2013]+"                              # separator
    r"(?P<title>[A-Za-z][A-Za-z&,'()/ \-]*?)"      # title
    r"(?=\s+[\dA-F][\d.+%]*\b|\s*$)"               # stop at a number, a grade, or line end
)


def extract_text(data: bytes, filename: str) -> str:
    """Return the text of a PDF or plain-text transcript, read from memory."""
    if filename.lower().endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    return data.decode("utf-8", errors="replace")


def parse_courses(text: str) -> List[Dict[str, str]]:
    """Find course codes and titles in transcript text. Duplicates are dropped."""
    courses, seen = [], set()
    for line in text.splitlines():
        match = COURSE_LINE.match(line)
        if not match:
            continue
        code = match["code"].replace(" ", "").upper()
        title = " ".join(match["title"].split()).strip(" -:,")
        if code not in seen and len(title) >= 3:
            seen.add(code)
            courses.append({"code": code, "title": title})
    return courses
