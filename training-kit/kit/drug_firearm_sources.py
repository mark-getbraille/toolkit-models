"""DRUGS, COUNTERFEIT PILLS AND PARAPHERNALIA, and FIREARMS AND FIREARM ACCESSORIES for the Picture Model Training
Kit: the collections that cannot be ready-made packs because of their licence, and the ones that need a sign-up,
need permission, or were looked at and left out. The open ones (Commons drug, paraphernalia, accessory, gun-kind and
maker categories, CBP seizure photos, CDC PHIL drug photos and Wikidata firearm models with a picture) are packs in
packs/drug_firearm_packs.py.

As in med_vet_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on
the user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.
Every licence was checked at its source in November 2026 (the link and the terms line are in each entry).

Groups (Source.group, as in sources.py):
  "share-alike"  CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with them
                 is CC BY-SA.

Answers are fixed sentences from each source's own words (a Commons category's name, a file's own caption), never
written by an AI model. Answers about a drug or pill end with DRUG_LINE ("Drugs cannot be identified for sure by how
they look ..."); answers about a gun end with GUN_LINE ("Treat every gun as loaded ..."), the owner's line.

Safety (packs/SOURCE-RULES.md and drug_firearm_packs.py): no sexual content; no child (files whose words name a child
are left out, never kept); no one using a drug, no overdose, no one shot, wounded or killed, no gun pointed at a
person; no files for making a suppressor or converting a gun; files whose words name a person are left out, so the
entry shows the things themselves. Even so, NONE of these collections is ever used for picture-making
(DRUG_FIREARM_PICTURE_MAKING_OK is empty, so sources.py puts every key in NOT_FOR_PICTURE_MAKING).

The collections (DRUG_FIREARM_SOURCES):
  share-alike
    drug_firearm_commons_sa  Wikimedia Commons files under CC BY-SA or GFDL of the categories of the open packs
                           (drugs, paraphernalia, firearm accessories and firearm kinds). Captions CC0. Firearm MODELS
                           under BY-SA are already safety_rites_sources.commons_firearms_sa, so not repeated.

Needing sign-up (DRUG_FIREARM_SIGN_UP), permission candidates (DRUG_FIREARM_PERMISSION_CANDIDATES), and looked at but
not included (DRUG_FIREARM_NOT_INCLUDED, with the reason).

    python kit/drug_firearm_sources.py drug_firearm_commons_sa --cap 8      (from the kit folder: a quick check)
"""

import json
import os
import re

from home_sources import commons_sa_items
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS
from extra_sources import say
from sources import Source

WHAT_Q = "What is this?"
DRUG_LINE = "Drugs cannot be identified for sure by how they look: only a laboratory test can tell what is in them."
GUN_LINE = "Treat every gun as loaded, and keep your fingers away from the trigger."

# Words that leave a file out (every row of it): someone using a drug, harm, death, shooting or crime, toys and
# replicas, making a suppressor or converting a gun, and people.
USE_NOUNS = re.compile(r"\b(smoking|vaping|vape|injecting|injection|smoke) (pipes?|devices?|accessor\w*|articles?|"
                       r"paraphernalia|products?|implements?|equipment|bowls?|mixtures?|blends?|kits?|pens?|"
                       r"liquids?|juices?|shops?|supplies|tobacco|papers?)\b", re.I)
USE = re.compile(r"\b(smok(es|ed|ing)|smoker\w*|inhal\w*|inject\w*|snort\w*|vap(es|ed|ing)|toking|puff\w*|"
                 r"overdos\w*|addict\w*|users?|junkies?|stoned|high on)\b", re.I)
HARM = re.compile(r"\b(dead|deaths?|died|killed|corpses?|wound\w*|injur\w*|blood\w*|murder\w*|crime|suicide|robbery|"
                  r"shoot(s|ing)? (at|people|someone)|shot (at|by|dead)|gunshot|at gunpoint|hostages?|evidence|"
                  r"fir(e|es|ed|ing)\b|airsoft|replicas?|toys?|props?|nude|naked|sexual\w*)\b", re.I)
MAKING = re.compile(r"\b(solvent traps?|baffles?|build kits?|form 1|drilled|filter adapters?|oil filters?|"
                    r"home-?made|improvised|auto ?sears?|lightning links?|conversion kits?|3D[- ]printed|ghost guns?|"
                    r"80% lowers?|jigs?)\b", re.I)
PERSON = re.compile(r"\b(man|men|woman|women|person|people|boy|boys|girl|girls|wearing|holding|he|she|his|her|"
                    r"him|portraits?|selfie|soldiers?|troops?|police\w*|officers?|agents?|hunters?|marines?|"
                    r"sailors?|airm[ae]n|guards?|hands?|faces?)\b", re.I)


def left_out(words):
    """True when a file's words name someone using a drug, harm or crime, a toy or replica, making a suppressor or
    converting a gun, a child, or a person."""
    return bool(USE.search(USE_NOUNS.sub(" ", words)) or HARM.search(words) or MAKING.search(words)
                or CHILD_WORDS.search(words) or PERSON.search(words))


# ----------------------------------------------------------------- share-alike: Commons BY-SA files

def spec(category, answer, deeper=False, line=""):
    """(category, question, answer with its line, also its subcategories) for home_sources.commons_sa_items."""
    return (category, WHAT_Q, f"{answer} {line}".strip(), deeper)


# The categories of packs/drug_firearm_packs.py (the answers shortened to their first clause).
DRUG_FIREARM_SA = [
    spec("Cannabis buds", "This looks like cannabis (marijuana) flower.", True, DRUG_LINE),
    spec("Cannabis edibles", "This looks like a cannabis edible: a food or sweet made with cannabis.", True,
         DRUG_LINE),
    spec("Hashish", "This looks like hashish (hash): resin from the cannabis plant pressed into a block.", True,
         DRUG_LINE),
    spec("Joints (cannabis)", "This looks like a joint: cannabis rolled in paper.", True, DRUG_LINE),
    spec("Cocaine", "This looks like cocaine: an illegal stimulant drug, usually a white powder.", False, DRUG_LINE),
    spec("Crack cocaine", "This looks like crack cocaine.", True, DRUG_LINE),
    spec("Heroin", "This looks like heroin: an illegal opioid drug.", False, DRUG_LINE),
    spec("Methamphetamine", "This looks like methamphetamine (meth): an illegal stimulant drug.", False, DRUG_LINE),
    spec("Ecstasy tablets", "These look like ecstasy tablets: pressed pills sold as the drug MDMA.", False, DRUG_LINE),
    spec("Psilocybin mushrooms", "These look like psilocybin mushrooms (magic mushrooms).", False, DRUG_LINE),
    spec("Opium", "This looks like opium: the dried sap of the opium poppy.", False, DRUG_LINE),
    spec("Counterfeit medications", "This looks like a counterfeit (fake) medicine.", True, DRUG_LINE),
    spec("Seized drugs", "These look like illegal drugs seized by police or customs.", True, DRUG_LINE),
    spec("Bongs", "This looks like a bong: a water pipe used to smoke cannabis or tobacco.", True),
    spec("Smoking pipes", "This looks like a smoking pipe.", True),
    spec("Hookahs", "This looks like a hookah (a shisha pipe).", True),
    spec("Electronic cigarettes", "This looks like an electronic cigarette (a vape).", True),
    spec("Cannabis vaporizers", "This looks like a cannabis vaporizer.", True),
    spec("Cigarette rolling papers", "These look like rolling papers.", True),
    spec("Herb grinders", "This looks like a herb grinder."),
    spec("Drug paraphernalia", "This looks like drug paraphernalia: equipment used to take illegal drugs.", True),
    spec("Holsters", "This looks like a holster: a case that holds a handgun."),
    spec("Speedloaders", "This looks like a speedloader for a revolver."),
    spec("Stripper clips", "This looks like a stripper clip: a metal strip that holds a row of cartridges."),
    spec("Telescopic sights", "This looks like a telescopic sight (a scope) for a gun."),
    spec("Reflex sights", "This looks like a red dot (reflex) sight."),
    spec("Iron sights", "These look like iron sights: the metal sights on a gun."),
    spec("Tactical lights", "This looks like a tactical light: a strong flashlight, often mounted on a gun."),
    spec("Laser sights", "This looks like a laser sight for a gun."),
    spec("Slings (firearms)", "This looks like a gun sling."),
    spec("Firearm silencers", "This looks like a suppressor (a silencer)."),
    spec("Muzzle brakes", "This looks like a muzzle brake."),
    spec("Firearm cases", "This looks like a gun case."),
    spec("Gun cleaning equipment", "This looks like gun cleaning equipment."),
    spec("Gun safes", "This looks like a gun safe.", True),
    spec("Gun racks", "This looks like a gun rack."),
    spec("Trigger locks", "This looks like a trigger lock."),
    spec("Revolvers", "This looks like a revolver.", False, GUN_LINE),
    spec("Semi-automatic pistols", "This looks like a semi-automatic pistol.", False, GUN_LINE),
    spec("Derringers", "This looks like a derringer: a very small pocket pistol.", False, GUN_LINE),
    spec("Double-barreled shotguns", "This looks like a double-barrelled shotgun.", False, GUN_LINE),
    spec("Pump-action shotguns", "This looks like a pump-action shotgun.", False, GUN_LINE),
    spec("Bolt-action rifles", "This looks like a bolt-action rifle.", False, GUN_LINE),
    spec("Lever-action rifles", "This looks like a lever-action rifle.", False, GUN_LINE),
    spec("Hunting rifles", "This looks like a hunting rifle.", False, GUN_LINE),
    spec("Air rifles", "This looks like an air rifle.", False, GUN_LINE),
]


def sa_items(specs, cap, test, prefix):
    """home_sources.commons_sa_items (files under CC BY-SA or GFDL, the categories sharing the cap, children left
    out), without the files whose words are left out (left_out): every row of such a file goes."""
    items = commons_sa_items(specs, cap, test, prefix, adults_only=True)
    bad = {name for name, _, row in items if left_out(f"{name.replace('_', ' ')} {row['answer']}")}
    if bad:
        say(f"  {len(bad)} files left out by their words")
    return [i for i in items if i[0] not in bad]


def prepare_drug_firearm_commons_sa(source, data_dir, work, cap):
    """Commons drug, paraphernalia, firearm accessory and firearm kind categories, files under CC BY-SA or GFDL."""
    items = sa_items(DRUG_FIREARM_SA, cap, source.test, "drugfire-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
DRUG_FIREARM_SOURCES = [
    Source("drug_firearm_commons_sa", "Wikimedia Commons: drugs, counterfeit pills, bongs, pipes, vapes, holsters, "
                                      "scopes, lights, suppressors, gun safes and kinds of guns, files under CC BY-SA "
                                      "or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 1500, 20, prepare_drug_firearm_commons_sa, "about 300 MB of pictures", terms=SA_TERMS,
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
]

# The collections a picture-making model may learn from: none (drugs and guns are for describing only).
DRUG_FIREARM_PICTURE_MAKING_OK = set()

DRUG_FIREARM_SIGN_UP = {
    "Roboflow Universe pill, drug and weapon detection sets (for example handgun, knife and 'weapon detection' sets)":
        "https://universe.roboflow.com : a free Roboflow account and API key (it would come from a GitHub secret such "
        "as ROBOFLOW_API_KEY) to export. Each set's licence must be checked on its page, and where its photos came "
        "from: most weapon and drug sets are scraped from web searches, films and news (other people's copyright), "
        "so a set is usable only when its page names its own photos and an open licence. Not built.",
    "Kaggle pill, drug and firearm image sets":
        "https://www.kaggle.com : a free Kaggle account and API token (KAGGLE_USERNAME and KAGGLE_KEY secrets); each "
        "set's licence checked one by one ('Other', 'Unknown' and web-scraped sets are not usable). Not built.",
    "DVIDS (US Department of Defense photos of small arms, optics and accessories)":
        "https://www.dvidshub.net : public domain photos, but its API needs a free key (the kit's signup_sources "
        "DVIDS entry). Most DVIDS small-arms photos show service members and are in the open commons_military pack "
        "through their Commons copies already.",
}

DRUG_FIREARM_PERMISSION_CANDIDATES = {
    "DrugsData.org (Erowid Center; formerly EcstasyData)":
        "Has: about 20,000 laboratory-tested drug samples, most with a photo of the pill or powder and what the "
        "laboratory found in it (exactly the 'what is really in this pill' answer). Terms on every page: '(c) "
        "Copyright 2001 - 2024 Erowid Center. All rights reserved.', 'By using this site you agree not to publish "
        "results or analysis of our data without written permission from Erowid Center', 'Permission required "
        "before reproducing or using in other software or system.' Ask Erowid Center (https://www.erowid.org/"
        "general/about/about_contact.shtml) for written permission.",
    "NIDA (National Institute on Drug Abuse) drug photos":
        "NIDA's written materials are public domain, but its FAQ says many 'photographs, illustrations, and videos' "
        "on its site 'are not in the public domain and may not be used without permission' (most of its drug photos "
        "are credited to DEA or stock agencies). Ask: nidamultimedia@mail.nih.gov.",
    "EUDA (European Union Drugs Agency, formerly EMCDDA)":
        "Its legal notice says its copyright policy is compatible with CC BY 4.0 (search result, "
        "https://www.euda.europa.eu/about/legal-notice; the page refused this machine, 403, so its exceptions for "
        "photos were not read: unverified). Its drug profiles carry few photos, several credited to others. Ask "
        "through the contact form whether its own drug photos may be used under CC BY 4.0.",
}

DRUG_FIREARM_NOT_INCLUDED = {
    "DEA (dea.gov): One Pill Can Kill counterfeit pill photos, Drug Fact Sheets, the 'Drug Images' gallery, press "
    "and seizure photos":
        "DEA's own words (DEA-run sites' disclaimers and archived DEA pages, found by search): US government works "
        "'may be used without obtaining permission from DEA', but 'if a photo is copyrighted, permission should be "
        "obtained from the copyright owner', and material with visible DEA identifiers may not be used. dea.gov "
        "refuses automated readers: every page, robots.txt included, answered 403 'Access Denied' (Akamai) to this "
        "machine on 19 November 2026, so neither its robots.txt nor its current legal page could be read, and the "
        "Internet Archive's copies (web.archive.org) could not be reached from this machine either. Not built. DEA "
        "photos that people have copied to Commons are used, each file's licence checked there (Commons categories "
        "'Drug Enforcement Administration', 'Seized drugs', 'Fentanyl', 'Counterfeit medications' in the open "
        "commons_drugs pack). A builder reading the Internet Archive copies of dea.gov/media-gallery/drug-images "
        "could be tried from GitHub's machines once its robots.txt can be read (unverified).",
    "DEA Microgram Bulletin (tablet photos with laboratory findings)":
        "the bulletins' photos are sent in by many federal, state and local laboratories and are credited to them "
        "(state and local works are not US federal works, so not public domain by 17 U.S.C. 105); the PDFs are on "
        "dea.gov, which refuses this machine (see above). Not built.",
    "FDA counterfeit medicine and BeSafeRx pages":
        "FDA text is public domain, but no gallery of counterfeit-pill photos with captions was found; the few "
        "photos on its pages are not listed anywhere with their source. Not built (unverified: fda.gov pages were "
        "not read one by one).",
    "CDC drug photos beyond PHIL":
        "CDC's overdose-prevention pages use stock photos (iStock, Getty). Only PHIL items whose own copyright field "
        "says public domain are used (the open cdc_phil_drugs pack).",
    "ATF (Bureau of Alcohol, Tobacco, Firearms and Explosives) photos":
        "Commons's ATF category (48 files, 15 subcategories, November 2026) holds the 1993 Mount Carmel fire, Ruby "
        "Ridge, badges, seals, flags, buildings and directors, not firearm or accessory photos. ATF's own photos are "
        "on Flickr (not used: Flickr's API terms forbid storing photos). Not built.",
    "Commons 'Magazines (firearms)' and its subcategories":
        "already in the open commons_uxo pack (safety_rites_packs.py), whose answers end with the warning line for "
        "ammunition found lying around. Not repeated.",
    "Commons firearm and cartridge MODEL categories, military small arms and their sights":
        "already commons_firearms, commons_cartridges (and commons_firearms_sa) and commons_military. Not repeated; "
        "the new wikidata_firearms pack takes only models that have a picture but no Commons category.",
    "Smithsonian and National Park Service historic arms":
        "the Smithsonian's arms are in the open nmah_service pack (service_packs.py); the Smithsonian's own API "
        "needs a key (api.data.gov), and its open-access bucket has no subject index (all of the National Museum of "
        "American History's records would have to be read to find the guns). NPS museum photos are mostly in "
        "npgallery. Not built separately.",
    "Health Canada and UK government drug images":
        "no image collection of drugs or paraphernalia under the Open Government Licence was found (Health "
        "Canada's Drug Product Database has no pictures; see med_vet_sources). Not built.",
    "Pillreports and similar user-submitted pill sites":
        "photos uploaded by the public with no licence; terms forbid copying. Not built.",
    "Commons categories with no files or not about the thing (November 2026)":
        "Khat, Kratom, LSD, Vaporizers (cannabis), Rolling papers, Bipods, Gun holsters, Red dot sights, Gun locks, "
        "Gun cleaning kits, Suppressors, Gun cases (the spellings 'Cannabis vaporizers', 'Cigarette rolling "
        "papers', 'Reflex sights', 'Trigger locks', 'Firearm silencers' and 'Firearm cases' do have files and are "
        "used); 'Synthetic cannabinoids', 'Nitrous oxide', 'Ayahuasca', 'Salvia divinorum' and 'Peyote' are mostly "
        "chemical structures, plants or ceremonies.",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one drug or firearm collection.")
    parser.add_argument("key", choices=[s.key for s in DRUG_FIREARM_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in DRUG_FIREARM_SOURCES if s.key == args.key)
    source.test = 0
    source.cap = args.cap
    data = args.data or tempfile.mkdtemp(prefix="drug-firearm-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
