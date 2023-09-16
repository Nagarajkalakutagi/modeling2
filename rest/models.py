from django.db import models

# Create your models here.


class Users(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    age = models.IntegerField(default=True)