import csv
from django.core.management.base import BaseCommand

from plugins.bepress.csv_handler import csv_to_xml


class Command(BaseCommand):
    """Converts a Bepress export in CSV format into XML"""

    help = "Converts a Bepress export in CSV format into XML"

    def add_arguments(self, parser):
        parser.add_argument('csv_path')
        parser.add_argument('--dry-run', action="store_true", default=False)

    def handle(self, *args, **options):
        with open(options["csv_path"], "r", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            iterator = csv_to_xml( reader, commit=options["dry_run"])
            for xml, path in iterator:
                if path:
                    print("Written XML to %s" % path)
                else:
                    print("Parsed XML: %s" % xml)
