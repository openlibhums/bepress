from bs4 import BeautifulSoup
from django.test import TestCase

try:
    from plugins import books
except Exception as e:
    books = None
from utils.testing import helpers

from bepress import utils

if books:
    class TestImportBook(TestCase):

        @classmethod
        def setUpTestData(cls):
            cls.press = helpers.create_press()

        def test_import_book(self):
            soup = BeautifulSoup(XML_DATA, "lxml")
            book, chapter = utils.import_book_chapter(soup, self.press)
            self.assertEqual(book.title, "Test Book")

        def test_import_chapter(self):
            soup = BeautifulSoup(XML_DATA, "lxml")
            book, chapter = utils.import_book_chapter(soup, self.press)
            self.assertEqual(chapter.title, "Test Chapter")

        def test_import_comments(self):
            soup = BeautifulSoup(XML_DATA, "lxml")
            book, chapter = utils.import_book_chapter(soup, self.press)
            comment = chapter.publisher_notes.first()
            self.assertEqual(comment.note, "Test Comments")

        def test_import_contributors(self):
            soup = BeautifulSoup(XML_DATA, "lxml")
            book, chapter = utils.import_book_chapter(soup, self.press)
            contributors = utils.import_book_contributors(soup, book, chapter)
            self.assertEqual(contributors[1].last_name, "Pike")


XML_DATA = """
<?xml version="1.0" encoding="iso-8859-1"?>
<documents xmlns="" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <document>
    <title>Test Chapter</title>
    <publication-date>2016-02-17T00:00:00-08:00</publication-date>
    <authors>
      <author>
        <email>kirk@noemail.com</email>
        <institution>OLH</institution>
        <lname>Kirk</lname>
        <fname>J.</fname>
        <mname>T.</mname>
      </author>
      <author>
        <institution>OLH</institution>
        <lname>Pike</lname>
        <fname>C.</fname>
      </author>
    </authors>
    <keywords>
      <keyword>Transporters</keyword>
      <keyword>Replicators</keyword>
    </keywords>
    <disciplines>
      <discipline>Hyposprays</discipline>
    </disciplines>
    <abstract>Test Abstract</abstract>
    <label>1</label>
    <document-type>book</document-type>
    <type>article</type>
    <articleid>1001</articleid>
    <submission-date>2015-03-12T05:39:49-07:00</submission-date>
    <publication-title>Test Book</publication-title>
    <context-key>6824795</context-key>
    <submission-path>cancer_concepts/20</submission-path>
    <fields>
      <field name="city" type="string">
        <value>Vulkan</value>
      </field>
      <field name="comments" type="string">
        <value>Test Comments</value>
      </field>
      <field name="distribution_license" type="string">
        <value>http://creativecommons.org/licenses/by-nc/4.0/</value>
      </field>
      <field name="doi" type="string">
        <value>10.1234/chapter1</value>
      </field>
      <field name="doi_link" type="string">
        <value>&lt;a href="http://doi.org/10.1234/chapter1"&gt;</value>
      </field>
      <field name="embargo_date" type="date">
        <value>2015-03-12T00:00:00-07:00</value>
      </field>
      <field name="publication_date" type="date">
        <value>2016-02-17T00:00:00-08:00</value>
      </field>
      <field name="publisher" type="string">
        <value>Test Publisher</value>
      </field>
      <field name="upload_cover_image" type="special">
        <value>use_pdf</value>
      </field>
    </fields>
  </document>
</documents>
"""

