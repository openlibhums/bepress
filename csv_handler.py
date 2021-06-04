"""
Collection of functions for handling of a bepress CSV

Missing Metadata:
 - DOI
 - Submission Date
 - Metadata


"""
import pathlib
import urllib.parse as urlparse
from urllib.parse import parse_qs

from bs4 import BeautifulSoup
import requests
from django.template.loader import render_to_string
from utils.logger import get_logger

from plugins.bepress.plugin_settings import BEPRESS_PATH

logger = get_logger(__name__)


AUTHOR_FIELDS_MAP = {
    ('author%d_fname', 'first_name'),
    ('author%d_mname', 'middle_name'),
    ('author%d_lname', 'last_name'),
    ('author%d_suffix', 'suffix'),
    ('author%d_email', 'email'),
    ('author%d_institution', 'institution'),
    ('author%d_is_corporate', 'is_corporate'),
}


SCRAPE_FIELDS = {
    "fulltext_url",
    "article_id",
}


def csv_to_xml(reader, commit=True, scrape_missing=True):
    """Converts a Bepress CSV Batch into Bepress XML format

    :param reader: A csv.DictReader
    :param commit: If true, the metadata is persisted to disk.
    :return: A generator that yields XML documents and the path they'
    """
    file_path = None
    for row in reader:
        parsed = parse_row(row)
        if scrape_missing:
            scrape_missing_metadata(parsed)
        xml = render_xml(parsed)
        id = parsed["article_id"]
        if commit:
            file_path = pathlib.Path(BEPRESS_PATH, row["issue"], id, "metadata.xml")
            logger.info("Writing to %s", file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(str(file_path), "w") as xml_file:
                xml_file.write(xml)

        yield xml, file_path


def render_xml(parsed):
    """Render Bepress XML metadata from the given context
    :param parsed: Dict representation of an article's metadata
    :return: A rendered django Template of the metadata in XML format
    """
    template = 'bepress/xml/metadata.xml'
    context = {"article": parsed}
    return render_to_string(template, context)


def parse_row(row):
    """Parse the given Bepress CSV Row data into a dictionary
    :param row: Dict of a CSV Row:
    :return: Dict of the parsed data
    """
    article_dict = parse_article_metadata(row)
    article_dict["authors"] = parse_authors(row)
    return article_dict


def parse_article_metadata(row):
    """Parse the given Bepress CSV Row data into a dictionary
    :param row: Dict of a CSV Row:
    :return: Dict of the parsed article metadata
    """
    return dict(
        row,
        keywords=(w.strip() for w in row['disciplines'].split(";")),
        fulltext_url=get_fulltext_url(row),
        language=row.get('language', 'en'),
        peer_reviewed=row.get('peer_reviewed', False),
    )


def parse_authors(row):
    """ Parse author data from the given row into a nested mapping
    The bepress CSV exposes all authors in a single row, by adding an
    index to each column (e.g author1_fname, author2_fname). The indexes
    range from 1 to 5 and are present even with blank
    :param row: Dict of a CSV Row:
    :return: Dict of the parsed author metadata
    """
    authors = []
    for author_index in range(1,6):
        author = {}
        for src, dest in AUTHOR_FIELDS_MAP:
            if row.get(src % author_index):
                author[dest] = row[src % author_index]
        if author:
            # If not all fields were blank
            authors.append(author)
        else:
            # If author is blank, no point checking the next indexes
            break
    return authors


def scrape_missing_metadata(data, unstamped=True):
    """ Scrape missing entries in the provided metadata from remote URL
    :param data: A dict with the article data 
    :param unstamped: (bool) Return URL to the unstamped version of the PDF
    """
    if all(data.get(key)for key in SCRAPE_FIELDS):
        return

    soup = None

    if data.get("calc_url"):
        try:
            logger.info("Fetching article from %s", data["calc_url"])
            response = requests.get(data["calc_url"])
        except requests.exceptions.RequestException as exc:
            logger.warning("Failed to extract PDF URL: %s", exc)
        else:
            if response.ok:
                soup = BeautifulSoup(response.text, "html.parser")
            else:
                logger.warning("No fulltext url found")
    if soup:
        if not data.get("fulltext_url"):
            data["fulltext_url"] = get_fulltext_url(data, soup=soup)
    if not data.get("article_id"):
        data["article_id"] = get_article_id(data)


def get_fulltext_url(row, soup=None, unstamped=True):
    """ Parse the given Bepress CSV Row and retrieve the fulltext PDF url
    If no fulltext url is found, we try to scrape it from the article page
    :param row: Dict of a CSV Row:
    :param soup: A BeautifulSoup instance of the remote article
    :param unstamped: (bool) Return URL to the unstamped version of the PDF
    :return: URL of the fulltext file
    """
    url = row.get("fulltext_url")
    
    if not url and soup:
        # Try from the meta tags
        meta_tag = soup.find("meta", {"name":"bepress_citation_pdf_url"})
        if meta_tag:
            url = meta_tag.attrs["content"]
            logger.debug("Extracted fulltext url %s", url)
    
    if not url and soup:
        # Try from the download link
        anchor_tag = soup.find("a", id="pdf")
        if anchor_tag:
            url = anchor_tag.attrs["href"]
            logger.debug("Extracted fulltext url %s", url)

    if url and unstamped:
        if "unstamped=0" in url:
            url = url.replace("unstamped=0", "unstamped=1")
        elif "?" in url:
            url += "&unstamped=1"
        else:
            url += "?unstamped=1"

    return url


def get_article_id(data):
    url = data.get("fulltext_url")
    article_id = None
    if url:
        parsed_url = urlparse.urlparse(url)
        article_id = parse_qs(parsed_url.query).get("article", "")[0]

    return article_id or data["context_key"]
        

