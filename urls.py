__copyright__ = "Copyright 2017 Birkbeck, University of London"
__author__ = "Martin Paul Eve & Andy Byers"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck Centre for Technology and Publishing"

from django.urls import re_path

from plugins.bepress import views

urlpatterns = [
    re_path(r'^$', views.index, name='bepress_index'),
    re_path(r'^index/$', views.index, name='bepress_index'),
    re_path(r'^import/$', views.import_bepress_articles, name='bepress_import'),
    re_path(r'^csv_import/$', views.import_bepress_csv, name='bepress_csv_import'),
]
