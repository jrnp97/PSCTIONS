""" Module to define prescription app tests """
from urllib.error import HTTPError
from urllib.request import Request
from unittest.mock import patch, MagicMock
from unittest.mock import Mock

from django.test import TestCase
from rest_framework import status
from rest_framework.utils import json

from prescription.exceptions import ExternalApiError, ExternalResourceNotFound
from prescription.utils import api_request
from prescription.utils import prepare_request_obj


# Create your tests here.

class TestingUtilFunction(TestCase):

    def test_should_prepare_request_obj_add_always_json_content_type_on_headers(self):
        """ Testing Content-Type header always with application/json value """
        config = {
            'base_url': 'http://8.8.8.8/',
        }
        request_ = prepare_request_obj(
            config=config,
            method='GET',
            endpoint='/test.html',
        )
        self.assertEqual(request_.headers.get('Content-type'), 'application/json')

    def test_should_prepare_request_obj_add_authorization_header_if_config_has_auth_toke(self):
        """ Testing Authorization header is set when config has auth_toke set """
        config = {
            'base_url': 'http://8.8.8.8/',
            'auth_token': 'JWT token_text',
        }
        request_ = prepare_request_obj(
            config=config,
            method='GET',
            endpoint='/test.html',
        )
        self.assertEqual(request_.headers.get('Authorization'), config['auth_token'])

    def test_should_prepare_request_obj_raise_key_error_if_config_has_not_base_url(self):
        """ Testing that fnc raise Key Error when config dict has not base_url information """
        configs = [
            {},
            {'base': 'tested'},
        ]
        for config in configs:
            with self.assertRaises(KeyError):
                prepare_request_obj(
                    config=config,
                    method='GET',
                    endpoint='/test.html',
                )

    def test_should_prepare_request_obj_accept_data_kwargs(self):
        """ Testing that fnc accept data kwargs and add it like requests payload, and dont add it
        when type is different of dict"""
        config = {
            'base_url': 'http://8.8.8.8/',
        }
        request_ = prepare_request_obj(
            config=config,
            method='GET',
            endpoint='/test.html',
            data='not inserted',
        )
        self.assertEqual(request_.data, None)
        data = {
            'testing': 'data payload',
        }
        request_ = prepare_request_obj(
            config=config,
            method='GET',
            endpoint='/test.html',
            data=data,
        )
        self.assertJSONEqual(request_.data, data)

    def test_should_prepare_request_obj_return_a_request_object(self):
        """ Testing that function return a urllib.request.Request object"""
        config = {
            'base_url': 'http://8.8.8.8/',
        }
        request_ = prepare_request_obj(
            config=config,
            method='GET',
            endpoint='/test.html',
        )
        self.assertIsInstance(request_, Request)

    @patch('prescription.utils.urlopen')
    def test_api_request_should_trigger_external_api_exc_when_has_bad_data_or_http_error(self, mocked_urlopen):
        """ Testing that ExternalApiException is raised when a non-json response is received and when
        a http error is raised"""
        config = {
            'base_url': 'http://8.8.8.8/',
        }
        request_ = prepare_request_obj(
            config=config,
            method='GET',
            endpoint='/test.html',
        )
        mocked_urlopen.side_effect = HTTPError(
            url='http://test.com',
            code=400,
            msg='bad response', hdrs={},
            fp=None
        )
        with self.assertRaises(ExternalApiError):
            api_request(request_obj=request_)
        mocked_urlopen.assert_called_once()
        mocked_urlopen.side_effect = None

        response_mock = Mock()
        response_mock.status.return_value = status.HTTP_200_OK
        response_mock.read.return_value = b'non-json response'
        mocked_urlopen.return_value = response_mock
        with self.assertRaises(ExternalApiError):
            api_request(request_obj=request_)
        response_mock.read.assert_called_once()

    @patch('prescription.utils.urlopen')
    def test_api_request_should_trigger_external_resource_not_found_when_a_404_response_happen(self, mocked_urlopen):
        """ Testing that ExternalResourceNotFound is raised when a 404 response happen """

        config = {
            'base_url': 'http://8.8.8.8/',
        }
        request_ = prepare_request_obj(
            config=config,
            method='GET',
            endpoint='/test.html',
        )

        response_mock = Mock()
        response_mock.status = status.HTTP_404_NOT_FOUND
        mocked_urlopen.return_value = response_mock

        with self.assertRaises(ExternalResourceNotFound):
            api_request(request_obj=request_)
        mocked_urlopen.assert_called_once()

    @patch('prescription.utils.urlopen')
    def test_api_request_should_return_a_dict_information(self, mocked_urlopen):
        """ Testing that function return a dict object """
        config = {
            'base_url': 'http://8.8.8.8/',
        }
        request_ = prepare_request_obj(
            config=config,
            method='GET',
            endpoint='/test.html',
        )
        raw_response = json.dumps({
            'testing': 'data',
        }).encode()
        response_mock = Mock()
        response_mock.status = 200
        response_mock.read.return_value = raw_response
        mocked_urlopen.return_value = response_mock
        response = api_request(request_obj=request_)
        self.assertJSONEqual(raw=raw_response, expected_data=response)
