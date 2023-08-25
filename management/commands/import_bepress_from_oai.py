
from django.core.management.base import BaseCommand
from sickle import Sickle

from plugins.bepress.oai import import_from_oai


class Command(BaseCommand):
    """Imports a bepress XML archive from their OAI feed"""

    help = "Imports a bepress archive from their OAI feed"

    def add_arguments(self, parser):
        parser.add_argument('oai-url')
        parser.add_argument(
            '--set', '-s',
            default=None,
            help="The set identifier by which to filter the OAI feed",
        )
        parser.add_argument(
            '--identifier', '-i',
            default=None,
            help="URI identifier for retrieving a single document from the OAI",
        )

    def handle(self, *args, **options):
        client = Sickle(options["oai-url"])
        import_from_oai(client, set_=options.get("set"))
        print("Done.")
        print(
            "You can now import the loaded archives with "
            "python src/manage.py import_bepress_archive.py"
        )

