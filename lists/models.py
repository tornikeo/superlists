from django.db import models
import inspect

# Create your models here.
class Item(models.Model):
    text = models.TextField(default='')