"""Tests of the rule-made instructions (kit/instructions.py). Every message here is made up."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import instructions  # noqa: E402


def kind(text, subject="", reply=False):
    return instructions.classify_kind(subject, text, reply)


def test_kinds_are_found_from_the_words():
    assert kind("Thanks so much for covering my shift on Friday, it really helped.") == "thank-you note"
    assert kind("Could you send me the updated price list by Monday?") == "request"
    assert kind("Unfortunately I won't be able to make the planning session tomorrow.") == "declining"
    assert kind("Sorry for the late reply, I was out all week.") == "apology"
    assert kind("Just following up on the quote I sent last week. Any update?") == "follow-up"
    assert kind("Can we set up a meeting next week? Does Tuesday work for you?") == "scheduling"
    assert kind("Please note the office will be closed on Monday for the holiday.") == "announcement"
    assert kind("I am disappointed that the order still hasn't arrived after three weeks.") == "complaint"
    assert kind("Sounds good, I will confirm the room.") == "confirmation"
    assert kind("We would love for you to join us at the open day.") == "invitation"
    assert kind("The new figures are in the shared folder.", reply=True) == "reply"
    assert kind("The new figures are in the shared folder.") == "update"


def test_person_is_swapped_for_the_instruction():
    assert instructions.swap_person("send me your notes") == "send you their notes"
    assert instructions.swap_person("answer any you know the answers to") == "answer any they know the answers to"


def test_the_main_point_is_taken_from_the_message():
    assert instructions.main_point("request", "Hi,\nCould you please send me the signed form?") == \
        " asking them to send you the signed form"
    assert instructions.main_point("thank-you note", "Thanks for the lovely flowers!") == \
        " thanking them for the lovely flowers"
    assert instructions.main_point("request", "Please do not share the draft yet.") == \
        " asking them not to share the draft yet"
    assert instructions.main_point("invitation", "Would you wanna grab lunch on Friday?") == \
        " asking whether they would like to grab lunch on Friday"
    assert instructions.main_point("update", "The report is done.") == ""


def test_forms_tones_and_lengths():
    assert instructions.guess_form("Running ten minutes late, start without me.", "update", "a colleague") == \
        "text message"
    assert instructions.guess_form("Hi all,\n\nPlease note the lift is out today and tomorrow. Use the stairs on "
                                   "the east side.\n\n[Your name]", "announcement", "the team") == "memo"
    assert instructions.guess_tone("Hey! Thanks, that's awesome, see you there!", "update") == "friendly and casual"
    assert instructions.guess_tone("Dear Ms [Name], I would like to request a copy. Kind regards.", "request") == \
        "polite and professional"
    assert instructions.guess_tone("Anything", "complaint") == "firm but polite"
    assert instructions.length_word("word " * 20) == "very short"
    assert instructions.length_word("word " * 60) == "short"
    assert instructions.length_word("word " * 150) == "fairly short"


def test_subject_hints_skip_empty_and_placeholder_subjects():
    assert instructions.subject_hint("Budget for March") == ' The subject is "Budget for March".'
    for subject in ["", "Hi", "FYI", "[Name 2]", "1234"]:
        assert instructions.subject_hint(subject) == ""


def test_a_whole_instruction_is_plain_and_the_same_every_time():
    text = "Hi [Name],\n\nUnfortunately I can't make the meeting on Thursday. Could we move it to Friday?\n\n" \
           "Thanks,\n[Your name]"
    first = instructions.make_instruction("Thursday meeting", text, "a colleague", is_reply=True)
    second = instructions.make_instruction("Thursday meeting", text, "a colleague", is_reply=True)
    assert first == second
    instruction, details = first
    assert details["kind"] == "declining"
    assert details["audience"] == "a colleague"
    assert "a colleague" in instruction and "It answers a message they sent." in instruction
    assert instruction.endswith('The subject is "Thursday meeting".')
    assert "  " not in instruction and ".." not in instruction
