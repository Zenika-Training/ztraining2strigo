# -*- coding: utf-8 -*-

import json
import re
from pathlib import Path
from typing import List

from strigo.api.presentations import Note

SLIDE_SEP_RE = re.compile(r'\r?\n\r?\n\r?\n\r?\n')
NOTES_SEP_RE = re.compile(r'\r?\nNotes : *\r?\n')


def parse_notes(notes_source: Path) -> List[Note]:

    if not notes_source.exists():
        raise Exception(f"Notes source file '{notes_source.absolute()}' does not exists'")

    with notes_source.open() as f:
        slides_list = json.load(f)

    notes = []
    page = 1
    for slides_file in slides_list:
        slides_file: Path = notes_source.parent / slides_file
        if not slides_file.exists():
            raise Exception(f"Slide file '${slides_file.absolute()}' does not exists'")

        with slides_file.open() as f:
            slides = f.read()
        for slide in SLIDE_SEP_RE.split(slides.strip()):
            if re.search(NOTES_SEP_RE, slide):
                note = re.split(NOTES_SEP_RE, slide)[1].strip()
                if note:
                    notes.append(Note(page, note))
            page += 1

    return notes
