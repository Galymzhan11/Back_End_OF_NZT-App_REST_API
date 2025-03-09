from django.db import models

class Setting(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)
    language = models.CharField(db_column='Language')
    notify = models.BooleanField(db_column='Notify')
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        managed = False
        db_table = 'Settings'

    def __str__(self):
        return f'Language: {self.get_language_display()}, Notify: {self.notify}'

    def get_language_display(self):
        languages = {1: "Русский", 2: "Английский"}
        return languages.get(self.language, "Unknown")