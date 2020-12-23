""" Module to define model structure """

from django.db import models


# Create your models here.

class Prescription(models.Model):
    """ Class defining Prescription database table schema """
    clinic_id = models.IntegerField(null=True, blank=True)
    physician_id = models.IntegerField()
    patient_id = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        """ Defining display text """
        return f'[{self.clinic_id}] {self.patient_id}: {self.description}'

    @property
    def clinic(self):
        """ Defining property to define display attribute """
        return {
            'id': self.clinic_id
        }

    @property
    def physician(self):
        """ Defining property to define display attribute """
        return {
            'id': self.physician_id,
        }

    @property
    def patient(self):
        """ Defining property to define display attribute """
        return {
            'id': self.patient_id,
        }

    @property
    def text(self):
        """ Defining property to define display attribute """
        return self.description
