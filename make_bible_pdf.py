import requests
from pylatex import Document, Section, Subsection, Command, Package
from pylatex.section import Chapter
from pylatex.utils import italic, NoEscape
from pylatex.basic import NewPage, MediumText, SmallText, LargeText, HugeText
from pylatex.math import Math
import pandas as pd
import re
import IPython
from pdb import set_trace
import time

BOOKS = {
    "01": "Genesis",
    "02": "Exodus",
    "03": "Leviticus",
    "04": "Numbers",
    "05": "Deuteronomy",
    "06": "Joshua",
    "07": "Judges",
    "08": "Ruth",
    "09": "1 Samuel",
    "10": "2 Samuel",
    "11": "1 Kings",
    "12": "2 Kings",
    "13": "1 Chronicles",
    "14": "2 Chronicles",
    "15": "Ezra",
    "16": "Nehemiah",
    "17": "Esther",
    "18": "Job",
    "19": "Psalms",
    "20": "Proverbs",
    "21": "Ecclesiastes",
    "22": "Song of Solomon",
    "23": "Isaiah",
    "24": "Jeremiah",
    "25": "Lamentations",
    "26": "Ezekiel",
    "27": "Daniel",
    "28": "Hosea",
    "29": "Joel",
    "30": "Amos",
    "31": "Obadiah",
    "32": "Jonah",
    "33": "Micah",
    "34": "Nahum",
    "35": "Habakkuk",
    "36": "Zephaniah",
    "37": "Haggai",
    "38": "Zechariah",
    "39": "Malachi",
    "40": "Matthew",
    "41": "Mark",
    "42": "Luke",
    "43": "John",
    "44": "Acts",
    "45": "Romans",
    "46": "1 Corinthians",
    "47": "2 Corinthians",
    "48": "Galatians",
    "49": "Ephesians",
    "50": "Philippians",
    "51": "Colossians",
    "52": "1 Thessalonians",
    "53": "2 Thessalonians",
    "54": "1 Timothy",
    "55": "2 Timothy",
    "56": "Titus",
    "57": "Philemon",
    "58": "Hebrews",
    "59": "James",
    "60": "1 Peter",
    "61": "2 Peter",
    "62": "1 John",
    "63": "2 John",
    "64": "3 John",
    "65": "Jude",
    "66": "Revelations",
}

SINGLE_CHAPTER_BOOKS = ["Obadiah", "Philemon", "2 John", "3 John", "Jude"]

# Read Auth Key
with open("key.txt") as f:
    key = f.readlines()[0].strip()


def download_book(book, single_chapter: bool = False):
    """Download a whole book"""
    chapter = 1
    prev_text = ""
    results = {}
    while True:
        if not single_chapter:
            text = download_chapter(book, chapter)
        else:
            text = download_chapter(book)
            return {1: text}

        if text == prev_text:
            break

        print(f"Processing {book} {chapter}...")
        results[chapter] = text
        prev_text = text
        chapter += 1
        time.sleep(5)
    return results


# Function to Download Passage
def download_chapter(book, c1=None):
    url = "https://api.esv.org/v3/passage/text/?q=" + book
    if not c1 is None:
        url += f"+{c1}"

    headers = {"Authorization": key}
    params = {
        "include-footnotes": "false",
        "include-passage-references": "false",
        "include-headings": "true",
    }

    # Pull from API
    try:
        r = requests.get(url, headers=headers, params=params)
        passage = r.json()["passages"][0]
    except Exception as e:
        print(e)
        raise
    return passage


def process_text(text):
    def replace_verse(m):
        verse = m.group(1)
        return Math(data=[verse], inline=True)

    output = []
    pattern = re.compile(r"\[([0-9]+)\]")
    while len(text) > 0:
        m = re.search(pattern, text)
        if not m is None:
            start = m.span()[0]
            end = m.span()[1]
            verse = m.group(1)

            # Append preceding content
            output.append(text[:start])
            output.append(NoEscape(f"$^{{{verse}}}\ $"))

            # Truncate text
            text = text[end:]
        else:
            output.append(text)
            text = ""

    return output


def make_book(number, book, single_chapter=False):
    chapter = 1
    geometry_options = {
        "tmargin": "1cm",
        "lmargin": "1cm",
        "rmargin": "6cm",
        "bmargin": "5cm",
    }
    doc = Document(
        book,
        documentclass="article",
        geometry_options=geometry_options,
        font_size="large",
    )

    # Packages
    doc.packages.append(Package(name="helvet", options="scaled"))
    doc.packages.append(Package(name="setspace"))
    doc.packages.append(Package(name="titlesec"))
    doc.packages.append(Package(name="hyperref"))
    doc.packages.append(Package(name="bookmark"))

    # Preambles
    doc.preamble.append(NoEscape(r"\renewcommand\familydefault{\sfdefault}"))
    doc.preamble.append(NoEscape(r"\setstretch{1.5}"))
    doc.preamble.append(NoEscape(r"\titleformat*{\section}{\Huge\bfseries}"))
    doc.preamble.append(NoEscape(r"\setcounter{secnumdepth}{0}"))

    prev_text = ""
    while True:
        # Process text
        if not single_chapter:
            text = download_chapter(book, chapter)
        else:
            text = download_chapter(book)

        output = process_text(text)

        if text == prev_text:
            break

        if chapter > 1:
            doc.append(NewPage())

        chapter_name = book + " " + str(chapter)
        with doc.create(Section(chapter_name, numbering=True)):
            print(f"Processing {book} {chapter}...")
            doc.append(NoEscape(r"\bigskip"))
            for o in output:
                doc.append(o)

        prev_text = text
        chapter += 1
        time.sleep(5)

        if single_chapter:
            break

    doc.generate_pdf(f"outputs/{number}-{book}", clean_tex=False)


if __name__ == "__main__":
    for number, book in BOOKS.items():
        if book != "1 Timothy":
            continue
        results = download_book(book, single_chapter=False)
        for chapter, text in results.items():
            name = book if len(results) == 1 else f"{book}-{chapter}"
            with open(f"raw/{name}.txt", "w") as f:
                f.write(text)
            set_trace()
