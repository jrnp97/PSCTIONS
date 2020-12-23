""" Module to define app utils """
import json

from urllib.parse import urljoin

from urllib.error import HTTPError

from urllib.request import urlopen
from urllib.request import Request

from django.conf import settings

from rest_framework import status

from prescription.exceptions import ExternalApiError
from prescription.exceptions import ExternalResourceNotFound


def prepare_request_obj(service: str, method: str, endpoint: str, **kwargs) -> Request:  # TODO Test
    """ Function to preparate and create Request object for service specified """
    if service not in settings.EXTERNAL_SERVICES.keys():
        raise ValueError(f'{service} is not a valid external service, please configure it.')

    if not isinstance(settings.EXTERNAL_SERVICES[service], dict):
        raise ValueError(f'{service} config has not a valid value.')

    config = dict(settings.EXTERNAL_SERVICES[service])
    request_data = {
        'method': method,
        'url': urljoin(base=config['base_url'], url=endpoint),
        'headers': {
            'Content-Type': 'application/json',
        },
    }
    if config.get('auth_token'):
        request_data['headers']['Authorization'] = f'{config["auth_token"]}'
    if kwargs.get('data') and isinstance(kwargs['data'], dict):
        request_data['data'] = bytes(
            json.dumps(kwargs['data']),
            encoding='utf-8',
        )

    return Request(**request_data)


def api_request(request_obj: Request, timeout=30) -> dict:  # TODO Test
    """ Method to perform a json api request with error handle """
    response = urlopen(
        request_obj,
        timeout=timeout,
    )
    if response.status == status.HTTP_404_NOT_FOUND:
        raise ExternalResourceNotFound
    try:
        return json.loads(response.read())
    except ValueError:
        raise HTTPError


class ExternalServiceConnector:
    """ Class to perform external service request and return data or correct validation error """

    def __init__(self, service: str, method: str, endpoint: str, **kwargs) -> None:
        """ Initializing ExternalService Connector to configure request object with service config. """
        self.service_name = service.lower()
        self.request_obj = prepare_request_obj(
            service=service,
            method=method,
            endpoint=endpoint,
            **kwargs,
        )

    def do_request(self) -> dict:
        """ Method to perform configured request to server """
        try:
            return api_request(
                request_obj=self.request_obj,
                timeout=30,
            )
        except HTTPError:
            raise ExternalApiError

