""" Module to define app utils """
import json

from urllib.parse import urljoin

from urllib.error import HTTPError

from urllib.request import urlopen
from urllib.request import Request

from django.conf import settings

from rest_framework import status, serializers

from prescription.exceptions import ExternalApiError
from prescription.exceptions import ExternalResourceNotFound


def prepare_request_obj(config: dict, method: str, endpoint: str, **kwargs) -> Request:  # TODO Test
    """ Function to preparate and create Request object for service specified """
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
    try:
        response = urlopen(
            request_obj,
            timeout=timeout,
        )
    except HTTPError:
        raise ExternalApiError
    if response.status == status.HTTP_404_NOT_FOUND:
        raise ExternalResourceNotFound
    try:
        return json.loads(response.read())
    except ValueError:
        raise ExternalApiError


class ClientExternalService:
    """ Strategy for Client External Service to connect and trigger Validation errors """

    def __init__(self, method: str, endpoint: str, **kwargs) -> None:
        """ Initializing ExternalService to configure request object with service config. """
        self.service_name = settings.EXTERNAL_CLINIC.lower()
        self.config = dict(settings.EXTERNAL_SERVICES[settings.EXTERNAL_CLINIC])
        self.request_obj = prepare_request_obj(
            config=self.config,
            method=method,
            endpoint=endpoint,
            **kwargs,
        )

    def _api_request(self):
        return api_request(
            request_obj=self.request_obj,
            timeout=30,
        )

    def do_request(self) -> dict:
        try:
            return self._api_request()
        except ExternalApiError:
            return {}


class PatientExternalService:
    """ Strategy for Patient External Service to connect and trigger Validation errors """

    def __init__(self, method: str, endpoint: str, **kwargs) -> None:
        """ Initializing ExternalService to configure request object with service config. """
        self.service_name = settings.EXTERNAL_PATIENT.lower()
        self.config = dict(settings.EXTERNAL_SERVICES[settings.EXTERNAL_PATIENT])
        self.request_obj = prepare_request_obj(
            config=self.config,
            method=method,
            endpoint=endpoint,
            **kwargs,
        )

    def _api_request(self):
        return api_request(
            request_obj=self.request_obj,
            timeout=30,
        )

    def do_request(self) -> dict:
        try:
            return self._api_request()
        except ExternalResourceNotFound:
            raise serializers.ValidationError(
                detail={
                    'error': {
                        'message': f'{self.service_name} not found',
                        'code': '03',
                    }
                },
            )
        except ExternalApiError:
            raise serializers.ValidationError(
                detail={
                    'error': {
                        'message': f'{self.service_name}s service not available',
                        'code': '06',
                    }
                },
            )


class PhysicianExternalService:
    """ Strategy for Physician External Service to connect and trigger Validation errors """

    def __init__(self, method: str, endpoint: str, **kwargs) -> None:
        """ Initializing ExternalService to configure request object with service config. """
        self.service_name = settings.EXTERNAL_PHYSICIAN.lower()
        self.config = dict(settings.EXTERNAL_SERVICES[settings.EXTERNAL_PHYSICIAN])
        self.request_obj = prepare_request_obj(
            config=self.config,
            method=method,
            endpoint=endpoint,
            **kwargs,
        )

    def _api_request(self):
        return api_request(
            request_obj=self.request_obj,
            timeout=30,
        )

    def do_request(self) -> dict:
        try:
            return self._api_request()
        except ExternalResourceNotFound:
            raise serializers.ValidationError(
                detail={
                    'error': {
                        'message': f'{self.service_name} not found',
                        'code': '02',
                    }
                },
            )
        except ExternalApiError:
            raise serializers.ValidationError(
                detail={
                    'error': {
                        'message': f'{self.service_name}s service not available',
                        'code': '05',
                    }
                },
            )


class MetricExternalService:
    """ Strategy for Metric External Service to connect and trigger Validation errors """

    def __init__(self, method: str, endpoint: str, **kwargs) -> None:
        """ Initializing ExternalService to configure request object with service config. """
        self.service_name = settings.EXTERNAL_METRIC.lower()
        self.config = dict(settings.EXTERNAL_SERVICES[settings.EXTERNAL_METRIC])
        self.request_obj = prepare_request_obj(
            config=self.config,
            method=method,
            endpoint=endpoint,
            **kwargs,
        )

    def _api_request(self):
        return api_request(
            request_obj=self.request_obj,
            timeout=30,
        )

    def do_request(self) -> dict:
        try:
            return self._api_request()
        except ExternalApiError:
            raise serializers.ValidationError(
                detail={
                    'error': {
                        'message': f'{self.service_name}s service not available',
                        'code': '04',
                    },
                },
            )


class ExternalServiceContext:
    """ Class to manage context of external service request """

    def __init__(self, service: str, method: str, endpoint: str, **kwargs) -> None:
        """ Initializing ExternalService Connector to configure request object with service config. """
        strategies = {
            settings.EXTERNAL_CLINIC: ClientExternalService,
            settings.EXTERNAL_METRIC: MetricExternalService,
            settings.EXTERNAL_PATIENT: PatientExternalService,
            settings.EXTERNAL_PHYSICIAN: PhysicianExternalService,
        }
        if service not in settings.EXTERNAL_SERVICES.keys():
            raise ValueError(f'{service} is not a valid external service, please configure it.')

        if not isinstance(settings.EXTERNAL_SERVICES[service], dict):
            raise ValueError(f'{service} config has not a valid value.')

        self.strategy = strategies[service](
            method=method,
            endpoint=endpoint,
            **kwargs,
        )

    def do_request(self) -> dict:
        """ Method to perform configured request to server """
        return self.strategy.do_request()
