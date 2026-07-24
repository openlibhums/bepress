import csv
from django.core.management.base import BaseCommand

from journal import models as journal_models
from press.models import Press
from submission import models as sub_models

from plugins.bepress import utils


class Command(BaseCommand):
    """Checks local files for supplementary files in metadata.xml and exports a
    list

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "folder", help="The name of the folder under files/plugins/bepress"
        )

    def handle(self, *args, **options):
        utils.report_local_files(options["folder"])
