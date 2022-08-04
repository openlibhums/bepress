from bs4 import BeautifulSoup
from django.test import TestCase, override_settings

from utils.testing import helpers

from plugins.bepress.utils import add_youtube_galley

class TestImportArticle(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.journal_one, cls.journal_two = helpers.create_journals()

    @override_settings(URL_CONFIG="domain")
    def test_import_youtube_galley(self):
        youtube_url = "https://youtu.be/xyz"
        article = helpers.create_article(journal=self.journal_one)
        galley = add_youtube_galley(youtube_url, article)
        galley_contents = galley.file_content(dont_render=True)
        expected = f'xlink:href="{youtube_url}"'
        self.assertTrue(expected in str(galley_contents))

