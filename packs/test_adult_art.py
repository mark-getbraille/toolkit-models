"""A self-test of the nudes and erotic art packs (packs/adult_art_packs.py), with made-up records only: nothing is
downloaded from the internet (the museum and Commons readers are given made-up answers).

It checks that:
  - erotic_art leaves out any artwork whose words name a child or young person (child, boy, girl, teen, school,
    pupil, putto, Cupid, Eros, Ganymede, wakashu, furisode, 若衆 ...) or give an age under 18; adult phrases ("young
    woman", "maiden", "nymph", "youthful") leave out only a Japanese work; harm, animals (Leda, Pasiphae), photographs
    and non-art are left out; works of force, no consent and restraint are kept, said plainly and tagged "theme";
  - answers follow the description guide: no judgement or titillating words;
  - museum_art_nudes takes only what art_nudes leaves out, never a photograph, a sexual act or sexual violence,
    keeps a child only as a sacred or winged figure (Madonna and Child, putti, Cupid, cherubs) in a plainly
    non-sexual work, never a real girl, boy or youth as the nude subject, and marks those rows "child";
  - each item's own licence is checked: The Met isPublicDomain, Cleveland CC0, Wellcome pdm/cc-0/cc-by, Commons
    CC0/public domain/CC BY (never SA, NC or ND, never no licence);
  - every erotic_art row carries "content": "sexual", and crude or catalogue words are put in plain English;
  - both packs are wired: build_packs.PACKS, COMMONS_KEYS (erotic_art), the workflow's known list and limits, the
    kit's sources with content "nudity" and "sexual", NOT_FOR_PICTURE_MAKING and PEOPLE_AND_BODILY_PACK_KEYS, and
    the kit marks an add-on that learned from sexual content as personal use only.

Run it from the repository's folder:   python3 -m pytest packs/test_adult_art.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import adult_art_packs as a  # noqa: E402

REPO = os.path.dirname(HERE)


def test_erotic_minor_words_exclude():
    """Clear minor words, or an age under 18, leave an erotic artwork out; so do adult-sounding "young" phrases in a
    Japanese work (where they often stand for wakashu or musume)."""
    for title in ("Lovers with a child nearby, shunga", "A boy and a woman, erotic print", "Girl and lover, erotic",
                  "Young woman and her lover, shunga", "Young man with a courtesan, ukiyo-e erotic print",
                  "Erotic scene with putti", "Cupid and Venus, erotic", "Eros watching lovers, erotic",
                  "Schoolgirl, erotic", "Erotic print of students", "Erotic print of a pupil",
                  "Wakashu and a woman, shunga", "A courtesan in furisode with a lover, shunga", "Kagema, shunga",
                  "若衆と女 春画", "Erotic scene, she is aged 15", "Erotic scene with a 16-year-old",
                  "Teenage lovers, erotic", "Adolescent couple, erotic", "Infant and erotic couple",
                  "Apprentice courtesan, shunga", "Underage lovers, erotic", "Ganymede, erotic"):
        why = a.erotic_left_out(kind="woodblock print", title=title)
        assert why.startswith("names or may name a young person"), (title, why)


def test_erotic_adult_phrases_kept_in_non_japanese_art():
    """The owner's decision: "young woman", "young man", "young couple", "maiden", "nymph" and "youthful" do not
    leave a (non-Japanese) artwork out."""
    for title in ("Young man and woman making love, erotic engraving", "A young couple, erotic etching",
                  "Erotic scene with a maiden", "Youthful lovers, erotic print", "Nymph and satyr, erotic"):
        assert a.erotic_left_out(kind="engraving", title=title) == "", title


def test_erotic_other_rules_and_kept():
    """Harm, animals, photographs, non-art and off-topic records are left out; adult erotic art is kept, and so are
    works of force, no consent and restraint (with their theme)."""
    out = {"Leda, erotic": "painting", "Pasiphae, erotic": "painting",
           "Dream of the fisherman's wife (octopus), shunga": "print", "Erotic scene": "gelatin silver print",
           "Erotic couple": "photograph", "Erotic catalogue": "", "Landscape with a river": "painting",
           "Shiva linga, erotic": "sculpture", "Erotic scene with a corpse": "print",
           "The rape of Lucretia, her suicide": "engraving", "Europa and the bull": "painting"}
    for title, kind in out.items():
        assert a.erotic_left_out(kind=kind, title=title), title
    kept = {"Lovers, from an album of shunga": "woodblock print; ink and color on paper",
            "Couple engaged in sexual intercourse": "gouache painting",
            "Mithuna couple": "sandstone sculpture relief",
            "A couple making love on a terrace": "opaque watercolor",
            "Kylix with an erotic scene": "terracotta",
            "The Rape of the Sabine Women": "engraving", "The Abduction of Proserpina": "bronze",
            "Erotic scene, the woman asleep": "print", "Couple, erotic, bound with ropes": "print",
            "Tarquin and Lucretia": "oil on canvas", "Europa": "oil on canvas"}
    for title, kind in kept.items():
        assert a.erotic_left_out(kind=kind, title=title) == "", title


def test_themes_are_said_plainly_and_tagged():
    """A work of force, no consent or restraint says so factually and carries its theme in every row."""
    cases = {"The Abduction of Proserpina": (a.THEME_FORCE, "carried her off by force"),
             "The Rape of the Sabine Women": (a.THEME_FORCE, "by force"),
             "Erotic scene: a man forces a woman": (a.THEME_FORCE, "sexual violence, not consent"),
             "Erotic scene, the woman asleep": (a.THEME_NO_CONSENT, "cannot consent"),
             "Susanna and the Elders, erotic": (a.THEME_NO_CONSENT, "spied on"),
             "Couple, erotic, bound with ropes": (a.THEME_RESTRAINT, "restraint")}
    for title, (theme, words) in cases.items():
        rows = a.erotic_rows("credit", title, "print", text="")
        assert all(r["theme"] == theme and r["content"] == "sexual" for r in rows), title
        assert words in rows[0]["answer"], (title, rows[0]["answer"])
        assert "not consent" in rows[1]["answer"] or "consent" in rows[1]["answer"] or "restraint" in rows[1]["answer"]
    plain_rows = a.erotic_rows("credit", "Lovers, shunga", "print")
    assert all("theme" not in r for r in plain_rows)


# Judgement and titillating words the answers never use (the guide's rule), and words that would eroticise force.
JUDGEMENT = __import__("re").compile(r"\b(obscen\w*|lewd\w*|lascivious\w*|lustful|bawdy|sexy|smutty|dirty|filthy|"
                                     r"naughty|pervert\w*|disgusting|shameful|steamy|seductive|tantaliz\w*|"
                                     r"titillat\w*|hot)\b", __import__("re").I)


def test_answers_follow_the_guide():
    """The guide is there; answers turn judgement words into plain ones, and themed answers never eroticise."""
    guide = os.path.join(REPO, "training-kit", "HOW TO DESCRIBE SEXUAL CONTENT, NUDITY AND CONSENT.txt")
    assert os.path.exists(guide)
    for title in ("An obscene print of lovers, erotic", "Lewd scene, erotic", "A lascivious couple, erotic",
                  "Sexy courtesan, erotic", "The Rape of the Sabine Women"):
        for r in a.erotic_rows("credit", title, "print"):
            assert not JUDGEMENT.search(r["answer"]), (title, r["answer"])
    for _, _, said in a.MYTH_FACTS:
        assert not JUDGEMENT.search(said)


def test_minor_word_ages():
    """Ages: under 18 is a minor word, 18 and over is not."""
    assert a.minor_word("a 16-year-old woman")
    assert a.minor_word("aged 17")
    assert a.minor_word("aged 30") == ""
    assert a.minor_word("a 25 year old man") == ""


def test_nudes_screen():
    """museum_art_nudes: only what art_nudes leaves out; no photographs, sex acts, sexual violence, or children with
    sexual or romantic words; children only in plainly non-sexual works, marked."""
    a.CHILD_TITLES.clear()
    kept = [("Madonna and Child", "oil on panel"), ("Venus and Cupid", "oil on canvas"), ("Putti playing", "etching"),
            ("Susanna and the Elders", "oil on canvas"), ("Nymph bathing", "marble"), ("The Kiss", "bronze"),
            ("Virgin and Child with Saint John", "tempera"), ("Venus and Cupid; the child reaches up", "engraving")]
    for title, kind in kept:
        assert a.nudes_left_out("test", title, kind=kind) is False, title
    assert {"Madonna and Child", "Venus and Cupid", "Putti playing"} <= a.CHILD_TITLES
    assert "Susanna and the Elders" not in a.CHILD_TITLES
    dropped = [("Standing female nude", "drawing"),              # art_nudes's already
               ("Nude girl", "gelatin silver print"), ("Female nude in a kiss", "photograph"),
               ("Erotic scene with nymphs", "etching"), ("Shunga", "woodblock print"),
               ("Leda and the Swan", "oil"), ("Aegina Visited by Jupiter", "oil on canvas"), ("The Rape of the Sabine Women", "engraving"),
               ("Ganymede", "marble"), ("Cupid and Psyche kissing", "marble"), ("Bacchanal with putti", "print"),
               ("Young lovers embracing", "drawing"),
               # a real child or young person as the nude subject: never (only sacred or winged child figures)
               ("Study from the Nude of a Girl Standing", "drypoint"), ("Study for the Nude Youth", "red chalk"),
               ("Nude boy bathing", "oil on canvas"), ("Pompeiian design with nude figures; children", "gouache"),
               ("Venus and Cupid with a girl", "engraving")]
    for title, kind in dropped:
        assert a.nudes_left_out("test", title, kind=kind) is True, title


def test_commons_licence_and_item():
    """Commons files: CC0, public domain or CC BY only; problem categories, logos and young-person words left out."""
    for licence in ("CC0", "Public domain", "PD-old", "CC BY 4.0", "CC BY 2.0"):
        assert a.commons_licence_open(licence), licence
    for licence in ("CC BY-SA 4.0", "CC BY-NC 2.0", "CC BY-ND 3.0", "", "GFDL", "Copyrighted"):
        assert not a.commons_licence_open(licence), licence

    def info(licence, description="", categories="Erotic sculptures in India", mime="image/jpeg"):
        """A made-up Commons imageinfo."""
        meta = {"LicenseShortName": {"value": licence}, "ImageDescription": {"value": description},
                "Categories": {"value": categories}, "Artist": {"value": "Someone"}}
        return {"mime": mime, "thumburl": "https://upload.wikimedia.org/x.jpg", "extmetadata": meta}

    good = a.commons_item("File:Khajuraho temple erotic sculpture.jpg",
                          info("CC BY 4.0", "Erotic sculpture on the Kandariya Mahadeva temple, Khajuraho."), "art")
    assert good and all(r["content"] == "sexual" for r in good[2])
    assert "CC BY 4.0" in good[2][0]["credit"]
    assert a.commons_item("File:Khajuraho temple erotic sculpture.jpg", info("CC BY-SA 4.0"), "art") is None
    assert a.commons_item("File:Khajuraho temple erotic sculpture.jpg", info(""), "art") is None
    assert a.commons_item("File:Khajuraho erotic sculpture.jpg",
                          info("CC0", categories="Images with missing permission"), "art") is None
    assert a.commons_item("File:Girl and a man, erotic sculpture.jpg", info("CC0"), "art") is None
    assert a.commons_item("File:Couple on a bed.jpg", info("CC0", categories="Sex positions"), "drawn") is None
    assert a.commons_item("File:Sex position diagram.svg", info("CC0", categories="Sex positions",
                                                                mime="image/svg+xml"), "drawn")


def test_museum_records_licence(monkeypatch):
    """The Met, Cleveland and Wellcome readers keep only items whose own record is open."""
    met = {1: {"isPublicDomain": True, "primaryImage": "https://x/1.jpg", "primaryImageSmall": "https://x/1s.jpg",
               "title": "Lovers, from an album of shunga", "objectName": "Print", "classification": "Prints",
               "medium": "Woodblock print; ink and color on paper", "tags": [{"term": "Erotica"}],
               "artistDisplayName": "Katsukawa Shunchō", "objectDate": "ca. 1785", "objectURL": "https://met/1",
               "culture": "Japan"},
           2: {"isPublicDomain": False, "primaryImage": "https://x/2.jpg", "primaryImageSmall": "https://x/2s.jpg",
               "title": "Lovers, shunga", "objectName": "Print", "medium": "Woodblock print", "tags": []},
           3: {"isPublicDomain": True, "primaryImage": "https://x/3.jpg", "primaryImageSmall": "https://x/3s.jpg",
               "title": "Erotic scene", "objectName": "Photograph", "medium": "Albumen silver print", "tags": []}}

    def fake(s, url, params=None, method="get", body=None, tries=3):
        """Made-up Met answers."""
        if url.endswith("search"):
            return {"objectIDs": [1, 2, 3]}
        return met[int(url.rsplit("/", 1)[-1])]

    monkeypatch.setattr(a, "get_json", fake)
    monkeypatch.setattr(a.time, "sleep", lambda *_: None)
    items = a.met_erotic(10)
    assert [n for n, _, _ in items] == ["met-1.jpg"]
    rows = items[0][2]
    assert rows[0]["answer"].startswith("Lovers, from an album of shunga (Japanese erotic art)")
    assert all(r["content"] == "sexual" for r in rows) and rows[1]["question"] == a.IS_SEXUAL

    cma = {"data": [{"id": 7, "title": "Couple making love", "share_license_status": "CC0", "type": "Painting",
                     "technique": "opaque watercolor", "digital_description": "A couple making love on a terrace.",
                     "images": {"web": {"url": "https://x/7.jpg"}}, "url": "https://cma/7", "culture": ["India"]},
                    {"id": 8, "title": "Couple making love", "share_license_status": "Copyrighted",
                     "type": "Painting", "technique": "oil", "images": {"web": {"url": "https://x/8.jpg"}}}]}
    monkeypatch.setattr(a, "get_json", lambda *x, **k: cma)
    assert [n for n, _, _ in a.cma_erotic(5)] == ["cma-7.jpg"]

    def wellcome(licence, wid):
        """A made-up Wellcome image record."""
        return {"id": wid, "source": {"id": "w" + wid, "title": "A couple engaged in sexual intercourse. Gouache.",
                                      "subjects": [], "genres": [{"label": "Paintings"}]},
                "locations": [{"license": {"id": licence}, "url": "https://iiif.wellcome/" + wid + "/info.json"}]}
    data = {"results": [wellcome("cc-by", "a"), wellcome("cc-by-nc", "b"), wellcome("inc", "c")], "totalPages": 1}
    monkeypatch.setattr(a, "get_json", lambda *x, **k: data)
    assert [n for n, _, _ in a.wellcome_erotic(5)] == ["wellcome-a.jpg"]


def test_plain_words():
    """Crude and catalogue words become plain adult English, once each."""
    assert a.plain("Shunga print: a man fucks a woman; shunga") == \
        "Shunga (Japanese erotic art) print: a man has sex with a woman; shunga"
    assert "oral sex on a penis (fellatio)" in a.plain("fellatio")


def test_wiring():
    """Both packs are in PACKS (erotic_art in COMMONS_KEYS), the workflows know them, the kit lists them with their
    content choice, never for picture-making, and sexual content makes an add-on personal use only."""
    keys = set(a.ADULT_ART_PACKS)
    assert keys <= set(build_packs.PACKS)
    assert "erotic_art" in build_packs.COMMONS_KEYS and "museum_art_nudes" not in build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    for key, limit in a.ADULT_ART_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    import sources
    assert sources.content_of("museum_art_nudes") == "nudity"
    assert sources.content_of("erotic_art") == "sexual"
    assert keys <= set(sources.NOT_FOR_PICTURE_MAKING)
    assert keys <= set(sources.PEOPLE_AND_BODILY_PACK_KEYS)
    chosen = {s.key for s in sources.chosen(with_nudity=True)}
    assert "museum_art_nudes" in chosen and "erotic_art" not in chosen
    assert "erotic_art" in {s.key for s in sources.chosen(with_nudity=True, with_sexual=True)}
    assert "erotic_art" not in {s.key for s in sources.chosen(with_sexual=True)}     # needs nudity too
    import train
    assert train.personal_chosen({"sexual_used": True, "collections": ["erotic_art"]})
    assert train.personal_lines({"sexual_used": True, "collections": ["erotic_art"]})[0] == train.SEXUAL_WARNING
    rows = [{"theme": "sexual violence (artwork)"}, {"theme": ""}, {}]
    assert sources.leave_out_themes(rows, sources.SEXUAL_VIOLENCE_THEMES) == [{"theme": ""}, {}]
    assert sources.leave_out_themes(rows, ()) == rows
    assert a.THEME_FORCE in sources.SEXUAL_VIOLENCE_THEMES and a.THEME_NO_CONSENT in sources.SEXUAL_VIOLENCE_THEMES
