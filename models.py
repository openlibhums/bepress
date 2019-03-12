from django.db import models


class ImportedArticle(models.Model):
    article = models.ForeignKey('submission.Article')
    bepress_id = models.BigIntegerField()
