"""
Test cases for the csv_handler module
"""
from django.test import TestCase

from plugins.bepress import csv_handler

class TestFilesHandler(TestCase):
    def test_csv_to_xml(self):
        data = [TEST_ARTICLE_DATA]
        expected = TEST_ARTICLE_XML
        result_iter = csv_handler.csv_to_xml(data, commit=False)
        result, _ = next(result_iter)
        self.assertEquals(expected.replace("\n", ''), result.replace("\n",''))

    def test_parse_article_metadata(self):
        expected = {
            "keywords": ["one", "two"],
            "fulltext_url": "www.example.org",
            "language": "fr",
            "peer_reviewed": True,
        }

    def test_parse_author(self):
        data = {
            'author1_email': 'mauro_bepress@test.com',
            'author1_fname': 'Mauro',
            'author1_mname': 'M',
            'author1_lname': 'Sanchez',
            'author1_institution': 'Birkbeck Centre for Technology and Publishing',
            'author1_is_corporate': '',
        }
        expected = {
            "first_name": "Mauro",
            "middle_name": "M",
            "last_name": "Sanchez",
            "email": "mauro_bepress@test.com",
            "institution": "Birkbeck Centre for Technology and Publishing",
        }
        
        result = csv_handler.parse_authors(data)
        self.assertDictEqual(expected, result[0])

    def test_parse_corporate_author(self):
        data = {
            'author1_fname': '',
            'author1_mname': '',
            'author1_lname': '',
            'author1_institution': 'Birkbeck Centre for Technology and Publishing',
            'author1_is_corporate': 'TRUE',
        }
        expected = {
            "institution": "Birkbeck Centre for Technology and Publishing",
            "is_corporate": 'TRUE',
        }
        
        result = csv_handler.parse_authors(data)
        self.assertDictEqual(expected, result[0])

TEST_ARTICLE_DATA = {
    'title': 'The art of importing articles from bepress',
    'abstract': 'This is the abstract of my test paper',
    'acknowledgements': 'Here are some acknowledgements',
    'author1_suffix': 'Mr',
    'author1_email': 'mauro_bepress@test.com',
    'author1_fname': 'Mauro',
    'author1_mname': 'M',
    'author1_lname': 'Sanchez',
    'author1_institution': 'Birkbeck Centre for Technology and Publishing',
    'author1_is_corporate': '',
    'author2_suffix': 'Mr',
    'author2_fname': 'Andy',
    'author2_mname': 'Jr',
    'author2_lname': 'Byers',
    'author2_email': 'andy_bepress@test.com',
    'author2_institution': 'Birkbeck Centre for Technology and Publishing',
    'author2_is_corporate': '',
    'author3_email': '',
    'author3_fname': '',
    'author3_institution': '',
    'author3_is_corporate': '',
    'author3_lname': '',
    'author3_mname': '',
    'author3_suffix': '',
    'author4_email': '',
    'author4_fname': '',
    'author4_institution': '',
    'author4_is_corporate': '',
    'author4_lname': '',
    'author4_mname': '',
    'author4_suffix': '',
    'author5_email': '',
    'author5_fname': '',
    'author5_institution': '',
    'author5_is_corporate': '',
    'author5_lname': '',
    'author5_mname': '',
    'author5_suffix': '',
    'calc_url': '',
    'comments': '',
    'context_key': '123456',
    'cover_paste': '',
    'ctmtime': '1434740413',
    'disciplines': 'keyword; other keyword',
    'document_type': 'Paper',
    'embargo_date': '',
    'erratum': '',
    'fpage': 'v',
    'fulltext_url': '',
    'issue': 'journal/vol1/iss2',
    'keywords': 'Some keyword',
    'peer_reviewed': '',
    'publication_date': '1999-01-01 00:00',
 } 

TEST_ARTICLE_XML= """
<?xml version='1.0' encoding='iso-8859-1' ?>
<documents>
    <document>
        <title>The art of importing articles from bepress</title>
        <publication-date>1999-01-01 00:00</publication-date>
        <state>published</state>
        <authors>
            
            <author>
              
                <institution>Birkbeck Centre for Technology and Publishing</institution>
              
              
                <fname>Mauro</fname>
              
              
                <mname>M</mname>
              
              
                <lname>Sanchez</lname>
              
              
                <email>mauro_bepress@test.com</email>
              
            </author>
          
            <author>
              
                <institution>Birkbeck Centre for Technology and Publishing</institution>
              
              
                <fname>Andy</fname>
              
              
                <mname>Jr</mname>
              
              
                <lname>Byers</lname>
              
              
                <email>andy_bepress@test.com</email>
              
            </author>
          
        </authors>
        <disciplines>
          
            <discipline>keyword</discipline>
          
            <discipline>other keyword</discipline>
          
        </disciplines
        <abstract>This is the abstract of my test paper</abstract>
        <coverpage-url></coverpage-url>
        <fulltext-url></fulltext-url>
        <document-type>Paper</document-type>
        <type>article</type>
        <articleid>123456</articleid>
        <context-key>123456</context-key>
        <submission-path></submission-path>
        <fields>
        
        <field name="fpage" type="string">
            <value>v</value>
        </field>
        
        
        
        <field name="language" type="string">
            <value>en</value>
        </field>
        
        
        
        
        <field name="publication_date" type="date">
            <value>1999-01-01 00:00</value>
        </field>
        
        </fields>
    </document>
</documents>
"""
