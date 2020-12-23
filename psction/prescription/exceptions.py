""" Module to define custom exceptions """
from urllib.error import HTTPError


class ExternalApiError(HTTPError):
    """ Exception to segment external api conexion error """


class ExternalResourceNotFound(ExternalApiError):
    """ Exception to segment external api with 404 response """
