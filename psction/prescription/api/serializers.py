""" Module to define api serializer to define api data sctructure and validations """
import sys

from django.conf import settings

from rest_framework import serializers

from prescription.models import Prescription

from prescription.exceptions import ExternalApiError
from prescription.exceptions import ExternalResourceNotFound
from prescription.utils import ExternalServiceConnector


class PrescriptionSerializer(serializers.Serializer):
    """ Class defining Prescription api structure """
    id = serializers.IntegerField(read_only=True)
    clinic = serializers.DictField(
        allow_empty=False,
        child=serializers.IntegerField(),
    )
    physician = serializers.DictField(
        allow_empty=False,
        child=serializers.IntegerField(),
    )
    patient = serializers.DictField(
        allow_empty=False,
        child=serializers.IntegerField(),
    )
    text = serializers.CharField(
        allow_null=False,
        allow_blank=False,
        max_length=500,
    )

    def external_request(self, service, endpoint, method='GET', data=None):
        manager = ExternalServiceConnector(
            service=service,
            method=method,
            endpoint=endpoint,
            data=data,
        )
        try:
            return manager.do_request()
        except ExternalResourceNotFound:
            raise serializers.ValidationError(f'{service} not found.')
        except ExternalApiError:
            raise serializers.ValidationError(f'{service} is not available.')

    def validate_clinic(self, value):
        if 'id' not in value:
            return None
        try:
            return self.external_request(
                service=settings.EXTERNAL_CLINIC,
                endpoint=f'/clinics/{value["id"]}/',
            )
        except serializers.ValidationError:
            return None

    def validate_physician(self, value):
        if 'id' not in value:
            raise serializers.ValidationError('')

        return self.external_request(
            service=settings.EXTERNAL_PHYSICIAN,
            endpoint=f'/physicians/{value["id"]}/',
        )

    def validate_patient(self, value):
        if 'id' not in value:
            raise serializers.ValidationError('')
        return self.external_request(
            service=settings.EXTERNAL_PATIENT,
            endpoint=f'/patients/{value["id"]}/',
        )

    def create(self, validated_data):
        try:
            metrics_data = {
                'clinic_id': validated_data['clinic']['id'],
                'clinic_name': validated_data['clinic']['name'],
                'physician_id': validated_data['physician']['id'],
                'physician_name': validated_data['physician']['name'],
                'physician_crm': validated_data['physician']['crm'],
                'patient_id': validated_data['patient']['id'],
                'patient_name': validated_data['patient']['name'],
                'patient_email': validated_data['patient']['email'],
                'patient_phone': validated_data['patient']['phone'],
            }
            _metric = self.external_request(
                service=settings.EXTERNAL_METRIC,
                endpoint=f'/metrics/',
                method='POST',
                data=metrics_data,
            )
        except KeyError:
            raise serializers.ValidationError('Bad formed external resources data')

        request_data = {
            'clinic_id': validated_data['clinic']['id'],
            'physician_id': validated_data['physician']['id'],
            'patient_id': validated_data['patient']['id'],
            'description': validated_data['text'],
        }
        return Prescription.objects.create(**request_data)
