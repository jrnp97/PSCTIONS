""" Module to define API Test Cases """
from django.test import TestCase

from prescription.models import Prescription


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
        self.response = {
            'data': dict(self.test_data),
        }

    def test_should_only_accept_post_method(self):
        invalid_method = [
            'get',
            'put',
            'path',
            'head',
            'delete',
        ]
        for method in invalid_method:
            response = getattr(self.client, method)(self.ENDPOINT)
            self.assertEqual(response.status_code, 405)

        # TODO Mock Request good response
        response = self.client.post(
            self.ENDPOINT,
            data=self.test_data,
        )
        self.assertJSONEqual(raw=response.content, expected_data=self.response)

    def test_should_response_equal_data_sent_and_save_data_on_db(self):
        # TODO Mock Request response
        response = self.client.post(
            self.ENDPOINT,
            data=self.test_data,
        )
        self.assertJSONEqual(raw=response.content, expected_data=self.response)
        db_data = Prescription.objects.all()
        self.assertEqual(db_data.count(), 1)
        db_data = db_data.get()
        self.assertEqual(db_data.client_id, self.test_data['client']['id'])
        self.assertEqual(db_data.patient_id, self.test_data['patient']['id'])
        self.assertEqual(db_data.physician_id, self.test_data['physician']['id'])
        self.assertEqual(db_data.description, self.test_data['text'])

    def test_should_response_code_error_on_failure(self):
        """ Testing code error message when a failure happen on request process """
        error_response = {
            'error': {
                'message': 'malformed request',
                'code': '01',
            },
        }
        response = self.client.post(
            path=self.ENDPOINT,
            data={'clinic': 1},
        )
        self.assertJSONEqual(raw=response.content, expected_data=error_response)

        # Testing error code 02
        error_response['error']['message'] = 'physician not found'
        error_response['error']['code'] = '02'

        # TODO Mock Request failure
        response = self.client.post(
            path=self.ENDPOINT,
            data=self.test_data
        )
        self.assertJSONEqual(raw=response.content, expected_data=error_response)

        # Testing error code 03
        error_response['error']['message'] = 'patient not found'
        error_response['error']['code'] = '03'

        # TODO Mock Request failure
        response = self.client.post(
            path=self.ENDPOINT,
            data=self.test_data
        )
        self.assertJSONEqual(raw=response.content, expected_data=error_response)

        # Testing error code 04
        error_response['error']['message'] = 'metrics service not available'
        error_response['error']['code'] = '04'

        # TODO Mock Request failure
        response = self.client.post(
            path=self.ENDPOINT,
            data=self.test_data
        )
        self.assertJSONEqual(raw=response.content, expected_data=error_response)

        # Testing error code 05
        error_response['error']['message'] = 'physicians service not available'
        error_response['error']['code'] = '05'

        # TODO Mock Request failure
        response = self.client.post(
            path=self.ENDPOINT,
            data=self.test_data
        )
        self.assertJSONEqual(raw=response.content, expected_data=error_response)

        # Testing error code 06
        error_response['error']['message'] = 'patients service not available'
        error_response['error']['code'] = '06'

        # TODO Mock Request failure
        response = self.client.post(
            path=self.ENDPOINT,
            data=self.test_data
        )
        self.assertJSONEqual(raw=response.content, expected_data=error_response)
