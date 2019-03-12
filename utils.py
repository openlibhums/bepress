import os
import logging
from bs4 import BeautifulSoup

from django.db import transaction

from plugins.bepress.plugin_settings import BEPRESS_PATH
from submission import models
from plugins.bepress import models as bepress_models

logger = logging.getLogger(__name__)


def get_bepress_import_folders():
    if os.path.exists(BEPRESS_PATH):
        return os.listdir(BEPRESS_PATH)
    else:
        return []


def get_pdf(sub_files, pdf_type):
    galley_filename = None

    if len(sub_files) > 1:
        if pdf_type == 'stamped':
            galley_filename = 'stamped.pdf'
        else:
            files = set(sub_files) - {"stamped.pdf", "metadata.xml", "auto_convert.pdf"}
            if files:
                galley_filename = next(iter(files))

    return galley_filename


def soup_metadata(metadata_path):
    logger.warning('Souping article.')
    metadata_content = open(metadata_path).read()
    return BeautifulSoup(metadata_content, "lxml")


def metadata_keywords(soup, article):
    keywords = [keyword.string for keyword in soup.find_all('keyword')]

    for keyword in keywords:
        word = models.Keyword.objects.get_or_create(word=keyword)
        article.keywords.add(word)


def metadata_section(soup, article):
    soup_section = soup.discipline.string if soup.discipline else None

    if soup_section:
        section, c = models.Section.objects.language('en').get_or_create(
            name=soup_section,
            journal=article.journal
        )
        article.section = section
    else:
        # TODO: Add some sort of default section?
        logger.warning('{article} no section found'.format(article=article.title))


@transaction.atomic
def create_article_record(soup, journal):
    try:
        bepress_models.ImportedArticle.objects.get(
            bepress_id=soup.articleid.string,
        )
        logger.warning(
            '#{id} has already been imported'.format(
                id=soup.articleid.string
            )
        )
        return
    except bepress_models.ImportedArticle.DoesNotExist:
        pass

    article = models.Article()

    article.title = soup.title.string
    article.journal = journal
    article.abstract = soup.abstract.string if soup.abstract else ''
    article.date_published = getattr(soup, 'publication-date').string
    article.date_submitted = getattr(soup, 'submission-date').string
    article.stage = models.STAGE_PUBLISHED
    metadata_section(soup, article)

    # TODO: Handle authors

    # TODO: Commented out to make development easier, uncomment when complete.
    # Currently you can't at items to a manytomany until it has an ID so
    # have commented out the keywords section
    #article.save()
    #metadata_keywords(soup, article)

    # TODO: create ImportedArticle record when done.


def add_pdf_as_galley(pdf_path):
    pass


def import_articles(folder, pdf_type, journal):
    path = os.path.join(BEPRESS_PATH, folder)
    for root, dirs, files in os.walk(path):

        if 'metadata.xml' in files:
            pdf = get_pdf(files, pdf_type)

            if not pdf and 'stamped.pdf' in files:
                pdf = 'stamped.pdf'

            metadata_path = os.path.join(root, 'metadata.xml')

            if pdf:
                pdf_path = os.path.join(root, pdf)
            else:
                pdf_path = None

            soup = soup_metadata(metadata_path)
            create_article_record(soup, journal)
            add_pdf_as_galley(pdf_path)
