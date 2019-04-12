from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_POST

from submission.models import Section

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
    pdf_type = request.POST.get('pdf_type', None)
    section_id = request.POST.get('section_id', None)
    section_key = request.POST.get('section_key')
    if section_id:
        default_section = get_object_or_404(Section,
                pk=section_id, journal=request.journal)
    else:
        default_section = None

    if folder:
        utils.import_articles(
            folder, pdf_type, request.journal,
            default_section, section_key
        )


# TODO: uncomment when development is finished, this allows you to run the
# command over without having to make selections repeatedly
"""
    return redirect(
        reverse(
            'bepress_index'
        )
    )"""
