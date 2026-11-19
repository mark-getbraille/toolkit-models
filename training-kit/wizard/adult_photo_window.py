"""The reviewer window for DOCUMENTED ADULT PHOTOGRAPHS (training-kit/kit/adult_photo_review.py): an optional second
look by the owner's sighted team at the photographs that were approved automatically because their institution's
record documents that every person in them is an adult.

Only those approved photographs are ever listed or shown: a record without that documentation was never downloaded
and is not in the review folder at all. The picture is read from its approved file into memory and shown with the
catalogue's title, institution, words, rights and the reason it was approved, with a button that opens the
catalogue page in the browser.

The reviewer types their name once when the window opens. For each picture:
  Approve (Alt+A, or the Y key): every person is clearly an adult. The second look is logged; nothing else changes.
  Reject (Alt+R, or the N key): the picture and its description are DELETED, it leaves its workspace, and its id is
    blocked so it is never fetched again.
  Unsure (Alt+S): counts as Reject (deleted and blocked), logged as "unsure".
Every decision is written to decisions.csv with the reviewer's name and the time.

Accessibility (the kit's rules): a label ending ":" right before every field and list, an Alt letter on every
button named in its tooltip, no letter twice, no default button, Escape closes, F1 opens the guide (HOW TO REVIEW
DOCUMENTED ADULT PHOTOGRAPHS.txt). Plain standard controls.

    python adult_photo_window.py "<review folder>"
"""

import io
import os
import re
import subprocess
import sys
import webbrowser

import wx

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(os.path.dirname(HERE), "kit")
if KIT not in sys.path:
    sys.path.insert(0, KIT)

import adult_photo_review as apr  # noqa: E402

GUIDE = os.path.join(os.path.dirname(HERE), "HOW TO REVIEW DOCUMENTED ADULT PHOTOGRAPHS.txt")
PICTURE_BOX = (520, 390)


def open_file(path):
    """Open a file with its usual program (the guide)."""
    if hasattr(os, "startfile"):
        os.startfile(path)  # noqa: S606 - the kit's own guide
    else:
        subprocess.Popen(["xdg-open", path])  # noqa: S603,S607


def ask_name(parent=None):
    """Ask the reviewer's name once (None when cancelled or empty)."""
    dialog = NameDialog(parent)
    try:
        if dialog.ShowModal() == wx.ID_OK and dialog.field.GetValue().strip():
            return dialog.field.GetValue().strip()
        return None
    finally:
        dialog.Destroy()


class Rules(wx.Dialog):
    """A dialog with the kit's keys: Escape closes, F1 opens the guide, Alt and a label's letter moves focus."""

    def __init__(self, parent, title, size):
        """Make the dialog and its panel."""
        super().__init__(parent, title=title, size=size, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.panel = wx.Panel(self)
        self.mnemonics = {}
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def labelled(self, sizer, label, factory, proportion=0):
        """A label ending ":" and, right after it (made after it, so it follows in tab order), its control."""
        sizer.Add(wx.StaticText(self.panel, label=label), 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
        control = factory()
        sizer.Add(control, proportion, wx.EXPAND | wx.ALL, 6)
        letter = re.search(r"&(\w)", label)
        if letter:
            self.mnemonics[letter.group(1).lower()] = control
        return control

    def button(self, label, tip, handler):
        """A button with its Alt letter named in its tooltip."""
        b = wx.Button(self.panel, label=label)
        b.SetToolTip(f"{tip} (Alt+{re.search(r'&(\w)', label).group(1).upper()})")
        b.Bind(wx.EVT_BUTTON, handler)
        return b

    def on_key(self, event):
        """Escape closes, F1 opens the guide, Alt and a label's letter moves focus; the rest goes on."""
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif key == wx.WXK_F1:
            open_file(GUIDE)
        elif event.AltDown() and not event.ControlDown() and 0 < key < 256 and chr(key).lower() in self.mnemonics:
            self.mnemonics[chr(key).lower()].SetFocus()
        elif not self.keys(event, key):
            event.Skip()

    def keys(self, event, key):
        """Extra keys of a window (True when used)."""
        return False


class NameDialog(Rules):
    """The reviewer's name, asked once when the window opens."""

    def __init__(self, parent):
        """The name field and two buttons."""
        super().__init__(parent, "Your name", (460, 200))
        s = wx.BoxSizer(wx.VERTICAL)
        self.field = self.labelled(s, "Your &name (written with every decision):", lambda: wx.TextCtrl(self.panel))
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.button("&Start", "Start reviewing", lambda e: self.EndModal(wx.ID_OK)), 0, wx.ALL, 4)
        row.Add(self.button("&Cancel", "Do not review now", lambda e: self.EndModal(wx.ID_CANCEL)), 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        self.panel.SetSizer(s)
        self.field.SetFocus()


class ReviewWindow(Rules):
    """The second-look window (see the module docstring)."""

    def __init__(self, parent, folder, person):
        """The list of approved pictures, the picture, its catalogue words, the buttons and the status."""
        super().__init__(parent, "Documented adult photographs: second look", (1000, 760))
        self.review, self.person = apr.ReviewFolder(folder), person
        s = wx.BoxSizer(wx.VERTICAL)
        top = wx.BoxSizer(wx.HORIZONTAL)
        left = wx.BoxSizer(wx.VERTICAL)
        self.list = self.labelled(left, "&Pictures approved as documented adults:", lambda: wx.ListBox(self.panel), 1)
        self.list.Bind(wx.EVT_LISTBOX, lambda e: self.show())
        top.Add(left, 1, wx.EXPAND)
        self.picture = wx.StaticBitmap(self.panel, size=PICTURE_BOX)
        top.Add(self.picture, 0, wx.ALL, 6)
        s.Add(top, 1, wx.EXPAND)
        self.text = self.labelled(s, "Catalogue &words, rights and reason:",
                                  lambda: wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY), 1)
        row = wx.BoxSizer(wx.HORIZONTAL)
        for label, tip, handler in (
                ("&Approve: every person is clearly an adult", "Confirm the approval (also the Y key)",
                 lambda e: self.decide("approve")),
                ("&Reject", "Delete this picture and never fetch it again (also the N key)",
                 lambda e: self.decide("reject")),
                ("Un&sure", "Counts as reject: the picture is deleted and never fetched again",
                 lambda e: self.decide("unsure")),
                ("&Open the catalogue page", "Open the institution's page in the browser", self.on_page),
                ("&Close", "Close the window", lambda e: self.EndModal(wx.ID_CANCEL))):
            row.Add(self.button(label, tip, handler), 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        self.status = self.labelled(s, "S&tatus:", lambda: wx.TextCtrl(self.panel, style=wx.TE_READONLY))
        self.panel.SetSizer(s)
        self.items = []
        self.fill()

    def fill(self, keep=0):
        """List the approved pictures still in the review folder."""
        self.items = [i for i in self.review.items() if i.get("status", "").startswith("approved") and i.get("file")]
        self.list.Set([f"{i['title'][:70]} ({i['institution']})" for i in self.items] or [])
        if self.items:
            self.list.SetSelection(min(keep, len(self.items) - 1))
            self.show()
        else:
            self.picture.SetBitmap(wx.Bitmap(1, 1))
            self.text.SetValue("")
            self.say("No approved pictures are waiting for a second look.")
        self.list.SetFocus()

    def current(self):
        """The selected item, or None."""
        n = self.list.GetSelection()
        return self.items[n] if 0 <= n < len(self.items) else None

    def show(self):
        """Show the selected picture (read into memory) and its catalogue words."""
        item = self.current()
        if not item:
            return
        path = os.path.join(self.review.folder, item["file"])
        try:
            with open(path, "rb") as f:
                image = wx.Image(io.BytesIO(f.read()))
            scale = min(PICTURE_BOX[0] / image.GetWidth(), PICTURE_BOX[1] / image.GetHeight(), 1)
            image = image.Scale(max(1, int(image.GetWidth() * scale)), max(1, int(image.GetHeight() * scale)))
            self.picture.SetBitmap(wx.Bitmap(image))
        except Exception:  # noqa: BLE001 - the picture cannot be read
            self.picture.SetBitmap(wx.Bitmap(1, 1))
        self.text.SetValue(f"Title: {item['title']}\nInstitution: {item['institution']}\n"
                           f"Approved because: {item['reason']}\nRights: {item['rights']} ({item['group']})\n"
                           f"Catalogue words: {item['catalogue_text']}\nPage: {item['page_url']}")
        self.say(f"Picture {self.list.GetSelection() + 1} of {len(self.items)}: {item['title'][:80]}.")

    def say(self, text):
        """Put a message in the Status field (read by the screen reader)."""
        self.status.SetValue(text)

    def decide(self, choice):
        """Approve (logged), Reject or Unsure (deleted and blocked)."""
        item = self.current()
        if not item:
            return
        n = self.list.GetSelection()
        if choice == "approve":
            apr.confirm(self.review, item["id"], self.person)
            self.say("Approved: logged with your name.")
            self.fill(n + 1)
        else:
            apr.reject(self.review, item["id"], self.person, "rejected" if choice == "reject" else "unsure")
            self.fill(n)
            self.say("Rejected: the picture was deleted and will never be fetched again." if choice == "reject" else
                     "Unsure counts as reject: the picture was deleted and will never be fetched again.")

    def keys(self, event, key):
        """Y approves and N rejects (every field of this window is read-only, so the keys never type)."""
        if event.AltDown() or event.ControlDown():
            return False
        if key in (ord("Y"), ord("y")):
            self.decide("approve")
            return True
        if key in (ord("N"), ord("n")):
            self.decide("reject")
            return True
        return False

    def on_page(self, _event):
        """Open the catalogue page in the browser."""
        item = self.current()
        if item and item.get("page_url", "").startswith("https://"):
            webbrowser.open(item["page_url"])


def main(argv=None):
    """Open the window for a review folder."""
    argv = list(sys.argv[1:] if argv is None else argv)
    folder = argv[0] if argv else apr.DEFAULT_FOLDER
    app = wx.App(False)
    person = ask_name()
    if person:
        window = ReviewWindow(None, folder, person)
        window.ShowModal()
        window.Destroy()
    app.Destroy()
    return 0


if __name__ == "__main__":
    sys.exit(main())
