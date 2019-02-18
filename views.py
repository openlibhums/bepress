from django.shortcuts import render


def index(request):

    template = 'bepress/index.html'
    context = {}

    return render(request, template, context)
