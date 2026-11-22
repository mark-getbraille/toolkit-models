"""The collection "Audio recorders, podcast microphones and recording gear (manuals)" (category key audio_gear): the
owner's request of 2026-11-22 for audio and media production. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (voice recorders and
            dictaphones, IC and PCM recorders, handheld, portable and field recorders, podcast gear, lavalier
            microphones and preamps). No word another collection already searches: microphones, mixers, audio
            interfaces and multitrack recorders are musical_instruments' (with the Tascam, Shure and M-Audio
            collections), headphones and headsets everyday_electronics', amplifiers and stereos tv_audio_video's;
  makers    the recorder and microphone makers, LINK-ONLY by the owner's rule: their own manuals and guides are for
            the person to open in a browser or fetch with Program Downloader; nothing is read from their sites;
  guidance  the pages the reference library builds in full (textbooks/audio_media.py: the Audacity Manual, OSARA,
            the W3C WAI media guide and the Library of Congress's audio and video format descriptions), as links.

The notice is said first (NOTICE): hearing (keep headphone volume down) and batteries.
"""

NOTICE = ("Keep the volume down when monitoring with headphones or earbuds: loud sound for long periods damages "
          "hearing. Use the batteries and chargers the maker names, and keep button and coin batteries away from "
          "children. Ask permission before recording people: recording laws differ from state to state.")

IA_WORDS = ["voice recorder", "dictaphone", "ic recorder", "pcm recorder", "handheld recorder", "portable recorder",
            "field recorder", "audio recorder", "podcast", "lavalier", "preamp"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="audio_gear", prefix="ag", documents="manuals", access="link", reason=RULE, types=[])
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="zoom", maker="Zoom Corporation", type="handheld and field recorders, podcast recorders",
         library="https://zoomcorp.com/en/us/support/", site="zoomcorp.com"),
    dict(key="tascam-recorders", maker="TASCAM (portable recorders)", type="handheld and field recorders",
         library="https://tascam.com/us/", site="tascam.com"),
    dict(key="om-system", maker="OM System (formerly Olympus) audio", type="voice recorders",
         library="https://explore.omsystem.com/us/en/support", site="omsystem.com"),
    dict(key="sony-audio", maker="Sony (IC recorders)", type="voice recorders",
         library="https://www.sony.com/electronics/support", site="sony.com"),
    dict(key="philips-speech", maker="Philips Speech Processing Solutions (Speech Processing Solutions GmbH)",
         type="dictation recorders", library="https://www.dictation.philips.com/", site="dictation.philips.com"),
    dict(key="rode", maker="RØDE Microphones", type="podcast and USB microphones, wireless and lavalier "
         "microphones, podcast consoles", library="https://rode.com/en/support", site="rode.com"),
    dict(key="focusrite", maker="Focusrite", type="audio interfaces and preamps", library="https://support.focusrite.com/",
         site="focusrite.com"),
    dict(key="audio-technica", maker="Audio-Technica", type="microphones and headphones",
         library="https://www.audio-technica.com/en-us/support", site="audio-technica.com"),
    dict(key="shure-podcast", maker="Shure (podcast and USB microphones)", type="podcast microphones",
         library="https://www.shure.com/en-US/support", site="shure.com"),
]]

GUIDANCE = [
    dict(title="Audacity Manual (the Audacity Team, CC BY 3.0; built in full: media:audacity_manual)",
         url="https://manual.audacityteam.org/", by="the Audacity Team"),
    dict(title="OSARA: accessibility for REAPER (GPL; built in full: media:osara_guide)",
         url="https://osara.reaperaccessibility.com/", by="James Teh, NV Access and the OSARA contributors"),
    dict(title="Making Audio and Video Media Accessible (W3C WAI; built in full: media:wai_media_accessibility)",
         url="https://www.w3.org/WAI/media/av/", by="the W3C Web Accessibility Initiative"),
    dict(title="Sound and moving image formats (Library of Congress; built in full: media:loc_av_formats)",
         url="https://www.loc.gov/preservation/digital/formats/fdd/sound_fdd.shtml", by="the Library of Congress"),
]

CATEGORY = dict(
    name="Audio recorders, podcast microphones and recording gear (manuals)",
    description="Voice recorders and dictaphones, IC and PCM recorders, handheld, portable and field recorders, "
                "podcast microphones and consoles, lavalier and wireless microphones and preamps: the Internet "
                "Archive's manuals, the makers' manual pages (links) and the reference library's audio guides. "
                "Microphones, mixers and audio interfaces in general are in the musical instruments and pro audio "
                "collection. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
