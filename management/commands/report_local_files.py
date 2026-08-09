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
            "folder",
            help="The name of the archive folder under files/plugins/bepress "
            "not including the journal folder"
        )
        parser.add_argument(
            "--base-csv",
            help="Earlier report CSV to use as a base.",
        )

    def handle(self, *args, **options):
        utils.report_all_local_files(options["folder"], options["base_csv"])
