"""A small made-up scanned PDF for the OCR tests: each page is a picture of printed text (no text layer), the way
agencies release printed emails. Every name, address and number in it is made up."""

import io

PAGES = [
    # page 1: a cover sheet with almost no text (the reader leaves it out)
    ["Release 7"],
    # page 2: a State Department-style email with a stamp, an attachment line, and a card number to mask
    ["U.S. Department of State Case No. F-2016-00001",
     "From: Lee, Jo <leej@state.gov>",
     "Sent: Monday, May 4, 2015 9:12 AM",
     "To: Bo Ray",
     "Subject: Re: water samples",
     "Attachments: Sampling plan.docx",
     "",
     "Bo, thanks for the quick turnaround. Can you send the results from",
     "Tuesday before the call? The card for the lab fee is 4111 1111 1111 1111.",
     "Jo"],
    # page 3: the attachment, printed after the email
    ["Sampling plan for the spring",
     "We will take water samples from twelve homes each week and send",
     "them to the state laboratory. Results come back in about ten days.",
     "Each household gets a letter with its own results and a phone number",
     "to call with questions about the readings and what they mean."],
    # page 4: the earlier message in the thread, from outside the government
    ["From: Bo Ray <bo.ray@example.com>",
     "Sent: Friday, May 1, 2015 4:40 PM",
     "To: Lee, Jo",
     "Subject: water samples",
     "",
     "Jo, the first samples are back and the lab says the numbers look",
     "better than last month. I will have the full results next week."],
]


def make_pdf(pages=PAGES, size=(1275, 1650), font_size=30):
    """The bytes of an image-only PDF with one page picture per entry of pages (lists of lines)."""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.load_default(size=font_size)
    pictures = []
    for lines in pages:
        img = Image.new("L", size, 255)
        draw = ImageDraw.Draw(img)
        y = 110
        for line in lines:
            draw.text((90, y), line, fill=0, font=font)
            y += int(font_size * 1.6)
        pictures.append(img.convert("RGB"))
    out = io.BytesIO()
    pictures[0].save(out, "PDF", save_all=True, append_images=pictures[1:], resolution=150)
    return out.getvalue()
