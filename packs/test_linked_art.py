"""A self-test of the Linked Art reader (packs/linked_art.py) and of the Getty Museum source in adult_art_packs.py,
with made-up JSON-LD records only: nothing is downloaded from the internet.

It checks that the reader finds the title, statements, types, maker, date and materials of a record; that rights
are open ONLY when the image's own Right names CC0 or the Public Domain Mark (a CC0 statement for the METADATA of the
object does not make its picture open); that the IIIF image service is found; and that Getty objects go to the right
pack under the existing rules (a nude drawing to museum_art_nudes, a nude photograph to nude_photo_studies, an
erotic print to erotic_art, a work with a closed image nowhere).

Run it from the repository's folder:   python3 -m pytest packs/test_linked_art.py
"""

import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import adult_art_packs as a  # noqa: E402
import linked_art as la  # noqa: E402

AAT = "http://vocab.getty.edu/aat/"
OBJECT = {
    "@context": "https://linked.art/ns/v1/linked-art.json",
    "id": "https://data.getty.edu/museum/collection/object/abc-1", "type": "HumanMadeObject",
    "_label": "Study of a Male Nude",
    "classified_as": [{"id": AAT + "300133025", "type": "Type", "_label": "Artwork"},
                      {"id": AAT + "300033973", "type": "Type", "_label": "Drawings"}],
    "identified_by": [{"type": "Identifier", "content": "85.GB.224"},
                      {"type": "Name", "content": "Study of a Male Nude",
                       "classified_as": [{"id": AAT + "300404670", "type": "Type", "_label": "Primary Title"}]}],
    "referred_to_by": [
        {"type": "LinguisticObject", "content": "A standing man, seen from the front, his weight on one leg.",
         "classified_as": [{"id": AAT + "300080091", "_label": "Description"}, {"id": AAT + "300418049",
                                                                               "_label": "Brief Text"}]},
        {"type": "LinguisticObject", "content": "Red chalk", "classified_as": [{"id": AAT + "300435429",
                                                                               "_label": "Materials Statement"}]},
        {"type": "LinguisticObject", "content": "French", "classified_as": [{"id": AAT + "300055768",
                                                                            "_label": "Culture"}]}],
    "produced_by": {"type": "Production", "carried_out_by": [{"type": "Person", "_label": "Jean Dupont"}],
                    "timespan": {"type": "TimeSpan", "identified_by": [{"type": "Name", "content": "about 1760"}]}},
    "subject_to": [{"type": "Right", "_label": "License for Collection Metadata",
                    "classified_as": [{"id": "http://creativecommons.org/publicdomain/zero/1.0/", "type": "Type"}]}],
    "shows": [{"id": "https://data.getty.edu/media/image/img-1", "type": "VisualItem"}],
    "subject_of": [{"id": "https://www.getty.edu/art/collection/object/103QYT", "type": "LinguisticObject"}],
}
VISUAL = {
    "id": "https://data.getty.edu/media/image/img-1", "type": "VisualItem",
    "digitally_shown_by": [{"type": "DigitalObject", "access_point": [
        {"id": "https://media.getty.edu/iiif/image/f991"},
        {"id": "https://media.getty.edu/iiif/image/f991/full/max/0/default.jpg"}]}],
    "subject_to": [{"id": "https://data.getty.edu/media/image/img-1/rights", "type": "Right", "classified_as": [
        {"type": "Type", "id": "http://creativecommons.org/publicdomain/zero/1.0/",
         "_label": "Creative Commons Public Domain Dedication"}]}],
}


def test_plain_fields():
    f = la.plain_fields(OBJECT)
    assert f == {"title": "Study of a Male Nude", "kind": "Drawings", "artist": "Jean Dupont", "date": "about 1760",
                 "medium": "Red chalk", "text": "A standing man, seen from the front, his weight on one leg.",
                 "place": "French"}
    assert la.types(OBJECT) == ["Drawings"]


def test_rights_only_from_the_image_record():
    assert la.rights_of(VISUAL) == "CC0"
    mark = copy.deepcopy(VISUAL)
    mark["subject_to"][0]["classified_as"][0]["id"] = "https://creativecommons.org/publicdomain/mark/1.0/"
    assert la.rights_of(mark) == "Public Domain Mark"
    closed = copy.deepcopy(VISUAL)
    closed["subject_to"][0]["classified_as"][0]["id"] = "http://rightsstatements.org/vocab/InC/1.0/"
    assert la.rights_of(closed) == ""
    assert la.rights_of({"id": "x", "type": "VisualItem"}) == ""
    # A CC0 type outside a Right (a description that mentions it) does not count.
    loose = {"id": "x", "classified_as": [{"id": "http://creativecommons.org/publicdomain/zero/1.0/"}]}
    assert la.rights_of(loose) == ""


def test_iiif_service():
    assert la.iiif_service(VISUAL) == "https://media.getty.edu/iiif/image/f991"
    assert la.image_url("https://media.getty.edu/iiif/image/f991") == \
        "https://media.getty.edu/iiif/image/f991/full/!1600,1600/0/default.jpg"
    only_full = {"digitally_shown_by": [{"access_point": [{"id": "https://x.org/iiif/2/abc/full/max/0/default.jpg"}]}]}
    assert la.iiif_service(only_full) == "https://x.org/iiif/2/abc"


class FakeSession:
    """Answers made-up records by address."""

    def __init__(self, records):
        """records: {address: JSON}."""
        self.records = records

    def get(self, url, **_):
        """The record, or a 404."""
        data = self.records.get(url)
        return type("R", (), {"status_code": 200 if data else 404, "json": lambda self, d=data: d})()


def variant(oid, title, kind="Drawings", open_image=True, medium="Red chalk", text=""):
    """A made-up object and its image record."""
    obj, vis = copy.deepcopy(OBJECT), copy.deepcopy(VISUAL)
    obj["id"] = f"https://data.getty.edu/museum/collection/object/{oid}"
    obj["identified_by"][1]["content"] = title
    obj["classified_as"][1]["_label"] = kind
    obj["referred_to_by"][0]["content"] = text or title
    obj["referred_to_by"][1]["content"] = medium
    obj["shows"][0]["id"] = vis["id"] = f"https://data.getty.edu/media/image/{oid}"
    if not open_image:
        vis["subject_to"][0]["classified_as"][0]["id"] = "http://rightsstatements.org/vocab/InC/1.0/"
    return {obj["id"]: obj, vis["id"]: vis}


def test_getty_record_and_routing(monkeypatch):
    records = {}
    for oid, title, kind, open_image, medium in (
            ("o1", "Study of a Male Nude", "Drawings", True, "Red chalk"),
            ("o2", "Nude woman seated in the studio. Photograph.", "Photographs", True, "Gelatin silver print"),
            ("o3", "Lovers, from an erotic album (shunga)", "Prints", True, "Woodblock print"),
            ("o4", "Reclining Nude", "Paintings", False, "Oil on canvas"),
            ("o5", "Nude girl bathing", "Paintings", True, "Oil on canvas")):
        records.update(variant(oid, title, kind, open_image, medium))
    session = FakeSession(records)
    monkeypatch.setattr(la, "PAUSE", 0)
    monkeypatch.setattr(a, "session", lambda: session)
    uris = [u for u in records if "/object/" in u]
    monkeypatch.setattr(la, "getty_objects", lambda s, pattern, limit=2000: list(uris))
    a.GETTY_SEEN.clear()
    record, picture, rights = la.getty_record(session, uris[0])
    assert rights == "CC0" and picture.endswith("/full/!1600,1600/0/default.jpg")
    nudes = {n for n, _, _ in a.getty_items(10, "nudes")}
    photos = {n for n, _, _ in a.getty_items(10, "photos")}
    erotic = a.getty_items(10, "erotic")
    assert nudes == {"getty-o1.jpg"}                        # not the photograph, the closed image or the child
    assert photos == {"getty-o2.jpg"}
    assert [n for n, _, _ in erotic] == ["getty-o3.jpg"]
    assert all(r["content"] == "sexual" for r in erotic[0][2])
    assert ": a print by Jean Dupont, about 1760" in erotic[0][2][0]["answer"]   # "Prints" said as one kind
    assert "getty.edu/art/collection/object/103QYT" in erotic[0][2][0]["credit"]
