from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_POST

from journal.models import Journal
from submission.models import Section

from plugins.bepress import const
from plugins.bepress import utils


def index(request):

    folders = utils.get_bepress_import_folders()
    sections = Section.objects.filter(journal=request.journal)

    template = 'bepress/index.html'
    context = {
        'folders': folders,
        'sections': sections
    }

    return render(request, template, context)


@require_POST
def import_bepress_articles(request):
    folder = request.POST.get('folder', None)
    struct = request.POST.get('bepress_structure')
    pdf_type = request.POST.get('pdf_type', None)
    section_id = request.POST.get('section_id', None)
    section_key = request.POST.get('section_key')
    if request.journal:
        journal = request.journal
    else:
        journal_code = request.POST['journal_code']
        journal = Journal.objects.get(code=journal_code)

    if section_id:
        default_section = get_object_or_404(Section,
                pk=section_id, journal=request.journal)
    else:
        default_section = None

    if folder:
        stamped = pdf_type == "stamped"
        utils.import_articles(
            folder, stamped, journal,
            struct, default_section, section_key,
        )


    return redirect(
        reverse(
            'bepress_index'
        )
    )
