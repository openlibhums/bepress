"""
A module for retrieving Bepress XML documents by traversing an OAI feed
"""
from lxml import etree as et
import pathlib

from django.template.loader import render_to_string
from utils.logger import get_logger

from plugins.bepress.plugin_settings import BEPRESS_PATH

logger = get_logger(__name__)


# An undocumented prefix that fromats the XML records in bepress custom format
METADATA_PREFIX = "document-export"


def import_from_oai(client, set_=None, identifier=None):
    """ Imports bepress metadata from a given OAI client
    Metadata is written as XML to the location defined in settings as
    BEPRESS_PATH
    :param client: an instance of sicle.app.Sickle
    """
    if identifier:
        record = client.ListRecords(
            metadataPrefix=METADATA_PREFIX,
            identifier="identifier",
        )
        generate_metadata_from_oai_record(record.raw)
    else:
        list_records_kwargs = {}
        if set_:
            list_records_kwargs["set"] = set_

        record_iterator = client.ListRecords(
            metadataPrefix=METADATA_PREFIX,
            **list_records_kwargs,
        )
        for record in record_iterator:
            logger.info("Processing %s", record.header)
            generate_metadata_from_oai_record(record.raw)


def generate_metadata_from_oai_record(record):
    tree = et.fromstring(record)
    documents = tree.xpath("//documents")
    if documents:
        document = documents[0]
        path = document.xpath("//submission-path/text()")
        if path:
            parsed = et.tostring(document)
            xml = render_xml(parsed)
            file_path = pathlib.Path(BEPRESS_PATH, path[0], 'metadata.xml')
            logger.info("Writing to %s", file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(str(file_path), "w") as xml_file:
                xml_file.write(xml)
        else:
            logger.warning("No submission-path found")


def render_xml(parsed):
    """Render Bepress XML metadata from the given context
    :param parsed: Dict representation of an article's metadata
    :return: A rendered django Template of the metadata in XML format
    """
    template = 'bepress/xml/oai_metadata.xml'
    context = {"documents": parsed}
    return render_to_string(template, context)
