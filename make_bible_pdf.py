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

# Read Auth Key
with open('key.txt') as f:
    key = f.readlines()[0].strip()

# Function to Download Passage
def download_chapter(book, c1):
    url = "https://api.esv.org/v3/passage/text/?q=" + book + "+" + str(c1)
    headers = {"Authorization": key}
    params = {"include-footnotes" : "false",
              "include-passage-references" : "false",
              "include-headings": "false"}
    
    # Pull from API
    r = requests.get(url, headers=headers, params=params)
    passage = r.json()["passages"][0]
    
    return passage

# A text class
#class BibleText:
#
#    def __init__(self, text):
#        self.text = text
#        ends = self.findPassageEnds()
#        for end in ends:
#            title = self.findTitle(end)
#
#    def findPassageEnds(self):
#        pattern = re.compile(r"\n[ \t]*\n")
#        m = re.finditer(pattern, self.text)
#        return m
#    
#    def findTitle(self, end):
#        span = end.span()
#        truncated_text = self.text[span[1]:]
#        next_break = re.search(r"\n", truncated_text)
#        IPython.embed();exit(1)

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
            #output.append(Math(data=[r"^{verse} "], inline=True))

            # Truncate text
            text = text[end:]
        else:
            output.append(text)
            text = ""

    return output


book = "Mark"
chapter = 1
geometry_options = {
    "tmargin": "1cm", "lmargin": "1cm", 
    "rmargin": "6cm", "bmargin": "5cm"
    }
doc = Document(
    book, 
    documentclass="article", 
    geometry_options=geometry_options,
    font_size="large"
    )

# Packages
#doc.packages.append(Package(name='extsizes', options="12pt"))
doc.packages.append(Package(name='helvet', options='scaled'))
doc.packages.append(Package(name='setspace'))
doc.packages.append(Package(name="titlesec"))
doc.packages.append(Package(name='hyperref', options="bookmarks"))
#doc.packages.append(Package(name='bookmark', options="depth=4"))

# Preambles
doc.preamble.append(NoEscape(r"\renewcommand\familydefault{\sfdefault}"))
doc.preamble.append(NoEscape(r"\setstretch{1.5}"))
doc.preamble.append(NoEscape(r"\titleformat*{\section}{\Huge\bfseries}"))
doc.preamble.append(NoEscape(r"\hypersetup{pdftex,colorlinks=true,allcolors=blue}"))
#\hypersetup{pdftex,colorlinks=true,allcolors=blue}
#doc.preamble.append(Command("tableofcontents"))

 
prev_text = ""
while True:

    # Process text
    text = download_chapter(book, chapter)
    output = process_text(text)

    if text == prev_text:
        break
    if chapter > 2:
        print("Triggered")
        break

    if chapter > 1:
        doc.append(NewPage())

    chapter_name = book + " " + str(chapter)
    with doc.create(Section(chapter_name, numbering=False)):
        print(f"Processing {book} {chapter}...")
        doc.append(NoEscape(r"\bigskip"))
        for o in output:
            doc.append(o)

    prev_text = text
    chapter += 1

doc.generate_pdf(clean_tex=False)