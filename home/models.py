from django.contrib.auth.models import User
from django.db import models


class Feeder(models.Model):
    feeder = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    item_number = models.IntegerField()
    score = models.IntegerField(default=0)
    positive_score = models.IntegerField(default=0)
    negative_score = models.IntegerField(default=0)
    visible_status = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-score']


class Item(models.Model):
    feed = models.ForeignKey(Feeder, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    score = models.IntegerField(default=0)
    positive_score = models.IntegerField(default=0)
    negative_score = models.IntegerField(default=0)
    embedded = models.CharField(max_length=255, blank=True)  # for only youtube

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-score']


class Comment(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    commented_item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-createdAt']
