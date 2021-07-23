import cgi
import dateutil
import hashlib
import logging
import os
from urllib.parse import urlsplit
from uuid import uuid4

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files import File as DjangoFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import OperationalError
import requests

from core import files
from core.models import Account, Galley
from identifiers.models import Identifier
from submission import models as submission_models
from journal import models as journal_models

from plugins.bepress import const
from plugins.bepress import models
from plugins.bepress.plugin_settings import BEPRESS_PATH

logger = logging.getLogger(__name__)

SECTION_FIELDS = ["track"]


def get_bepress_import_folders():
    if os.path.exists(BEPRESS_PATH):
        return os.listdir(BEPRESS_PATH)
    else:
        return []


def soup_metadata(metadata_path):
    logger.info('Souping article %s' % metadata_path)
    metadata_content = open(metadata_path).read()
    return BeautifulSoup(metadata_content, "lxml")


def create_article_record(dump_name, soup, journal, default_section, section_key):
    imported_article, created = models.ImportedArticle.objects.get_or_create(
        dump_name=dump_name,
        bepress_id=soup.articleid.string,
        journal=journal,
    )
    if created or not imported_article.article:
        article = submission_models.Article(is_import=True)
        logger.info(
            "Importing new article with bepress id %s"
            "" % imported_article.bepress_id
        )
    else:
        article = imported_article.article
        logger.info(
            "Updating article %s (bepress id %s)"
            "" % (article.pk, imported_article.bepress_id)
        )

    article.title = soup.title.string
    article.journal = journal
    article.abstract = str(soup.abstract.string) if soup.abstract else ''
    article.date_published = getattr(soup, 'publication-date').string
    if getattr(soup, 'submission-date'):
        article.date_submitted = getattr(soup, 'submission-date').string
    else:
        article.date_submitted = article.date_published
    article.stage = submission_models.STAGE_PUBLISHED
    metadata_section(soup, article, default_section, section_key)

    article.save()

    metadata_doi(soup, article)
    metadata_keywords(soup, article)
    metadata_authors(soup, article)
    metadata_license(soup, article)
    metadata_citation(soup, article)
    article.save()

    imported_article.article = article
    imported_article.save()

    return article


def metadata_doi(soup, article):
    field = soup.fields.find(attrs={"name": "doi"})
    if field and field.value:
        Identifier.objects.get_or_create(
            id_type="doi",
            article=article,
            identifier=field.value.string
        )


def metadata_keywords(soup, article):
    keywords = [keyword.string for keyword in soup.find_all('keyword')]

    for keyword in keywords:
        try:
            word, _ = submission_models.Keyword.objects.get_or_create(
                word=keyword)
            article.keywords.add(word)
        except OperationalError as e:
            logger.warning("Couldn't add keyword %s: %s" % (keyword, e))


def metadata_section(soup, article, default_section, section_key=None):
    if section_key:
        field = soup.fields.find(attrs={"name": section_key})
        soup_section = field.value.string if field else None
    else:
        field = getattr(soup, 'document-type').string
        soup_section = field.string if field else None

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
        logger.warning(
            '{article} no section found'.format(article=article.title))


def metadata_license(soup, article):
    field = soup.fields.find(attrs={"name": "distribution_license"})
    if field:
        license_url = field.value.string
        if license_url.endswith("/"):
            license_url = license_url[:-1]
        license_url.replace("http:", "https:")
        article.license, c = submission_models.Licence.objects.get_or_create(
            journal=article.journal,
            url=license_url,
            defaults={
                "name": "Imported license",
                "short_name": "imported",
            }
        )
        if c:
            logger.info("Created new license %s", license_url)

    else:
        try:
            # Default to Copyright
            article.license = submission_models.Licence.objects.get(
                journal=article.journal,
                short_name="Copyright",
            )
            logger.info("No license in metadata, defaulting to copyright")
        except submission_models.Licence.DoesNotExist:
            logger.warning("No license in metadata, leaving blank")


def metadata_citation(soup, article):
    field = soup.fields.find(attrs={"name": "dc_citation"})
    if field and field.value:
        article.custom_how_to_cite = field.value.string
        article.save()


def metadata_authors(soup, article, dummy_accounts=False):
    bepress_authors = [a for a in soup.authors if a.string != "\n"]
    for i, bepress_author in enumerate(bepress_authors):
        if bepress_author.organization:
            handle_corporate_author(bepress_author, article)
            continue
        author_dict = {}

        if bepress_author.fname:
            author_dict["first_name"] = bepress_author.fname.string
        else:
            author_dict["first_name"] = " "
        if bepress_author.lname:
            author_dict["last_name"] = bepress_author.lname.string
        else:
            author_dict["last_name"] = " "
        if bepress_author.mname:
            author_dict["middle_name"] = bepress_author.mname.string
        if bepress_author.institution:
            author_dict["institution"] = bepress_author.institution.string

        try:
            email = bepress_author.email.string
        except AttributeError:
            email = None
        account = None

        if not email and dummy_accounts:
            email = make_dummy_email(bepress_author)

        if email:
            account, _ = Account.objects.get_or_create(
                email=email,
                defaults=author_dict,
            )
        if account:
            author_order, created = submission_models.ArticleAuthorOrder \
                .objects.get_or_create(
                    article=article, author=account,
                    defaults={"order": i}
            )
            models.ImportedArticleAuthor.objects.get_or_create(
                    article=article,
                    author=account,
            )

        # This field is frozen only
        if bepress_author.suffix:
            author_dict["name_suffix"] = bepress_author.suffix.string
        handle_frozen_author(author_dict, article, i, account=account)

        if i == 0 and account:
            article.correspondence_author = account


def handle_corporate_author(bepress_author, article):
    frozen_record,c = submission_models.FrozenAuthor.objects.get_or_create(
        article=article,
        institution=bepress_author.organization.string,
        is_corporate=True,
    )


def handle_frozen_author(bepress_author, article, order, account=None):
    frozen_record, c = submission_models.FrozenAuthor.objects.update_or_create(
        article=article,
        order=order,
        author=account,
        defaults=bepress_author,
    )


def make_dummy_email(author):
    hashed = hashlib.md5(str(author).encode("utf-8")).hexdigest()
    return "{0}@{1}".format(hashed, settings.DUMMY_EMAIL_DOMAIN)


def fetch_remote_galley(soup, stamped=False):
    url = getattr(soup, "fulltext-url").string
    if url:
        if stamped:
            has = "unstamped=1"
            wants = "unstamped=0"
        else:
            has = "unstamped=0"
            wants = "unstamped=1"
        if '?' in url and "unstamped=" in url:
            url = url.replace(has, wants)
        elif '?' in url:
            url += "&%s" % wants
        else:
            url += "?%s" % wants

        response = requests.get(url, stream=True)
        if response.status_code != 200:
            logger.error("Error fetching galley: %s", response.status_code)
        else:
            filename = get_filename_from_headers(response)
            django_file = SimpleUploadedFile(
                filename,
                response.content,
                "application/pdf",
            )
            return django_file

    return None

def add_pdf_galley(pdf_file, article):
    if article.pdfs:
        return

    saved_file = files.save_file_to_article(
            pdf_file, article,
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


def import_articles(folder, stamped, journal, struct, default_section, section_key):
    path = os.path.join(BEPRESS_PATH, folder)
    for root, dirs, files_ in os.walk(path):

        if 'metadata.xml' in files_:
            metadata_path = os.path.join(root, 'metadata.xml')

            soup = soup_metadata(metadata_path)
            try:
                pdf_file = fetch_remote_galley(soup, stamped)
            except AttributeError:
                pdf_file = fetch_local_galley(root, files_, stamped)

            article = create_article_record(
                folder, soup, journal, default_section, section_key)

            #Query the article to ensure correct attribute types
            article = submission_models.Article.objects.get(pk=article.pk)
            add_to_issue(article, root, path, struct, soup)
            if pdf_file:
                add_pdf_galley(pdf_file, article)


def fetch_local_galley(root_path, sub_files, stamped):
    filename = get_filename_from_local(sub_files, stamped)

    if filename:
        pdf_path = os.path.join(root_path, filename)

        f = open(pdf_path, "rb")
        return DjangoFile(f)
    else:
        return None

def add_to_issue(article, root_path, export_path, struct, soup):
    """ Adds the new article to the right issue. Issue created if not present

    Bepress exports have roughly this structure:
    - Journal export (JOURNAL_STRUCTURE):
        path/to/export/vol{volume_id}/iss{issue_id}/{article_id}/*
    - Conference export (EVENTS_STRUCTURE):
        path/to/export/{year}/*/*
    :param article: The submission.Article being imported
    :param root_path: The absolute path in which the metadata.xml was found
    :param export_path: The absolute path to the provided exported data
    :param struct: (str) One of const.BEPRESS_STRUCTURES
    :param soup: (bs4.Soup) Soupified metadata.xml
    """
    relative_path = root_path.replace(export_path, "")
    issue_title = year = issue_num = vol_num = None
    issue_type = journal_models.IssueType.objects.get(
        code="issue", journal=article.journal)
    try:
        if struct == const.EVENTS_STRUCTURE:
            issue_type = journal_models.IssueType.objects.get(
                code="collection", journal=article.journal)
            _, year, *remaining = relative_path.split("/")
            pub_title = getattr(soup, 'publication-title')
            if pub_title:
                issue_title = "%s %s" % (pub_title.string, year)
        elif struct == const.JOURNAL_STRUCTURE:
            _, volume_code, issue_code, article_id = relative_path.split("/")
            vol_num = int(volume_code.replace("vol", ""))  # volN
            issue_num = int(issue_code.replace("iss", ""))  # issN
        elif struct == const.SERIES_STRUCTURE:
            year = vol_num = str(article.date_published.year - 1)
        else:
            raise RuntimeError("Unkown bepress structure %s" % struct)
    except Exception as e:
        logger.exception(e)
        logger.error(
            "Failed to get issue details for {}, path: {}".format(
                "conference" if article.journal.is_conference else "journal",
                export_path,
            )
        )
    else:
        issue, created = journal_models.Issue.objects.get_or_create(
            journal=article.journal,
            volume=vol_num or 1,
            issue=issue_num or year,
            issue_title=issue_title
        )
        if created:
            issue.issue_type = issue_type
            logger.info("Created new issue {}".format(issue))

        if year:
            issue.date = dateutil.parser.parse(year)
        issue.save()
        issue.articles.add(article)
        article.primary_issue = issue
        article.save()
        logger.info("Added to issue {}".format(issue))

        return issue


def get_filename_from_local(sub_files, stamped=False):
    galley_filename = None

    if len(sub_files) > 1:
        if stamped:
            if 'stamped.pdf' in sub_files:
                galley_filename = 'stamped.pdf'
            else:
                stamped = False
                galley_filename = get_filename_from_local(sub_files, pdf_type)
        else:
            candidates = [
                f for f in sub_files
                if f not in {"stamped.pdf", "metadata.xml", "auto_convert.pdf"}
                or not f.endswith("pdf")
            ]
            if candidates:
                galley_filename = candidates[0]

    return galley_filename


def get_filename_from_headers(response):
    try:
        header = response.headers["Content-Disposition"]
        _, params = cgi.parse_header(header)
        return params["filename"]
    except Exception as e:
        logger.warning(
            "No filename available in headers, will autogenerate one: %s"
            "" % e
        )
        return '{uuid}.pdf'.format(uuid=uuid4())
