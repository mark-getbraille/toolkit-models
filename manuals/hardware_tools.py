"""Hardware, tools and shop equipment in the manual library: the makers' manual and installation-instruction
libraries of door and cabinet hardware, fasteners and connectors, plumbing fittings, electrical devices, garage doors,
power and hand tools, outdoor power equipment, woodshop and metal shop machines and welders, automotive shop tools,
trade tools, masonry, painting and drywall tools, ladders and material handling, sewing machines, kitchen equipment,
accessible tools and personal protective equipment, with each category's safety notice and its public-domain guides
(categories.py adds these categories and extends power_tools, hand_tools and lawn_garden with them).

The makers. Each maker's robots.txt, home page, terms of use and support pages were read by a program on 2026-11-21
with the builder's own User-Agent (the same rules as the firearms makers, categories.MAKERS):
  read     robots.txt allows the page and the terms do not forbid programs (or no terms page was found), and the page
           holds the maker's manual files: the builder reads only the pages listed and keeps the links to the
           maker's own files (its hosts). One maker: RIKON (Weiser's and Clopay's pages allow programs, but their
           file hosts' robots.txt do not).
  link     everything else: the site refuses programs, its robots.txt says ai-train=no, its terms speak of robots,
           spiders, scraping, data mining or deep links, or no page of manual files was found. Nothing is read; the
           library's address (or the home page, where no library address was confirmed) is listed for the person
           to open. Each maker's own reason is in its entry.

Public-domain guides (public_guides): US government works, each the Internet Archive's copy (osha.gov and fema.gov
refuse programs, and research.fs.usda.gov's robots.txt disallows everything), kept in the index only when the item
has a PDF; a military training manual (army or navy) only when the front of its own text says "Approved for public
release; distribution is unlimited" or it is older than 1964, and shows no restricted marking (checked at every
build: build_manuals.public_guide_entries). The official pages of OSHA, FEMA, NIOSH and the Forest Products Laboratory
are linked as guidance for the person to open.

The safety notice ("notice") of each category is written into its index, for the toolkit to say first.
"""

# What the documents of a maker are called, the index ids' prefix, and an empty "types" so that the firearm words of
# build_manuals.TYPES ("safe", "laser", "lock" ...) are never used for these products: each keeps its maker's type.
_COMMON = dict(prefix="hw", types=[], documents="manuals and installation instructions")


def _makers(category, makers):
    """The makers of one category, with the shared fields and the category key."""
    return [dict(_COMMON, category=category, **m) for m in makers]


_POWER = [
    dict(key='dewalt', maker='DeWalt', type='power tool', access='link', library='https://www.dewalt.com/', reason='its terms of use (read 2026-11-21) speak of data mining, robot, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='milwaukee', maker='Milwaukee Tool', type='power tool', access='link', library='https://www.milwaukeetool.com/Support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='makita', maker='Makita', type='power tool', access='link', library='https://www.makitatools.com/', reason='its terms of use (read 2026-11-21) speak of harvesting, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='ryobi', maker='Ryobi', type='power tool', access='link', library='https://www.ryobitools.com/support/manuals', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='bosch', maker='Bosch Power Tools', type='power tool', access='link', library='https://www.boschtools.com/us/en/service', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='craftsman', maker='Craftsman', type='power tool', access='link', library='https://www.craftsman.com/support', reason='its terms of use (read 2026-11-21) speak of data mining, robot, so nothing is read'),
    dict(key='black-decker', maker='BLACK+DECKER', type='power tool', access='link', library='https://www.blackanddecker.com/', reason='its terms of use (read 2026-11-21) speak of data mining, robot, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='ridgid', maker='RIDGID', type='power tool', access='link', library='https://www.ridgid.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='metabo-hpt', maker='Metabo HPT', type='power tool', access='link', library='https://www.metabo-hpt.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='festool', maker='Festool', type='power tool', access='link', library='https://www.festoolusa.com/service', reason='its terms of use (read 2026-11-21) speak of deep-link, so nothing is read'),
    dict(key='porter-cable', maker='PORTER-CABLE', type='power tool', access='link', library='https://www.portercable.com/support', reason='its terms of use (read 2026-11-21) speak of data mining, robot, so nothing is read'),
    dict(key='kobalt', maker='Kobalt', type='power tool', access='link', library='https://www.kobalttools.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
    dict(key='hart', maker='HART', type='power tool', access='link', library='https://www.harttools.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
]
_OUTDOOR = [
    dict(key='ego', maker='EGO', type='outdoor power', access='link', library='https://egopowerplus.com/support', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='greenworks', maker='Greenworks', type='outdoor power', access='link', library='https://www.greenworkstools.com/pages/support', reason='its terms of use (read 2026-11-21) speak of artificial intelligence, data mining, robot, spider, so nothing is read'),
    dict(key='stihl', maker='STIHL', type='outdoor power', access='link', library='https://www.stihlusa.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='husqvarna', maker='Husqvarna', type='outdoor power', access='link', library='https://www.husqvarna.com/us/support/manuals', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='echo', maker='ECHO', type='outdoor power', access='link', library='https://www.echo-usa.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='toro', maker='Toro', type='outdoor power', access='link', library='https://www.toro.com/en/customer-support', reason='its terms of use (read 2026-11-21) speak of robot, so nothing is read'),
    dict(key='honda-pe', maker='Honda Power Equipment', type='outdoor power', access='link', library='https://powerequipment.honda.com/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='champion', maker='Champion Power Equipment', type='generator', access='link', library='https://www.championpowerequipment.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='generac', maker='Generac', type='generator', access='link', library='https://www.generac.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='troy-bilt', maker='Troy-Bilt', type='outdoor power', access='link', library='https://www.troybilt.com/en_US/manuals', reason='its terms of use (read 2026-11-21) speak of data mining, robot, so nothing is read'),
    dict(key='cub-cadet', maker='Cub Cadet', type='outdoor power', access='link', library='https://www.cubcadet.com/en_US/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='ariens', maker='Ariens', type='outdoor power', access='link', library='https://www.ariens.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
]
_HAND = [
    dict(key='stanley', maker='STANLEY', type='hand tool', access='link', library='https://www.stanleytools.com/support', reason='its terms of use (read 2026-11-21) speak of data mining, robot, so nothing is read'),
    dict(key='klein', maker='Klein Tools', type='hand tool', access='link', library='https://www.kleintools.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='irwin', maker='IRWIN', type='hand tool', access='link', library='https://www.irwin.com/', reason='its terms of use (read 2026-11-21) speak of data mining, robot, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='fluke', maker='Fluke', type='meter', access='link', library='https://www.fluke.com/en-us/support/manuals', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='wera', maker='Wera', type='hand tool', access='link', library='https://products.wera.de/en/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
]
_DOOR = [
    dict(key='kwikset', maker='Kwikset', type='lock', access='link', library='https://www.kwikset.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='schlage', maker='Schlage', type='lock', access='link', library='https://www.schlage.com/en/home/support.html', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='baldwin', maker='Baldwin Hardware', type='lock', access='link', library='https://www.baldwinhardware.com/support', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='weiser', maker='Weiser', type='lock', access='link', library='https://www.weiserlock.com/en/support', reason='robots.txt allows its support page, but its installation guides are on a file host (weiserlock.blob.core.windows.net) whose robots.txt cannot be read (HTTP 400), so nothing is read (2026-11-21)'),
    dict(key='yale', maker='Yale (Yale Home)', type='lock', access='link', library='https://shopyalehome.com/pages/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='master-lock', maker='Master Lock', type='lock', access='link', library='https://www.masterlock.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='lcn', maker='LCN (door closers, Allegion)', type='door closer', access='link', library='https://us.allegion.com/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='national-hardware', maker='National Hardware', type='door hardware', access='link', library='https://www.natman.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
]
_CABINET = [
    dict(key='blum', maker='Blum', type='cabinet hardware', access='link', library='https://www.blum.com/us/en/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='hettich', maker='Hettich', type='cabinet hardware', access='link', library='https://web.hettich.com/en-us/', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='amerock', maker='Amerock', type='cabinet hardware', access='link', library='https://www.amerock.com/', reason='the site refuses programs (HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='liberty-hardware', maker='Liberty Hardware', type='cabinet hardware', access='link', library='https://www.libertyhardware.com/support', reason='its terms of use (read 2026-11-21) speak of harvest, robot, scrape, spider, so nothing is read'),
    dict(key='accuride', maker='Accuride', type='drawer slide', access='link', library='https://www.accuride.com/en-us/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='grass', maker='Grass America', type='cabinet hardware', access='link', library='https://www.grassusa.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
    dict(key='salice', maker='Salice America', type='cabinet hardware', access='link', library='https://www.saliceamerica.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
]
_FASTENER = [
    dict(key='simpson', maker='Simpson Strong-Tie', type='connector', access='link', library='https://www.strongtie.com/resources', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='hillman', maker='Hillman', type='fastener', access='link', library='https://www.hillmangroup.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='grk', maker='GRK Fasteners', type='fastener', access='link', library='https://www.grkfasteners.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='spax', maker='SPAX', type='fastener', access='link', library='https://www.spax.us/resources', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='tapcon', maker='Tapcon (ITW Red Head)', type='anchor', access='link', library='https://www.itwredhead.com/resources', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='toggler', maker='TOGGLER', type='anchor', access='link', library='https://www.toggler.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='fastenmaster', maker='FastenMaster', type='fastener', access='link', library='https://www.fastenmaster.com/resources', reason='its terms of use (read 2026-11-21) speak of bot, so nothing is read'),
]
_PLUMBING = [
    dict(key='sharkbite', maker='SharkBite', type='plumbing fitting', access='link', library='https://www.sharkbite.com/us/en/resources', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='uponor', maker='Uponor', type='plumbing fitting', access='link', library='https://www.uponor.com/en-us/resources', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='moen', maker='Moen', type='faucet', access='link', library='https://www.moen.com/customer-support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='delta', maker='Delta Faucet', type='faucet', access='link', library='https://www.deltafaucet.com/customer-support', reason='its terms of use (read 2026-11-21) speak of artificial intelligence, harvest, robot, scrape, spider, so nothing is read'),
    dict(key='fluidmaster', maker='Fluidmaster', type='toilet part', access='link', library='https://www.fluidmaster.com/', reason='the site refuses programs (robots.txt answered HTTP 429); its manual library address was not confirmed, so its home page is linked'),
    dict(key='korky', maker='Korky', type='toilet part', access='link', library='https://www.korky.com/support', reason='its terms of use (read 2026-11-21) speak of robot, scrape, spider, so nothing is read'),
    dict(key='viega', maker='Viega', type='plumbing fitting', access='link', library='https://www.viega.us/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='nibco', maker='NIBCO', type='plumbing fitting', access='link', library='https://www.nibco.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='kohler', maker='Kohler', type='faucet', access='link', library='https://www.kohler.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
]
_ELECTRICAL = [
    dict(key='leviton', maker='Leviton', type='wiring device', access='link', library='https://leviton.com/support', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='lutron', maker='Lutron', type='wiring device', access='link', library='https://www.lutron.com/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='eaton', maker='Eaton', type='breaker', access='link', library='https://www.eaton.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
    dict(key='square-d', maker='Square D (Schneider Electric)', type='breaker', access='link', library='https://www.se.com/us/en/download/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='legrand', maker='Legrand (Pass & Seymour)', type='wiring device', access='link', library='https://www.legrand.us/resources', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='hubbell', maker='Hubbell', type='wiring device', access='link', library='https://www.hubbell.com/hubbell/en', reason='its terms of use (read 2026-11-21) speak of automated software, crawl, harvesting, scrape, spider, so nothing is read'),
    dict(key='ideal', maker='IDEAL Electrical', type='electrical tool', access='link', library='https://www.idealind.com/', reason='its terms of use (read 2026-11-21) speak of automated program, automated script, bot, crawler, deep-link, harvest, robot, spider, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='greenlee', maker='Greenlee', type='electrical tool', access='link', library='https://www.greenlee.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='southwire', maker='Southwire', type='electrical tool', access='link', library='https://www.southwire.com/resources', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
]
_GARAGE = [
    dict(key='liftmaster', maker='LiftMaster', type='garage door opener', access='link', library='https://www.liftmaster.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='chamberlain', maker='Chamberlain', type='garage door opener', access='link', library='https://www.chamberlain.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='genie', maker='Genie', type='garage door opener', access='link', library='https://www.geniecompany.com/support', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='clopay', maker='Clopay', type='garage door', access='link', library='https://www.clopaydoor.com/support', reason='its terms of use have no rule against programs, but the robots.txt of its file host literature.clopay.com disallows PDF files, so nothing is read (2026-11-21)'),
    dict(key='skylink', maker='SkyLink', type='garage door opener', access='link', library='https://www.skylinkhome.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
]
_WOOD = [
    dict(key='powermatic', maker='Powermatic', type='woodworking machine', access='link', library='https://www.powermatic.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='jet', maker='JET', type='woodworking machine', access='link', library='https://www.jettools.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='grizzly', maker='Grizzly Industrial', type='woodworking machine', access='link', library='https://www.grizzly.com/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='delta-machinery', maker='Delta Machinery', type='woodworking machine', access='link', library='https://www.deltamachinery.com/', reason='its robots.txt says ai-train=no, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='sawstop', maker='SawStop', type='table saw', access='link', library='https://www.sawstop.com/support/manuals', reason='its robots.txt says ai-train=no, so nothing is read'),
    dict(key='laguna', maker='Laguna Tools', type='woodworking machine', access='link', library='https://lagunatools.com/manuals', reason='its terms of use (read 2026-11-21) speak of artificial intelligence, machine learning, so nothing is read'),
    dict(key='rikon', maker='RIKON Power Tools', type='woodworking machine', access='read', library='https://rikontools.com/support', pages=['https://rikontools.com/support'], hosts=['rikontools.com'], reason='robots.txt allows the page; its terms and conditions (rikontools.com/terms-and-conditions) have no rule against programs (read 2026-11-21)'),
    dict(key='shop-fox', maker='Shop Fox (Woodstock International)', type='woodworking machine', access='link', library='https://www.shopfox.biz/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='harvey', maker='Harvey Woodworking', type='woodworking machine', access='link', library='https://www.harveywoodworking.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='carbide3d', maker='Carbide 3D (Shapeoko)', type='cnc', access='link', library='https://carbide3d.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='glowforge', maker='Glowforge', type='laser cutter', access='link', library='https://glowforge.com/support', reason='its terms forbid access by automated means it has not authorized'),
    dict(key='kreg', maker='Kreg Tool', type='jig', access='link', library='https://www.kregtool.com/support', reason='its terms of use (read 2026-11-21) speak of deep linking, robot, spider, so nothing is read'),
]
_METAL = [
    dict(key='lincoln', maker='Lincoln Electric', type='welder', access='link', library='https://www.lincolnelectric.com/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='miller', maker='Miller Electric', type='welder', access='link', library='https://www.millerwelds.com/support', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='hobart', maker='Hobart Welders', type='welder', access='link', library='https://www.hobartwelders.com/support', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='esab', maker='ESAB', type='welder', access='link', library='https://esab.com/us/nam_en/support/', reason='its terms of use (read 2026-11-21) speak of data mining, robot, so nothing is read'),
    dict(key='hypertherm', maker='Hypertherm', type='plasma cutter', access='link', library='https://www.hypertherm.com/en-US/support/', reason='its terms of use (read 2026-11-21) speak of robot, so nothing is read'),
    dict(key='everlast', maker='Everlast Welders', type='welder', access='link', library='https://www.everlastgenerators.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='victor', maker='Victor (ESAB)', type='torch', access='link', library='https://esab.com/', reason='its terms of use (read 2026-11-21) speak of data mining, robot, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='harbor-freight', maker='Harbor Freight Tools', type='tool', access='link', library='https://www.harborfreight.com/', reason='the site refuses programs (HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='south-bend', maker='South Bend Lathe', type='machine tool', access='link', library='https://www.southbendlathe.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='clausing', maker='Clausing Industrial', type='machine tool', access='link', library='https://www.clausing-industrial.com/manuals', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='bridgeport', maker='Bridgeport (Hardinge)', type='machine tool', access='link', library='https://www.hardinge.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='tormach', maker='Tormach', type='machine tool', access='link', library='https://tormach.com/support', reason='its terms of use (read 2026-11-21) speak of robot, so nothing is read'),
    dict(key='starrett', maker='Starrett', type='measuring tool', access='link', library='https://www.starrett.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='mitutoyo', maker='Mitutoyo America', type='measuring tool', access='link', library='https://www.mitutoyo.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
]
_AUTO = [
    dict(key='noco', maker='NOCO', type='jump starter', access='link', library='https://no.co/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='schumacher', maker='Schumacher Electric', type='battery charger', access='link', library='https://www.batterychargers.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='clore', maker='Clore Automotive (Jump-N-Carry, Solar)', type='battery charger', access='link', library='https://www.cloreautomotive.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='autel', maker='Autel', type='obd scanner', access='link', library='https://www.autel.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='innova', maker='Innova', type='obd scanner', access='link', library='https://www.innova.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='arcan', maker='Arcan', type='jack', access='link', library='https://www.arcan.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='torin', maker='Big Red (Torin)', type='jack', access='link', library='https://www.torinjacks.com/support', reason='its terms of use (read 2026-11-21) speak of crawl, scrape, spider, so nothing is read'),
]
_TRADE = [
    dict(key='fieldpiece', maker='Fieldpiece', type='hvac tool', access='link', library='https://www.fieldpiece.com/support', reason='its terms of use (read 2026-11-21) speak of artificial intelligence, crawler, data mining, machine learning, robot, scrape, spider, so nothing is read'),
    dict(key='yellow-jacket', maker='Yellow Jacket (Ritchie Engineering)', type='hvac tool', access='link', library='https://www.yellowjacket.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='general-pipe', maker='General Pipe Cleaners', type='drain machine', access='link', library='https://www.drainbrain.com/', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='spartan', maker='Spartan Tool', type='drain machine', access='link', library='https://www.spartantool.com/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
]
_MASONRY = [
    dict(key='marshalltown', maker='MARSHALLTOWN', type='masonry tool', access='link', library='https://www.marshalltown.com/', reason='its terms of use (read 2026-11-21) speak of data mining, robot, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='kraft', maker='Kraft Tool', type='masonry tool', access='link', library='https://www.krafttool.com/manuals', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='qep', maker='QEP', type='tile tool', access='link', library='https://www.qep.com/support', reason='its terms of use (read 2026-11-21) speak of scraper, so nothing is read'),
    dict(key='mk-diamond', maker='MK Diamond', type='tile saw', access='link', library='https://www.mkdiamond.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
]
_PAINT = [
    dict(key='graco', maker='Graco', type='sprayer', access='link', library='https://www.graco.com/us/en/homeowner/support.html', reason='its robots.txt says ai-train=no, so nothing is read'),
    dict(key='wagner', maker='Wagner SprayTech', type='sprayer', access='link', library='https://www.wagnerspraytech.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='titan', maker='Titan Tool', type='sprayer', access='link', library='https://www.titantool.com/manuals', reason='its terms of use forbid any robot, spider, scraper or other data-mining technology'),
    dict(key='tapetech', maker='TapeTech', type='drywall tool', access='link', library='https://www.tapetech.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='telpro', maker='Telpro (Panelift)', type='drywall lift', access='link', library='https://www.telproinc.com/', reason='its terms of use (read 2026-11-21) speak of crawl, scrape, spider, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
]
_LADDER = [
    dict(key='werner', maker='Werner', type='ladder', access='link', library='https://www.wernerco.com/us/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='little-giant', maker='Little Giant Ladder Systems', type='ladder', access='link', library='https://www.littlegiantladders.com/support', reason='its terms of use (read 2026-11-21) speak of scraper, so nothing is read'),
    dict(key='louisville', maker='Louisville Ladder', type='ladder', access='link', library='https://www.louisvilleladder.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
]
_HANDLING = [
    dict(key='harper', maker='Harper Trucks', type='hand truck', access='link', library='https://www.harpertrucks.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='magliner', maker='Magliner', type='hand truck', access='link', library='https://www.magliner.com/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='maasdam', maker="Maasdam (Pow'R Pull)", type='come-along', access='link', library='https://www.maasdam.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
    dict(key='cm', maker='Columbus McKinnon (CM hoists)', type='hoist', access='link', library='https://www.columbusmckinnon.com/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
]
_SEWING = [
    dict(key='singer', maker='SINGER', type='sewing machine', access='link', library='https://www.singer.com/pages/manuals', reason='its terms of use forbid any robot, spider or other automatic device'),
    dict(key='brother', maker='Brother (sewing)', type='sewing machine', access='link', library='https://support.brother.com/g/b/productsearch.aspx?c=us&lang=en&content=ml', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='janome', maker='Janome', type='sewing machine', access='link', library='https://www.janome.com/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='juki', maker='JUKI', type='sewing machine', access='link', library='https://www.jukihome.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='bernina', maker='BERNINA', type='sewing machine', access='link', library='https://www.bernina.com/en-US/Support', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='baby-lock', maker='Baby Lock', type='sewing machine', access='link', library='https://babylock.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='pfaff', maker='PFAFF', type='sewing machine', access='link', library='https://www.pfaff.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
    dict(key='fiskars', maker='Fiskars', type='cutting tool', access='link', library='https://www.fiskars.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
]
_KITCHEN = [
    dict(key='kitchenaid', maker='KitchenAid', type='mixer', access='link', library='https://www.kitchenaid.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
    dict(key='hobart-food', maker='Hobart (food equipment)', type='commercial kitchen', access='link', library='https://www.hobartcorp.com/', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='anova', maker='Anova', type='sous vide', access='link', library='https://anovaculinary.com/', reason='its terms of use (read 2026-11-21) speak of crawl, scrape, spider, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='breville', maker='Breville', type='kitchen appliance', access='link', library='https://www.breville.com/us/en/support.html', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read'),
    dict(key='vollrath', maker='Vollrath', type='commercial kitchen', access='link', library='https://www.vollrath.com/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='waring', maker='Waring Commercial', type='commercial kitchen', access='link', library='https://www.waringcommercialproducts.com/', reason='the site refuses programs (no answer to programs); its manual library address was not confirmed, so its home page is linked'),
    dict(key='berkel', maker='Berkel', type='slicer', access='link', library='https://www.berkelequipment.com/', reason='its terms of use (read 2026-11-21) speak of harvesting, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
]
_ACCESS = [
    dict(key='aph', maker='American Printing House (APH)', type='accessible tool', access='link', library='https://www.aph.org/resources/', reason='its terms of use (read 2026-11-21) speak of artificial intelligence, harvest, robot, scrape, spider, so nothing is read'),
    dict(key='maxiaids', maker='MaxiAids', type='accessible tool', access='link', library='https://www.maxiaids.com/', reason='the site refuses programs (robots.txt answered HTTP 202); its manual library address was not confirmed, so its home page is linked'),
    dict(key='ilaids', maker='Independent Living Aids', type='accessible tool', access='link', library='https://www.independentliving.com/', reason='only a few manual files were found on its support pages (read 2026-11-21); its manuals are on product pages, so nothing is read; its manual library address was not confirmed, so its home page is linked'),
    dict(key='lssproducts', maker='LS&S Products', type='accessible tool', access='link', library='https://www.lssproducts.com/', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read; its manual library address was not confirmed, so its home page is linked"),
]
_PPE = [
    dict(key='3m', maker='3M (respirators, hearing, fall protection)', type='ppe', access='link', library='https://www.3m.com/', reason='the site refuses programs (robots.txt answered HTTP 403); its manual library address was not confirmed, so its home page is linked'),
    dict(key='honeywell', maker='Honeywell Safety', type='ppe', access='link', library='https://sps.honeywell.com/us/en/support/safety', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='msa', maker='MSA Safety', type='ppe', access='link', library='https://us.msasafety.com/resources', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
    dict(key='moldex', maker='Moldex', type='ppe', access='link', library='https://www.moldex.com/support', reason='its robots.txt says ai-train=no, so nothing is read'),
    dict(key='ansell', maker='Ansell', type='ppe', access='link', library='https://www.ansell.com/us/en/support', reason="no manual files were found in the HTML of its support pages (read 2026-11-21), so nothing is read"),
]


def _guide(ia, title, by, year, military=False):
    """One public-domain guide: an Internet Archive item, its title, who wrote it, its year, and whether it is a
    military training manual (whose front text must say it is approved for public release)."""
    return dict(ia=ia, title=title, by=by, year=year, military=military)


GUIDES = {
    "hand_and_power_tools": _guide("DTIC_ADA400353", "Hand and Power Tools (OSHA 3080, 1998)",
                                   "the US Occupational Safety and Health Administration", 1998),
    "machine_safeguarding": _guide("DTIC_ADA400219", "Concepts and Techniques of Machine Safeguarding (OSHA 3067, "
                                   "1992)", "the US Occupational Safety and Health Administration", 1992),
    "amputations": _guide("DTIC_ADA400603", "Safeguarding Equipment and Protecting Workers from Amputations (OSHA "
                          "3170, 2001)", "the US Occupational Safety and Health Administration", 2001),
    "fall_protection": _guide("DTIC_ADA400348", "Fall Protection in Construction (OSHA 3146, 1998)",
                              "the US Occupational Safety and Health Administration", 1998),
    "ppe": _guide("DTIC_ADA400241", "Assessing the Need for Personal Protective Equipment: A Guide for Small Business "
                  "Employers (OSHA 3151, 2000)", "the US Occupational Safety and Health Administration", 2000),
    "electrical_hazards": _guide("DTIC_ADA400134", "Controlling Electrical Hazards (OSHA 3075, 1997)",
                                 "the US Occupational Safety and Health Administration", 1997),
    "tools_and_their_uses": _guide("ERIC_ED132362", "Tools and Their Uses, Rate Training Manual (US Navy, 1971)",
                                   "the US Navy", 1971, True),
    "machine_tools": _guide("tc9-524", "Fundamentals of Machine Tools (TC 9-524, 1996)", "the US Army", 1996, True),
    "machinist_1941": _guide("TM10-445", "The Machinist (TM 10-445, 1941)", "the US Army", 1941, True),
    "lathe_course": _guide("US_Army_machinist_course_Lathe_Operations_OD1645", "Lathe Operations (US Army machinist "
                           "course OD1645)", "the US Army", None, True),
    "milling_course": _guide("US_Army_machinist_course_Milling_Machine_Operations_OD1644", "Milling Machine "
                             "Operations (US Army machinist course OD1644)", "the US Army", None, True),
    "band_saw_course": _guide("US_Army_machinist_course_Band_Saw_Operations_OD1646", "Band Saw Operations (US Army "
                              "machinist course OD1646)", "the US Army", None, True),
    "machinery_repairman": _guide("machinery-repairman_20200118", "Machinery Repairman (US Navy training manual, "
                                  "1993)", "the US Navy", 1993, True),
    "welding_theory": _guide("TM9-237", "Welding Theory and Application (TM 9-237, 1967)", "the US Army", 1967, True),
    "steelworker_1": _guide("steelworker1", "Steelworker, Volume 1 (US Navy NAVEDTRA 14250, 1996)", "the US Navy",
                            1996, True),
    "steelworker_2": _guide("steelworker2", "Steelworker, Volume 2 (US Navy NAVEDTRA 14251, 1996)", "the US Navy",
                            1996, True),
}

# Official pages linked for the person to open (their sites refuse programs or are not read).
LINKS = {
    "osha_tools": dict(title="Hand and power tools (OSHA)", url="https://www.osha.gov/hand-power-tools",
                       by="the US Occupational Safety and Health Administration"),
    "osha_machines": dict(title="Machine guarding (OSHA)", url="https://www.osha.gov/machine-guarding",
                          by="the US Occupational Safety and Health Administration"),
    "osha_welding": dict(title="Welding, cutting and brazing (OSHA)", url="https://www.osha.gov/welding-cutting-brazing",
                         by="the US Occupational Safety and Health Administration"),
    "niosh_welding": dict(title="Welding and manganese (NIOSH)", url="https://www.cdc.gov/niosh/topics/welding/",
                          by="the US National Institute for Occupational Safety and Health"),
    "osha_ladders": dict(title="Ladders (OSHA)", url="https://www.osha.gov/ladders",
                         by="the US Occupational Safety and Health Administration"),
    "osha_fall": dict(title="Fall protection (OSHA)", url="https://www.osha.gov/fall-protection",
                      by="the US Occupational Safety and Health Administration"),
    "osha_ppe": dict(title="Personal protective equipment (OSHA)", url="https://www.osha.gov/personal-protective-equipment",
                     by="the US Occupational Safety and Health Administration"),
    "niosh_respirators": dict(title="Respirators: how to choose and use them (NIOSH)",
                              url="https://www.cdc.gov/niosh/ppe/", by="the US National Institute for Occupational "
                                                                        "Safety and Health"),
    "niosh_hearing": dict(title="Noise and hearing loss (NIOSH)", url="https://www.cdc.gov/niosh/noise/",
                          by="the US National Institute for Occupational Safety and Health"),
    "osha_electrical": dict(title="Electrical safety (OSHA)", url="https://www.osha.gov/electrical",
                            by="the US Occupational Safety and Health Administration"),
    "wood_handbook": dict(title="Wood Handbook: Wood as an Engineering Material (chapter 8: fastenings)",
                          url="https://www.fpl.fs.usda.gov/products/publications/specific_pub.php?posting_id=18102",
                          by="the US Forest Products Laboratory"),
    "fema_earthquake_home": dict(title="Earthquake Safety at Home (FEMA P-530): anchoring furniture, shelves and water "
                                       "heaters", url="https://www.fema.gov/emergency-managers/risk-management/"
                                                      "earthquake/training/home", by="the US Federal Emergency "
                                                                                     "Management Agency"),
    "fema_wind": dict(title="Wind Retrofit Guide for Residential Buildings (FEMA P-804): connectors and straps",
                      url="https://www.fema.gov/emergency-managers/risk-management/building-science/hurricanes",
                      by="the US Federal Emergency Management Agency"),
    "osha_garage": dict(title="Garage door safety (US Consumer Product Safety Commission)",
                        url="https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Garage-Doors-and-Openers",
                        by="the US Consumer Product Safety Commission"),
}

# The safety notices, said first by the toolkit with each category.
POWER_NOTICE = ("Read the safety section first. Wear eye protection, and hearing protection for loud tools; unplug the "
                "tool or take out its battery before changing a blade or bit; keep guards in place.")
MACHINE_NOTICE = ("Read the safety section first. Never reach near a moving blade or cutter; use the guards, push "
                  "sticks and push blocks; unplug the machine before adjusting it; wear eye and hearing protection; "
                  "no gloves, loose sleeves or jewellery near turning parts.")
WELD_NOTICE = ("Read the safety section first. An arc burns the eyes and skin: wear a welding helmet, gloves and "
               "covered skin; weld only with good ventilation (the fumes are harmful); keep a fire extinguisher close "
               "and the gas cylinders chained upright.")
ELECTRIC_NOTICE = ("Read the safety section first. Turn off the breaker and check with a tester that the circuit is "
                   "dead before touching any wire; where local rules require it, have a licensed electrician do the "
                   "work.")
LADDER_NOTICE = ("Read the safety labels first: the weight rating, the angle, and never standing on the top step or cap. "
                 "Never stand under a load being lifted.")
PPE_NOTICE = ("Protective equipment protects only when it is the right kind for the hazard and fits; read its label, and "
              "for respirators the fit instructions.")
GARAGE_NOTICE = ("Read the safety section first. Garage door springs and their cables are under great tension: "
                 "adjusting or replacing them is a job for a trained technician.")
AUTO_NOTICE = ("Read the safety section first. Never work under a vehicle held only by a jack: use jack stands on firm "
               "ground. Battery chargers and jump starters: connect in the order the manual gives.")
GENERAL_NOTICE = "Read the safety and warnings section first."

_LIC = "CC0 (facts and links); each manual belongs to its maker; the public-domain guides are US government works"


def _cat(name, description, makers, ia=(), notice=GENERAL_NOTICE, guides=(), links=(), **extra):
    """One manuals category of this module."""
    return dict(name=name, description=description, kind="manuals", licence=_LIC, ia=list(ia), makers=makers,
                notice=notice, public_guides=[GUIDES[g] for g in guides], guidance=[LINKS[k] for k in links], **extra)


CATEGORIES = {
    "door_hardware_locks": _cat(
        "Door hardware and locks (installation instructions)",
        "Door locks, deadbolts, smart and keypad locks, knobs and levers, door closers and padlocks: the makers' own "
        "installation instructions and manuals (Kwikset, Schlage, Baldwin, Weiser, Yale, Master Lock and others).",
        _makers("door_hardware_locks", _DOOR),
        ["deadbolt", "door lock", "smart lock", "keypad lock", "door closer", "padlock", "lever set", "kwikset",
         "schlage"]),
    "cabinet_hardware": _cat(
        "Cabinet and furniture hardware (installation instructions)",
        "Cabinet hinges, drawer slides, pulls and knobs and furniture fittings: Blum, Hettich, Amerock, Liberty, "
        "Accuride, Grass and Salice installation instructions.",
        _makers("cabinet_hardware", _CABINET), ["drawer slide", "cabinet hinge", "concealed hinge"]),
    "fasteners_anchors": _cat(
        "Fasteners, anchors and structural connectors (installation guides)",
        "Screws, anchors and structural connectors: Simpson Strong-Tie, Hillman, GRK, SPAX, Tapcon, TOGGLER and "
        "FastenMaster, with the public guides on fastenings and anchoring (Wood Handbook, FEMA).",
        _makers("fasteners_anchors", _FASTENER), ["anchor", "fastener", "joist hanger"],
        links=["wood_handbook", "fema_earthquake_home", "fema_wind"]),
    "plumbing_fittings": _cat(
        "Plumbing fittings, faucets and toilet parts (installation instructions)",
        "Push-fit and PEX fittings, valves, faucets, showers and toilet fill and flush valves: SharkBite, Uponor, "
        "Moen, Delta, Fluidmaster, Korky, Viega, NIBCO and Kohler.",
        _makers("plumbing_fittings", _PLUMBING), ["faucet", "toilet", "fill valve", "shower valve", "pex"],
        notice="Read the safety section first. Turn off the water supply before you start, and the power or gas to a "
               "water heater."),
    "electrical_devices": _cat(
        "Electrical devices: outlets, switches, dimmers and breakers (installation instructions)",
        "Outlets, GFCI outlets, switches, dimmers, timers and circuit breakers: Leviton, Lutron, Eaton, Square D, "
        "Legrand and Hubbell, with OSHA's guide to controlling electrical hazards.",
        _makers("electrical_devices", _ELECTRICAL),
        ["dimmer", "gfci", "outlet", "timer switch", "circuit breaker", "load center"], ELECTRIC_NOTICE,
        ["electrical_hazards"], ["osha_electrical"]),
    "garage_doors": _cat(
        "Garage doors and openers (manuals and installation instructions)",
        "Garage doors, their hardware and openers: LiftMaster, Chamberlain, Genie, Clopay and SkyLink (the Internet "
        "Archive's garage door opener manuals are in the collection Around the house).",
        _makers("garage_doors", _GARAGE), [], GARAGE_NOTICE, links=["osha_garage"]),
    "woodshop_machines": _cat(
        "Woodshop machines (manuals)",
        "Jointers, planers, band saws, drill presses, lathes, scroll saws, sanders, dust collectors, router tables, "
        "mortisers, CNC routers, laser cutters and jigs: Powermatic, JET, Grizzly, Delta, SawStop, Laguna, RIKON, "
        "Shop Fox, Harvey, Carbide 3D, Glowforge and Kreg, with OSHA's machine-guarding guides.",
        _makers("woodshop_machines", _WOOD),
        ["jointer", "planer", "band saw", "bandsaw", "drill press", "wood lathe", "scroll saw", "dust collector",
         "router table", "mortiser", "shaper", "cnc router", "laser engraver", "laser cutter"],
        MACHINE_NOTICE, ["machine_safeguarding", "amputations"], ["osha_machines"]),
    "metal_shop_welding": _cat(
        "Metal shop machines and welding (manuals and training manuals)",
        "Welders (MIG, TIG, stick, flux-core), plasma cutters, torches, metal lathes, milling machines, grinders, saws, "
        "presses and precision measuring tools: Lincoln Electric, Miller, Hobart, ESAB, Hypertherm, Everlast, Victor, "
        "Harbor Freight, South Bend, Clausing, Bridgeport, Tormach, Starrett and Mitutoyo; and public-domain US Army "
        "and Navy machinist and welding training manuals.",
        _makers("metal_shop_welding", _METAL),
        ["welder", "mig welder", "tig welder", "plasma cutter", "metal lathe", "milling machine", "bench grinder",
         "hydraulic press", "micrometer", "machinist"], WELD_NOTICE,
        ["machine_tools", "machinist_1941", "lathe_course", "milling_course", "band_saw_course", "machinery_repairman",
         "welding_theory", "steelworker_1", "steelworker_2", "machine_safeguarding"],
        ["osha_welding", "niosh_welding", "osha_machines"]),
    "automotive_shop": _cat(
        "Automotive shop tools (manuals)",
        "Jacks and jack stands, battery chargers and jump starters, OBD scanners and code readers, tyre tools and "
        "engine hoists: NOCO, Schumacher, Clore, Autel, Innova, Arcan and Big Red.",
        _makers("automotive_shop", _AUTO),
        ["floor jack", "jack stand", "battery charger", "jump starter", "obd", "code reader", "engine hoist",
         "tire changer"], AUTO_NOTICE),
    "trade_tools": _cat(
        "HVAC, plumbing and electrical trade tools (manuals)",
        "Manifold gauges, vacuum pumps, drain cleaning machines, pipe threaders and press tools, clamp meters, cable "
        "pullers, conduit benders and crimpers: Fieldpiece, Yellow Jacket, General Pipe Cleaners, Spartan, Greenlee, "
        "IDEAL and Southwire.",
        _makers("trade_tools", _TRADE + [m for m in _ELECTRICAL if m["key"] in ("ideal", "greenlee", "southwire")]),
        ["manifold gauge", "refrigerant", "vacuum pump", "drain cleaning", "drain cleaner", "pipe threader",
         "clamp meter", "cable puller", "conduit bender", "crimper"], ELECTRIC_NOTICE, ["electrical_hazards"]),
    "masonry_paint_drywall": _cat(
        "Masonry, tile, painting and drywall tools (manuals)",
        "Concrete mixers, tile saws, paint sprayers, drywall lifts and texture sprayers: MARSHALLTOWN, Kraft Tool, "
        "QEP, MK Diamond, Graco, Wagner, Titan, TapeTech and Telpro.",
        _makers("masonry_paint_drywall", _MASONRY + _PAINT),
        ["paint sprayer", "airless sprayer", "tile saw", "concrete mixer", "cement mixer", "drywall lift",
         "texture sprayer"],
        "Read the safety section first. An airless sprayer's spray can pierce the skin: never point it at anyone, and "
        "use the trigger lock. Wear a dust mask or respirator when cutting tile or concrete."),
    "ladders_handling": _cat(
        "Ladders, scaffolding and material handling (manuals and safety labels)",
        "Stepladders, extension and multi-position ladders, scaffolds, hand trucks, dollies, come-alongs and hoists: "
        "Werner, Little Giant, Louisville Ladder, Harper, Magliner, Maasdam and Columbus McKinnon, with OSHA's fall "
        "protection guide.",
        _makers("ladders_handling", _LADDER + _HANDLING),
        ["ladder", "scaffold", "hand truck", "come along", "chain hoist", "winch"], LADDER_NOTICE,
        ["fall_protection"], ["osha_ladders", "osha_fall"]),
    "sewing_textile": _cat(
        "Sewing machines, sergers and textile tools (manuals)",
        "Sewing machines, sergers, embroidery and quilting machines and cutting tools: SINGER, Brother, Janome, JUKI, "
        "BERNINA, Baby Lock, PFAFF and Fiskars (the Internet Archive's sewing machine manuals are in Around the "
        "house).",
        _makers("sewing_textile", _SEWING), ["serger", "overlock", "embroidery machine", "quilting machine",
                                              "coverstitch"]),
    "kitchen_equipment": _cat(
        "Kitchen and food preparation equipment, home and commercial (manuals)",
        "Stand mixers, meat slicers and grinders, sous-vide cookers, vacuum sealers and commercial kitchen equipment: "
        "KitchenAid, Hobart, Anova, Breville, Vollrath, Waring and Berkel (small appliances such as toasters and "
        "blenders are in Small kitchen appliances).",
        _makers("kitchen_equipment", _KITCHEN),
        ["sous vide", "meat slicer", "meat grinder", "vacuum sealer", "stand mixer", "dehydrator", "commercial"],
        "Read the safety section first. Slicer and grinder blades are very sharp: unplug before cleaning and keep the "
        "guards on."),
    "accessible_tools": _cat(
        "Accessible tools for blind and low-vision people (manuals)",
        "Talking tape measures, tactile and audible levels, talking multimeters and thermometers, click rules and "
        "braille-marked tools: American Printing House, MaxiAids, Independent Living Aids and LS&S.",
        _makers("accessible_tools", _ACCESS),
        ["talking tape", "tactile", "click rule", "braille ruler", "talking multimeter", "audible level"]),
    "safety_ppe": _cat(
        "Personal protective equipment (instructions and guides)",
        "Respirators by class, hearing protection, safety glasses, gloves and fall protection harnesses: 3M, Honeywell, "
        "MSA, Moldex and Ansell, with OSHA's and NIOSH's guides.",
        _makers("safety_ppe", _PPE), ["respirator", "hearing protection", "fall arrest", "safety harness"],
        PPE_NOTICE, ["ppe", "fall_protection"], ["osha_ppe", "niosh_respirators", "niosh_hearing", "osha_fall"]),
}

# The existing categories this module extends: more Internet Archive words, the makers, the notice and the guides.
EXTEND = {
    "power_tools": dict(ia=["impact wrench", "oscillating", "heat gun", "air compressor", "shop vac", "wet dry vac",
                            "reciprocating saw", "band saw", "nail gun", "planer"],
                        makers=_makers("power_tools", _POWER), notice=POWER_NOTICE,
                        public_guides=[GUIDES["hand_and_power_tools"]], guidance=[LINKS["osha_tools"]]),
    "hand_tools": dict(ia=["clamp meter", "level", "socket set", "wrench set", "caliper", "laser distance"],
                       makers=_makers("hand_tools", _HAND), notice=GENERAL_NOTICE,
                       public_guides=[GUIDES["tools_and_their_uses"], GUIDES["hand_and_power_tools"]],
                       guidance=[LINKS["osha_tools"]]),
    "lawn_garden": dict(ia=["chipper", "shredder", "lawn edger", "cultivator"], makers=_makers("lawn_garden", _OUTDOOR),
                        notice="Read the safety section first. Run engines and generators only outdoors, far from "
                               "windows and doors (carbon monoxide); wear eye and hearing protection."),
}
