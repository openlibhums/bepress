import hashlib
import logging
import os
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from django.db import transaction
from django.conf import settings
from django.core.files import File as DjangoFile
from django.db.utils import OperationalError

from core import files
from core.models import Account, Galley
from submission import models as submission_models

from plugins.bepress import models
from plugins.bepress.plugin_settings import BEPRESS_PATH

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
    logger.debug('Souping article %s' % metadata_path)
    metadata_content = open(metadata_path).read()
    return BeautifulSoup(metadata_content, "lxml")


def metadata_keywords(soup, article):
    keywords = [keyword.string for keyword in soup.find_all('keyword')]

    for keyword in keywords:
        try:
            word, _ = submission_models.Keyword.objects.get_or_create(word=keyword)
            article.keywords.add(word)
        except OperationalError as e:
            logger.warning("Couldn't add keyword %s: %s" % (keyword, e))


def metadata_section(soup, article, default_section):
    soup_section = soup.discipline.string if soup.discipline else None

    if soup_section:
        section, c = submission_models.Section.objects.language("en")\
        .get_or_create(
            name=soup_section,
            journal=article.journal
        )
        article.section = section
    elif default_section:
        article.section = default_section
    else:
        logger.warning('{article} no section found'.format(article=article.title))


def metadata_license(soup, article):
    field = soup.fields.find(attrs={"name":"distribution_license"})
    if field:
        license_url = field.value.string
        if license_url.endswith("/"):
            license_url = license_url[:-1]
        try:
            article.license = submission_models.Licence.objects.get(
                    journal=article.journal,
                    url=license_url,
            )
        except submission_models.Licence.DoesNotExist:
            try:
                split = urlsplit(license_url)
                split = split._replace(
                    scheme="https" if split.scheme == "http" else "http")
                article.license = submission_models.Licence.objects.get(
                        journal=article.journal,
                        url=split.geturl(),
                )
            except submission_models.Licence.DoesNotExist:
                logging.warning("Unknown license %s" % license_url)


def metadata_authors(soup, article):
    bepress_authors = [a for a in soup.authors if a.string != "\n"]
    for i, bepress_author in enumerate(bepress_authors):
        try:
            email = bepress_author.email.string
        except AttributeError:
            email = make_dummy_email(bepress_author)
        account, _ = Account.objects.get_or_create(email=email)
        if bepress_author.fname:
            account.first_name = bepress_author.fname.string
        else:
            account.first_name = " "
        if bepress_author.fname:
            account.last_name = bepress_author.lname.string
        else:
            account.last_name = " "
        if bepress_author.institution:
            account.institution = bepress_author.institution.string
        if bepress_author.mname:
            account.middle_name = bepress_author.mname.string

        account.save()

        account.snapshot_self(article)

        models.ImportedArticleAuthor.objects.get_or_create(
                article=article,
                author=account,
        )

        if i == 0:
            article.correspondence_author = account


def make_dummy_email(author):
    hashed = hashlib.md5(str(author).encode("utf-8")).hexdigest()
    return "{0}@{1}".format(hashed, settings.DUMMY_EMAIL_DOMAIN)


def create_article_record(soup, journal, default_section):
    imported_article, created = models.ImportedArticle.objects.get_or_create(
        bepress_id=soup.articleid.string,
    )
    if created or not imported_article.article:
        article = submission_models.Article(is_import=True)
        logger.info(
            "Importing new article with bepress id %s"
            "" % imported_article.bepress_id
        )
    else:
        article = imported_article.article
        logger.debug(
            "Updating article %s (bepress id %s)"
            "" % (article.pk, imported_article.bepress_id)
        )

    article.title = soup.title.string
    article.journal = journal
    article.abstract = str(soup.abstract.string) if soup.abstract else ''
    article.date_published = getattr(soup, 'publication-date').string
    article.date_submitted = getattr(soup, 'submission-date').string
    article.stage = submission_models.STAGE_PUBLISHED
    metadata_section(soup, article, default_section)

    article.save()

    metadata_keywords(soup, article)
    metadata_authors(soup, article)
    metadata_license(soup, article)
    article.save()

    imported_article.article = article
    imported_article.save()

    return article


def add_pdf_as_galley(pdf_path, article):
    if article.pdfs:
        return

    with open(pdf_path, "rb") as f:
        django_file = DjangoFile(f)
        saved_file = files.save_file_to_article(django_file, article,
                owner=None,
                label="PDF",
                is_galley=True,
        )
        galley = Galley.objects.create(
                article=article,
                file=saved_file,
                type="pdf",
                label="pdf",
        )
        article.galley_set.add(galley)


def import_articles(folder, pdf_type, journal, default_section):
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
            article = create_article_record(soup, journal, default_section)
            if pdf_path is not None:
                add_pdf_as_galley(pdf_path, article)
