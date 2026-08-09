import csv
from django.core.management.base import BaseCommand

from journal import models as journal_models
from press.models import Press
from submission import models as sub_models

from plugins.bepress import utils
from plugins.bepress.management.commands.import_bepress_archive import GALLEY_CHOICES


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
            "galley",
            choices=GALLEY_CHOICES,
            help="What type of local galley to load.",
        )
        parser.add_argument(
            "--base-supp-csv",
            help="Earlier supp file report CSV to use as a base.",
        )

    def handle(self, *args, **options):
        utils.report_all_local_files(
            options["folder"],
            options["galley"],
            options["base_supp_csv"],
        )
