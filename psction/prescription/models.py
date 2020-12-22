""" Module to define model structure """

from django.db import models


# Create your models here.

class Prescription(models.Model):
    """ Class defining Prescription database table schema """
    client_id = models.IntegerField(null=True, blank=True)
    physician_id = models.IntegerField()
    patient_id = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        """ Defining display text """
        return f'[{self.client_id}] {self.patient_id}: {self.description}'
