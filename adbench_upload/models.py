from django.db import models

# Create your models here.


class AdbenchUpload(models.Model):
    user_email = models.CharField(max_length=200)
    file = models.FileField(upload_to='files/')
    algo = models.CharField(max_length=100)


class adgym_info(models.Model):
    user_email = models.CharField(max_length=200)
    file = models.FileField(upload_to='files/')
    best_pipeline = models.CharField(max_length=1000)
    fit_time = models.CharField(max_length=20)
    # anomaly_score = models.CharField(max_length=1000)
    anomaly_score = models.BinaryField()

