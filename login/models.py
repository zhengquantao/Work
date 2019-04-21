from django.db import models


class UserInfo(models.Model):
    name = models.CharField(max_length=16, unique=True, db_index=True)
    pwd = models.CharField(max_length=16)


class Execel(models.Model):
    area = models.CharField(max_length=64, default='')
    type = models.CharField(max_length=32, default='')
    phone = models.CharField(unique=True, max_length=16, default='')
    datetime = models.DateTimeField(auto_now_add=True)
