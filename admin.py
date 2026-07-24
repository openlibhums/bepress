from django.contrib import admin

from plugins.bepress import models


class ImportedArticleAdmin(admin.ModelAdmin):
    list_display = (
        'bepress_id',
        'dump_name',
        'article',
        'journal',
        'started',
    )
    list_filter = (
        'journal',
        'dump_name',
    )
    raw_id_fields = (
        'article',
    )
    search_fields = (
        'bepress_id',
        'article__pk',
        'article__title',
    )


for pair in [
    (models.ImportedArticle, ImportedArticleAdmin),
]:
    admin.site.register(*pair)
