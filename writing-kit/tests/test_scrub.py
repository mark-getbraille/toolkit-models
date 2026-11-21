"""Tests of the privacy scrubbing (kit/scrub.py). Every message, name, address and number here is made up; the
phone numbers use the 555 range and the addresses use example.com."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import scrub  # noqa: E402


def clean(subject, body, known="", writer=""):
    return scrub.clean_message(subject, body, scrub.names_from_headers(known), scrub.names_from_headers(writer))


# ----------------------------------------------------------------- personal details

def test_email_addresses_and_links_are_replaced():
    out = scrub.scrub_details("Write to pat.quill@example.com or see https://example.com/me?id=7 today.")
    assert "example.com" not in out
    assert "[email address]" in out and "[link]" in out


def test_lotus_notes_addresses_are_replaced():
    out = scrub.scrub_details("Send it to Dana Forbe/HOU/ECT@ECT by noon.")
    assert "HOU" not in out and "[email address]" in out


def test_phone_numbers_in_many_forms_are_replaced():
    for number in ["(713) 555-0142", "713-555-0142", "713.555.0142", "+1 713 555 0142", "+44 20 7946 0958",
                   "555-0142", "ext. 4471"]:
        out = scrub.scrub_details(f"Call me at {number} tomorrow.")
        assert "[phone number]" in out, number
        assert not any(ch.isdigit() for ch in out), (number, out)


def test_id_card_and_account_numbers_are_replaced():
    out = scrub.scrub_details("SSN 123-45-6789, card 4111 1111 1111 1111, account number is 99887766, "
                              "order #AB12345.")
    for secret in ["123-45-6789", "4111", "99887766", "AB12345"]:
        assert secret not in out
    assert "[ID number]" in out and "[card number]" in out and "[account number]" in out


def test_dates_of_birth_are_replaced_but_ordinary_dates_stay():
    out = scrub.scrub_details("DOB: 04/12/1971. The meeting is on March 3.")
    assert "1971" not in out and "[date of birth]" in out
    assert "March 3" in out


def test_street_addresses_postcodes_and_ip_addresses_are_replaced():
    out = scrub.scrub_details("Mail it to 1400 Maple Grove Street, Suite 210, Springfield, IL 62704 or "
                              "P.O. Box 77. Server 10.0.0.12 is down.")
    for secret in ["1400", "Maple", "62704", "Box 77", "10.0.0.12"]:
        assert secret not in out
    assert "[street address]" in out and "[postcode]" in out and "[IP address]" in out


def test_long_numbers_are_replaced():
    assert scrub.scrub_details("Deal 4410937 is booked.") == "Deal [number] is booked."


# ----------------------------------------------------------------- names

def test_names_from_headers_greetings_and_signatures_become_placeholders():
    body = ("Hi Quentin,\n\nCould you send me the revised rota for Thursday? Orla Vantreese said it was ready.\n\n"
            "Thanks,\nMarisol\nMarisol Pendergast\nSenior Analyst\n")
    cleaned, why = clean("Rota", body, known="Quentin Ashdown <q.ashdown@example.com>",
                         writer="Marisol Pendergast")
    assert not why
    text = cleaned["body"]
    for name in ["Quentin", "Orla", "Vantreese", "Marisol", "Pendergast", "Senior Analyst"]:
        assert name not in text
    assert text.startswith("Hi [Name],")
    assert text.endswith("Thanks,\n[Your name]")
    assert "[Name 2] said it was ready" in text


def test_the_same_person_keeps_the_same_placeholder():
    names = scrub.NameScrubber(known={"tobias", "renwick"})
    out = names.scrub("Tobias Renwick will come. Ask Tobias first, then Ingrid.", signature=False)
    assert out == "[Name] will come. Ask [Name] first, then [Name 2]."


def test_titles_make_a_name():
    names = scrub.NameScrubber()
    assert names.scrub("Please ask Dr. Okonkwo-Blyth about it.", signature=False) == "Please ask [Name] about it."


def test_unknown_capitalised_words_are_treated_as_names():
    names = scrub.NameScrubber()
    out = names.scrub("I gave the file to Zorbanek yesterday.", signature=False)
    assert "Zorbanek" not in out and "[Name]" in out


def test_ordinary_capitalised_words_and_places_stay():
    names = scrub.NameScrubber()
    text = "Thanks for the update. The Monday meeting in Houston moves to Tuesday."
    assert names.scrub(text, signature=False) == text


def test_ambiguous_names_count_only_where_a_name_fits():
    names = scrub.NameScrubber()
    assert names.scrub("Will you check it? I may be late in May.", signature=False) == \
        "Will you check it? I may be late in May."
    assert "Bill" not in names.scrub("I sent it to Bill on Friday.", signature=False)
    assert "Dawn" not in scrub.NameScrubber().scrub("Dawn has the keys.", signature=False)


def test_a_lone_name_at_the_end_becomes_your_name():
    names = scrub.NameScrubber()
    assert names.scrub("See you at the call then.\nBob").endswith("\n[Your name]")


def test_signature_blocks_and_trailing_contact_details_are_cut():
    names = scrub.NameScrubber(writer={"ferris"})
    out = names.scrub("We will switch half of it next month.\nFerris Quayle\nManager\nWestern Desk\nAcme Power")
    assert out.endswith("next month.\n[Your name]")
    assert "Manager" not in out and "Acme" not in out


def test_lower_case_greeting_names_are_caught():
    names = scrub.NameScrubber()
    assert names.scrub("hey zelda, are we still on?", signature=False).startswith("hey [Name],")


# ----------------------------------------------------------------- the writer's own words

def test_quoted_messages_and_footers_are_cut_off():
    body = ("Sounds good, see you at two.\n\nSent from my iPhone\n\n-----Original Message-----\nFrom: Someone\n"
            "Private earlier text")
    assert scrub.own_words(body) == "Sounds good, see you at two."
    body = "Yes, that works for me.\n\nOn Tue, Jan 4, 2000 at 9:15 AM Pell Ruark wrote:\n> old text"
    assert scrub.own_words(body) == "Yes, that works for me."
    assert "old" not in scrub.own_words("New text here.\n> old quoted line\nMore new text.")


def test_wrapped_lines_are_joined_back():
    body = ("I looked at the figures you sent this morning and I think\nwe are close to done with the report.\n\n"
            "Thanks,\nKip")
    assert scrub.own_words(body).startswith("I looked at the figures you sent this morning and I think we are")


# ----------------------------------------------------------------- sensitive messages are dropped

def test_sensitive_messages_are_dropped():
    examples = {
        "health or medical": "I can't come in, I have a doctor's appointment about my surgery next week.",
        "family or personal life": "My wife and I are going through a divorce, so I need Friday off.",
        "money trouble": "I am behind on my mortgage and cannot afford the payment this month.",
        "HR, jobs or discipline": "Her performance review went badly and HR wants a written warning on file.",
        "sexual content": "That party was full of sexy people, let me tell you about it.",
        "children": "Can you pick up the kids from school at three?",
        "passwords, confidential or legal": "My password is tulip42, keep it confidential.",
        "crime or police": "The police called about the stolen van.",
        "gambling, drinking or partying": "I put a bet on the game and got drunk after.",
        "swearing or insults": "That vendor is a bunch of idiots, damn it.",
        "personal banking": "Move $500 from our checking account to the credit card.",
    }
    for subject, text in examples.items():
        cleaned, why = clean("Hello there", text + " Let me know what you think about it soon.")
        assert cleaned is None and why == "sensitive: " + subject, (subject, why)


def test_a_sensitive_subject_line_drops_the_message():
    cleaned, why = clean("Funeral arrangements", "Please let me know when you can talk about the plans for Monday.")
    assert cleaned is None and why.startswith("sensitive")


# ----------------------------------------------------------------- quality

def test_too_short_too_long_and_automatic_messages_are_dropped():
    assert scrub.quality_reason("Ok thanks.") == "too short"
    assert scrub.quality_reason("Word and more words here. " * 60) == "too long"
    assert scrub.quality_reason("Our newsletter is out. Click here to read it, or unsubscribe at any time from "
                                "this list.") == "automatic message or newsletter"


def test_number_tables_and_lists_are_dropped():
    assert scrub.quality_reason("Here are the volumes for the whole week you asked me about: 1200 3400 5600 7800 9100 "
                                "2300 4500 6700 8900 1000 2000 3000.") == "mostly numbers"
    table = "Site\t\tVolume\nAlpha\t\tlow\nBeta\t\thigh\nThe rest of the table is in the file you have now."
    assert scrub.quality_reason(table) == "looks like a table"


def test_careless_capital_letters_are_dropped():
    assert scrub.quality_reason("yeah i saw it. we can go later if you want. let me know what you think.") == \
        "careless capital letters"


def test_a_good_workaday_message_is_kept_whole():
    body = ("Hi Tamsin,\n\nThanks for sending the agenda so quickly. Could we move the review to Wednesday at 10? "
            "Tuesday is packed for me.\n\nBest,\nOskar")
    cleaned, why = clean("Re: Review agenda", body, known="Tamsin Holloway", writer="Oskar Lindqvist")
    assert why == ""
    assert cleaned["subject"] == "Review agenda"
    assert cleaned["body"] == ("Hi [Name],\n\nThanks for sending the agenda so quickly. Could we move the review "
                               "to Wednesday at 10? Tuesday is packed for me.\n\nBest,\n[Your name]")


def test_a_message_full_of_personal_details_is_dropped():
    body = ("Hi Bo, call me at (713) 555-0142 or 713-555-0199, email me at bo@example.com or my other "
            "address jo@example.com, I'm at 12 Elm Street, TX 77002, fax 713-555-0100, account number 77665544.")
    cleaned, why = clean("Contact", body)
    assert cleaned is None and why == "quality: too many removed details"
