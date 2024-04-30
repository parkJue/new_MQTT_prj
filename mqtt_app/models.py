from django.db import models

class PCSModel(models.Model):
    active_power = models.FloatField()
    frequency = models.FloatField()
    R_vol = models.FloatField()
    S_vol = models.FloatField()
    T_vol = models.FloatField()
    R_cur = models.FloatField()
    S_cur = models.FloatField()
    T_cur = models.FloatField()

class BATModel(models.Model):
    SOC = models.FloatField()
    SOH = models.FloatField()
    vol = models.FloatField()
    cur = models.FloatField()
