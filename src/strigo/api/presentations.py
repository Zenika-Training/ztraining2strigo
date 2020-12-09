# coding: utf8
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from ..client import Client
from ..models.presentations import Note, Presentation

MAX_FILESIZE = 10485500


def _can_upload(p: Path, class_id: str) -> bool:
    if p.stat().st_size > MAX_FILESIZE:
        print(
            'Presentation file is bigger than authorized size through the API',
            f"Please add it through the WebUI https://app.strigo.io/classes/{class_id}",
            sep='\n',
            file=sys.stderr
        )
        return False
    else:
        return True


def list(client: Client, class_id: str) -> List[Presentation]:
    return client.get(f"/classes/{class_id}/presentations", Presentation)


def get(client: Client, class_id: str, presentation_id: str) -> Presentation:
    return client.get(f"/classes/{class_id}/presentations/{presentation_id}", Presentation)


def create(client: Client, class_id: str, presentation: Path) -> Presentation:
    if _can_upload(presentation, class_id):
        data = {'presentation': presentation}
        return client.upload(f"/classes/{class_id}/presentations", data, Presentation)
    else:
        return None


def delete(client: Client, class_id: str, presentation_id: str) -> None:
    client.delete(f"/classes/{class_id}/presentations/{presentation_id}")


def update(client: Client, class_id: str, presentation_id: str, presentation: Path) -> Presentation:
    if _can_upload(presentation, class_id):
        delete(client, class_id, presentation_id)
        create(client, class_id, presentation)
    else:
        return None


def get_notes(client: Client, class_id: str, presentation_id: str) -> List[Note]:
    return client.get(f"/classes/{class_id}/presentations/{presentation_id}/notes", Note)


def create_notes(client: Client, class_id: str, presentation_id: str, notes: List[Note]) -> List[Note]:
    data = {'notes': [n.to_dict() for n in notes]}
    return client.post(f"/classes/{class_id}/presentations/{presentation_id}/notes", data, Note)


def delete_notes(client: Client, class_id: str, presentation_id: str) -> None:
    client.delete(f"/classes/{class_id}/presentations/{presentation_id}/notes")
