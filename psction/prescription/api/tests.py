""" Module to define API Test Cases """
from unittest.mock import patch
from django.test import TestCase

from rest_framework import status

from prescription.exceptions import ExternalApiError, ExternalResourceNotFound
from prescription.models import Prescription

from prescription.utils import MetricExternalService
from prescription.utils import ClientExternalService
from prescription.utils import PatientExternalService
from prescription.utils import PhysicianExternalService


class TestApiPrescriptionEndpoint(TestCase):
    """ Test for tests /prescriptions endpoint cases """
    ENDPOINT = '/prescriptions'
    FAKE_PHYSICIAN_RESPONSE = {
        'id': '1',
        'name': 'Caesar Collins',
        'crm': 'e0d80e9f-5129-4636-b3b6-d9afba4d53c5'
    }
    FAKE_CLINIC_RESPONSE = {
        'id': '1',
        'name': 'Elenor Mraz'
    }
    FAKE_PATIENT_RESPONSE = {
        'id': '1',
        'name': 'Vita Mante',
        'email': 'Herta38@hotmail.com',
        'phone': '702.043.4233 x475',
    }

    FAKE_METRIC_RESPONSE = {
        'id': 1,
        'clinic_id': 1,
        'clinic_name': 'Clinica A',
        'physician_id': 1,
        'physician_name': 'Dr. João',
        'physician_crm': 'SP293893',
        'patient_id': 1,
        'patient_name': 'Rodrigo',
        'patient_email': 'rodrigo@gmail.com',
        'patient_phone': '(16)998765625',
    }

    def setUp(self):
        self.test_data = {
            'clinic': {
                'id': 1,
            },
            'physician': {
                'id': 1,
            },
            'patient': {
                'id': 1,
            },
            'text': 'Dipirona 1x ao dia',
        }
        aux = dict(self.test_data)
        aux['id'] = 1
        self.response = {
            'data': aux,
        }

    def create_prescription(self):
        with patch.object(
                MetricExternalService,
                'do_request',
                return_value=self.FAKE_METRIC_RESPONSE) as service_metric, \
             patch.object(
                 ClientExternalService,
                 'do_request',
                 return_value=self.FAKE_CLINIC_RESPONSE) as service_client, \
             patch.object(
                 PatientExternalService,
                 'do_request',
                 return_value=self.FAKE_PATIENT_RESPONSE) as service_patient, \
             patch.object(
                 PhysicianExternalService,
                 'do_request',
                 return_value=self.FAKE_PHYSICIAN_RESPONSE) as service_physician:
            response = self.client.post(
                self.ENDPOINT,
                data=self.test_data,
                content_type='application/json',
            )
            service_metric.assert_called_once()
            service_client.assert_called_once()
            service_patient.assert_called_once()
            service_physician.assert_called_once()
        self.assertJSONEqual(raw=response.content, expected_data=self.response)

    def test_should_only_accept_post_method(self):
        invalid_method = [
            'get',
            'put',
            'patch',
            'head',
            'delete',
        ]
        for method in invalid_method:
            response = getattr(self.client, method)(path=self.ENDPOINT)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.create_prescription()

    def test_should_response_equal_data_sent_and_save_data_on_db(self):
        """ Testing persistent request data on service, and response format """
        self.create_prescription()
        db_data = Prescription.objects.all()
        self.assertEqual(db_data.count(), 1)
        db_data = db_data.get()
        self.assertEqual(db_data.clinic_id, self.test_data['clinic']['id'])
        self.assertEqual(db_data.patient_id, self.test_data['patient']['id'])
        self.assertEqual(db_data.physician_id, self.test_data['physician']['id'])
        self.assertEqual(db_data.description, self.test_data['text'])

    def test_should_response_code_one_when_malformed_data(self):
        """ Testing Error response with code 01 for malformed requests """
        error_response = {
            'error': {
                'message': 'malformed request',
                'code': '01',
            },
        }
        payloads = [
            {'clinic': 1},
            {},
            {
                'clic': {
                    'id': 1,
                },
                'phys': {
                    'id': 1,
                },
                'patent': {
                    'id': 1,
                },
                'text': 'Dipirona 1x ao dia',
            }
        ]
        for data in payloads:
            response = self.client.post(
                path=self.ENDPOINT,
                data=data,
                content_type='application/json',
            )
            self.assertJSONEqual(raw=response.content, expected_data=error_response)

    def test_should_response_code_error_two_or_five_for_physician_failure(self):
        """ Testing response error codes 02, 05 for Physician service errors """
        error_response = {
            'error': {
                'message': 'physician not found',
                'code': '02',
            },
        }
        with patch.object(MetricExternalService, 'do_request', return_value=self.FAKE_METRIC_RESPONSE), \
                patch.object(ClientExternalService, 'do_request', return_value=self.FAKE_CLINIC_RESPONSE), \
                patch.object(PatientExternalService, 'do_request', return_value=self.FAKE_PATIENT_RESPONSE), \
                patch.object(PhysicianExternalService, '_api_request', side_effect=ExternalResourceNotFound):
            response = self.client.post(
                path=self.ENDPOINT,
                data=self.test_data,
                content_type='application/json',
            )
            self.assertJSONEqual(raw=response.content, expected_data=error_response)

        error_response = {
            'error': {
                'message': 'physicians service not available',
                'code': '05',
            },
        }
        with patch.object(MetricExternalService, 'do_request', return_value=self.FAKE_METRIC_RESPONSE), \
                patch.object(ClientExternalService, 'do_request', return_value=self.FAKE_CLINIC_RESPONSE), \
                patch.object(PatientExternalService, 'do_request', return_value=self.FAKE_PATIENT_RESPONSE), \
                patch.object(PhysicianExternalService, '_api_request', side_effect=ExternalApiError):
            response = self.client.post(
                path=self.ENDPOINT,
                data=self.test_data,
                content_type='application/json',
            )
            self.assertJSONEqual(raw=response.content, expected_data=error_response)

    def test_should_response_code_error_three_or_six_for_patient_failure(self):
        """ Testing response error codes 03, 06 for patient service errors """
        error_response = {
            'error': {
                'message': 'patient not found',
                'code': '03',
            },
        }
        with patch.object(MetricExternalService, 'do_request', return_value=self.FAKE_METRIC_RESPONSE), \
             patch.object(ClientExternalService, 'do_request', return_value=self.FAKE_CLINIC_RESPONSE), \
             patch.object(PatientExternalService, '_api_request', side_effect=ExternalResourceNotFound), \
             patch.object(PhysicianExternalService, 'do_request', return_value=self.FAKE_PHYSICIAN_RESPONSE):
            response = self.client.post(
                path=self.ENDPOINT,
                data=self.test_data,
                content_type='application/json',
            )
            self.assertJSONEqual(raw=response.content, expected_data=error_response)

        error_response = {
            'error': {
                'message': 'patients service not available',
                'code': '06',
            },
        }
        with patch.object(MetricExternalService, 'do_request', return_value=self.FAKE_METRIC_RESPONSE), \
             patch.object(ClientExternalService, 'do_request', return_value=self.FAKE_CLINIC_RESPONSE), \
             patch.object(PatientExternalService, '_api_request', side_effect=ExternalApiError), \
             patch.object(PhysicianExternalService, 'do_request', return_value=self.FAKE_PHYSICIAN_RESPONSE):
            response = self.client.post(
                path=self.ENDPOINT,
                data=self.test_data,
                content_type='application/json',
            )
            self.assertJSONEqual(raw=response.content, expected_data=error_response)

    def test_should_response_code_error_four_for_metric_failure(self):
        """ Testing response error codes 04 for metric service error, and return 500 response if detect a
         ExternalResourceNotFound Exception """
        error_response = {
            'error': {
                'message': 'metrics service not available',
                'code': '04',
            },
        }
        with patch.object(MetricExternalService, '_api_request', side_effect=ExternalApiError), \
             patch.object(ClientExternalService, 'do_request', return_value=self.FAKE_CLINIC_RESPONSE), \
             patch.object(PatientExternalService, 'do_request', return_value=self.FAKE_PATIENT_RESPONSE), \
             patch.object(PhysicianExternalService, 'do_request', return_value=self.FAKE_PHYSICIAN_RESPONSE):
            response = self.client.post(
                path=self.ENDPOINT,
                data=self.test_data,
                content_type='application/json',
            )
            self.assertJSONEqual(raw=response.content, expected_data=error_response)

        with patch.object(MetricExternalService, '_api_request', side_effect=ExternalResourceNotFound), \
             patch.object(ClientExternalService, 'do_request', return_value=self.FAKE_CLINIC_RESPONSE), \
             patch.object(PatientExternalService, 'do_request', return_value=self.FAKE_PATIENT_RESPONSE), \
             patch.object(PhysicianExternalService, 'do_request', return_value=self.FAKE_PHYSICIAN_RESPONSE):
            with self.assertRaises(ExternalResourceNotFound):
                self.client.post(
                    path=self.ENDPOINT,
                    data=self.test_data,
                    content_type='application/json',
                )

    def test_should_response_code_error_seven_when_some_service_give_info_with_unexpected_schema(self):
        """ Testing case where some patient, physician or client service give unexpected dictionary of data
        unable to create metrics information, server should response with error code 07 """
        error_response = {
            'error': {
                'message': 'malformed external resources data',
                'code': '07',
            },
        }
        with patch.object(MetricExternalService, 'do_request', return_value=self.FAKE_METRIC_RESPONSE), \
             patch.object(ClientExternalService, 'do_request', return_value=self.FAKE_CLINIC_RESPONSE), \
             patch.object(PatientExternalService, 'do_request', return_value={'test': 'malformed'}), \
             patch.object(PhysicianExternalService, 'do_request', return_value=self.FAKE_PHYSICIAN_RESPONSE):
            response = self.client.post(
                path=self.ENDPOINT,
                data=self.test_data,
                content_type='application/json',
            )
            self.assertJSONEqual(raw=response.content, expected_data=error_response)

        with patch.object(MetricExternalService, 'do_request', return_value=self.FAKE_METRIC_RESPONSE), \
             patch.object(ClientExternalService, 'do_request', return_value={'test': 'malformed'}), \
             patch.object(PatientExternalService, 'do_request', return_value=self.FAKE_PATIENT_RESPONSE), \
             patch.object(PhysicianExternalService, 'do_request', return_value=self.FAKE_PHYSICIAN_RESPONSE):
            response = self.client.post(
                path=self.ENDPOINT,
                data=self.test_data,
                content_type='application/json',
            )
            self.assertJSONEqual(raw=response.content, expected_data=error_response)

        with patch.object(MetricExternalService, 'do_request', return_value=self.FAKE_METRIC_RESPONSE), \
             patch.object(ClientExternalService, 'do_request', return_value=self.FAKE_CLINIC_RESPONSE), \
             patch.object(PatientExternalService, 'do_request', return_value=self.FAKE_PATIENT_RESPONSE), \
             patch.object(PhysicianExternalService, 'do_request', return_value={'test': 'malformed'}):
            response = self.client.post(
                path=self.ENDPOINT,
                data=self.test_data,
                content_type='application/json',
            )
            self.assertJSONEqual(raw=response.content, expected_data=error_response)