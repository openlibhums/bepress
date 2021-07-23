import csv
from django.core.management.base import BaseCommand

from journal import models as journal_models
from submission import models as sub_models

from plugins.bepress import utils

STRUCTURE_CHOICES = {"journal", "series", "events"}


class Command(BaseCommand):
    """Imports a bepress archive into Janeway"""

    help = "Imports a bepress archive into Janeway"

    def add_arguments(self, parser):
        parser.add_argument('journal_code')
        parser.add_argument(
            'archive_name',
            help='The name of the archive under files/plugins/bepress'
        )
        parser.add_argument('structure_type',
            choices=STRUCTURE_CHOICES,
            help="The Digital Commons structure type used in the archive",
        )
        parser.add_argument('--stamped', action="store_true", default=False)
        parser.add_argument(
            '--default-section',
            help="The ID of the section to use when one can't be found",
        )
        parser.add_argument(
            '--section-field',
            help="Custom field used for denoting the section name",
        )
        parser.add_argument('--dry-run', action="store_true", default=False)

    def handle(self, *args, **options):
        journal = journal_models.Journal.objects.get(code=options["journal_code"])
        section = None
        if options.get("default_section"):
            section = sub_models.Section.objects.get(
                id=options["default_section"],
                journal=journal,
            )
        utils.import_articles(
            options["archive_name"], options["stamped"], journal,
            options["structure_type"], section, options["section_field"],
        )