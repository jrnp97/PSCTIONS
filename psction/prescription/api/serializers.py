""" Module to define api serializer to define api data sctructure and validations """
from django.conf import settings

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from prescription.models import Prescription

from prescription.utils import ExternalServiceContext


class PrescriptionSerializer(serializers.Serializer):
    """ Class defining Prescription api schema """
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

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception=False)
        if not is_valid and raise_exception and self.errors.__len__() > 1:
            raise serializers.ValidationError(
                detail={
                    'error': {
                        'message': 'malformed request',
                        'code': '01',
                    }
                },
            )
        elif not is_valid and raise_exception:
            error = list(self.errors.values())[0]
            raise serializers.ValidationError(ReturnDict(error, serializer=self))
        return is_valid

    @staticmethod
    def external_request(service, endpoint, method='GET', data=None):
        manager = ExternalServiceContext(
            service=service,
            method=method,
            endpoint=endpoint,
            data=data,
        )
        return manager.do_request()

    @staticmethod
    def get_metric_data(validated_data):
        try:
            return {
                'clinic_id': validated_data['clinic']['id'] if validated_data.get('clinic') else None,
                'clinic_name': validated_data['clinic']['name'] if validated_data.get('clinic') else None,
                'physician_id': validated_data['physician']['id'],
                'physician_name': validated_data['physician']['name'],
                'physician_crm': validated_data['physician']['crm'],
                'patient_id': validated_data['patient']['id'],
                'patient_name': validated_data['patient']['name'],
                'patient_email': validated_data['patient']['email'],
                'patient_phone': validated_data['patient']['phone'],
            }
        except KeyError:
            raise serializers.ValidationError(
                detail={
                    'error': {
                        'message': 'malformed external resources data',
                        'code': '07',
                    },
                },
            )

    def validate_clinic(self, value):
        if 'id' not in value:
            return None
        return self.external_request(
            service=settings.EXTERNAL_CLINIC,
            endpoint=f'/clinics/{value["id"]}/',
        )

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
        _metric = self.external_request(
            service=settings.EXTERNAL_METRIC,
            endpoint=f'/metrics/',
            method='POST',
            data=self.get_metric_data(validated_data),
        )

        request_data = {
            'clinic_id': validated_data['clinic']['id'],
            'physician_id': validated_data['physician']['id'],
            'patient_id': validated_data['patient']['id'],
            'description': validated_data['text'],
        }
        return Prescription.objects.create(**request_data)
