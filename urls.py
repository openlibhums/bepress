__copyright__ = "Copyright 2017 Birkbeck, University of London"
__author__ = "Martin Paul Eve & Andy Byers"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck Centre for Technology and Publishing"

from django.conf.urls import url

from plugins.bepress import views

urlpatterns = [
    url(r'^bepress/$', views.index, name='bepress_index'),
]
