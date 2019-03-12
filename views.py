from django.shortcuts import render, redirect, reverse
from django.views.decorators.http import require_POST

from plugins.bepress import utils


def index(request):

    folders = utils.get_bepress_import_folders()

    template = 'bepress/index.html'
    context = {
        'folders': folders,
    }

    return render(request, template, context)


@require_POST
def import_bepress_articles(request):
    folder = request.POST.get('folder', None)
    pdf_type = request.POST.get('pdf_type', None)

    if folder:
        utils.import_articles(folder, pdf_type, request.journal)

    # TODO: uncomment when development is finished, this allows you to run the
    # command over without having to make selections repeatedly
    """
    return redirect(
        reverse(
            'bepress_index'
        )
    )"""
