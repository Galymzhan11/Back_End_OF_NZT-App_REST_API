from django.db import models


class Subject(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)
    name = models.CharField(db_column='Name', max_length=255)  
    language = models.IntegerField(db_column='Language')  
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2)  
    sell_price = models.DecimalField(db_column='SellPrice', max_digits=10, decimal_places=2, null=True, blank=True)  
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)  
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)  
    image_id = models.ForeignKey('profiles.File', db_column='ImageId', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'Courses'
        
    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return self.sell_price if self.sell_price else self.price