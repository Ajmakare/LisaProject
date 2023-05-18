from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, time

class Program(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

class Video(models.Model):
    id = models.AutoField(primary_key=True)
    video_link = models.URLField()
    name = models.CharField(max_length=100)
    description = models.TextField()

class PVJunction(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

class UPJunction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.start_date = timezone.make_aware(datetime.combine(self.start_date, time.min), timezone.get_current_timezone())
        self.end_date = timezone.make_aware(datetime.combine(self.end_date, time.max), timezone.get_current_timezone())
        super().save(*args, **kwargs)

class TrialCode(models.Model):
    code = models.CharField(max_length=100, unique=False)

class HomePageText(models.Model):
    id = models.AutoField(primary_key=True)
    home_text = models.TextField()

class TierText(models.Model):
    tier = models.IntegerField()
    tier_text = models.TextField()
    tier_price = models.IntegerField(default=0)

