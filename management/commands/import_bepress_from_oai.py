
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
        if options["structure_type"] == "books":
            site = Press.objects.first()
            utils.import_archive(
                options["archive_name"], options["stamped"],
                site, options["structure_type"],
            )
        else:
            site = journal_models.Journal.objects.get(code=options["site_code"])
            section = None
            if options.get("default_section"):
                section = sub_models.Section.objects.get(
                    id=options["default_section"],
                    journal=site,
                )
            utils.import_archive(
                options["archive_name"], options["stamped"], site,
                options["structure_type"], section, options["section_field"],
            )


    def handle(self, *args, **options):
        client = Sickle(options["oai-url"])
        import_from_oai(client, set_=options.get("set"))
        print("Done.")
        print(
            "You can now import the loaded archives with "
            "python src/manage.py import_bepress_archive.py"
        )

