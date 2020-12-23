""" Module to define custom exceptions """


class ExternalApiError(Exception):
    """ Exception to segment external api conexion error """


class ExternalResourceNotFound(Exception):
    """ Exception to segment external api with 404 response """
