"""A tiny made-up OpenStax-style repository (CNXML), for the tests here and in the Digital Accessibility Toolkit:
nothing in it comes from a real book.

make_sample_repo(folder) writes META-INF/books.xml, a collection with a preface, one unit holding two chapters (an
introduction and numbered sections), and modules with a figure (with its description), a table, MathML, a link to
a figure in another module, a teacher-only note (to be left out), exercises with answers, a footnote and a
glossary. Returns the folder.
"""

import os

CNXML = ('<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML"{cls}>'
         '<title>{title}</title><metadata xmlns:md="http://cnx.rice.edu/mdml"><md:content-id>{mid}</md:content-id>'
         '<md:title>{title}</md:title>{abstract}</metadata><content>{body}</content>{glossary}</document>')
MODULES = {
    "m00001": ("Preface", "", "", "<para id='p1'>Welcome to the Tiny Science book, written for tests.</para>", ""),
    "m00002": ("Introduction", " class=\"introduction\"", "",
               "<para id='p2'>This chapter is about how the kidney filters blood.</para>", ""),
    "m00003": ("The Kidney", "", "<md:abstract><para>By the end of this section, you will be able to:</para>"
               "<list><item>Describe the nephron</item></list></md:abstract>",
               "<section id='s1'><title>Filtering blood</title><para id='p3'>The <term>nephron</term> filters "
               "blood (<link target-id='fig-kidney'/>). Its rate is <m:math><m:mrow><m:mi>v</m:mi><m:mo>=</m:mo>"
               "<m:mfrac><m:mi>d</m:mi><m:mi>t</m:mi></m:mfrac></m:mrow></m:math> and water is "
               "H<sub>2</sub>O.<footnote>A made-up note.</footnote></para>"
               "<figure id='fig-kidney'><title>A kidney</title><media id='md1' alt='A bean-shaped organ with a "
               "tube leaving it.'><image mime-type='image/jpg' src='../../media/kidney.jpg'/></media>"
               "<caption>The kidney, cut in half.</caption></figure>"
               "<table id='tab-1'><title>Daily amounts</title><tgroup cols='2'><thead><row><entry>Fluid</entry>"
               "<entry>Litres</entry></row></thead><tbody><row><entry>Filtered</entry><entry>180</entry></row>"
               "</tbody></tgroup></table>"
               "<note class='os-teacher'><title>Teacher Support</title><para>SECRET TEACHER TEXT</para></note>"
               "<note class='everyday'><title>Everyday Connection</title><para>Drink water.</para></note>"
               "</section><section class='review-questions'><exercise><problem><para>What filters blood?</para>"
               "</problem><solution><para>The nephron.</para></solution></exercise></section>",
               "<glossary><definition id='d1'><term>nephron</term><meaning>the filtering unit of the kidney"
               "</meaning></definition></glossary>"),
    "m00004": ("Introduction", " class=\"introduction\"", "", "<para id='p4'>Hearts pump blood.</para>", ""),
    "m00005": ("The Heart", "", "", "<para id='p5'>The heart has four chambers, like the kidney in "
               "<link document='m00003' target-id='fig-kidney'/> has none.</para>"
               "<para id='p6'>See <link url='https://example.org/heart'>a page</link>.</para>", ""),
}
COLLECTION = """<col:collection xmlns="http://cnx.rice.edu/collxml" xmlns:md="http://cnx.rice.edu/mdml"
 xmlns:col="http://cnx.rice.edu/collxml" authors="A. Writer">
<metadata xmlns:md="http://cnx.rice.edu/mdml"><md:title>Tiny Science</md:title><md:language>en</md:language>
<md:license url="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution License</md:license>
<md:slug>tiny-science</md:slug></metadata>
<col:content><col:module document="m00001"/>
<col:subcollection><md:title>The Body</md:title><col:content>
<col:subcollection><md:title>The Urinary System</md:title><col:content>
<col:module document="m00002"/><col:module document="m00003"/></col:content></col:subcollection>
<col:subcollection><md:title>The Heart</md:title><col:content>
<col:module document="m00004"/><col:module document="m00005"/></col:content></col:subcollection>
</col:content></col:subcollection></col:content></col:collection>"""


def make_sample_repo(folder):
    """Write the made-up repository into folder (see the module docstring) and return folder."""
    os.makedirs(os.path.join(folder, "META-INF"), exist_ok=True)
    os.makedirs(os.path.join(folder, "collections"), exist_ok=True)
    os.makedirs(os.path.join(folder, "media"), exist_ok=True)
    with open(os.path.join(folder, "META-INF", "books.xml"), "w", encoding="utf-8") as f:
        f.write('<container xmlns="https://openstax.org/namespaces/book-container" version="1"><book '
                'slug="tiny-science" href="../collections/tiny-science.collection.xml"/></container>')
    with open(os.path.join(folder, "collections", "tiny-science.collection.xml"), "w", encoding="utf-8") as f:
        f.write(COLLECTION)
    for mid, (title, cls, abstract, body, glossary) in MODULES.items():
        os.makedirs(os.path.join(folder, "modules", mid), exist_ok=True)
        with open(os.path.join(folder, "modules", mid, "index.cnxml"), "w", encoding="utf-8") as f:
            f.write(CNXML.format(cls=cls, title=title, mid=mid, abstract=abstract, body=body, glossary=glossary))
    with open(os.path.join(folder, "media", "kidney.jpg"), "wb") as f:
        f.write(b"\xff\xd8\xff\xe0made-up picture")
    return folder
