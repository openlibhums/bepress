import os
import logging

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


def import_articles(folder, pdf_type):
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

            print(metadata_path, pdf_path)
