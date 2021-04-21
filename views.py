import csv
from io import TextIOWrapper

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from core import forms as core_forms
from journal.models import Journal
from submission.models import Section

from plugins.bepress import const
from plugins.bepress import utils
from plugins.bepress import csv_handler

CSV_MIMETYPES = ["application/csv", "text/csv"]


def index(request):

    folders = utils.get_bepress_import_folders()
    sections = Section.objects.filter(journal=request.journal)

    template = 'bepress/index.html'
    context = {
        'folders': folders,
        'sections': sections
    }

    return render(request, template, context)


def import_bepress_csv(request):
    form = core_forms.FileUploadForm(mimetypes=CSV_MIMETYPES)
    if request.FILES and 'file' in request.FILES:
        form = core_forms.FileUploadForm(
            request.POST, request.FILES,
            mimetypes=CSV_MIMETYPES,
        )
        if form.is_valid():
            file_ = TextIOWrapper(request.FILES['file'].file, encoding="utf-8")
            reader = csv.DictReader(file_)
            csv_handler.csv_to_xml(reader)

            messages.add_message(
                request, messages.SUCCESS,
                "CSV File Uploaded",
            )
        else:
            messages.add_message(
                request, messages.ERROR,
                "Invalid file",
            )

    template = 'bepress/csv_import.html'
    context = {"form": form}
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
