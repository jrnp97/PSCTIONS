""" Module to define viewsets """

from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from prescription.models import Prescription

from prescription.api.serializers import PrescriptionSerializer


class PrescriptionViewSet(GenericViewSet, CreateModelMixin):
    """ Class to manage view set logic """
    queryset = Prescription.objects.none()
    serializer_class = PrescriptionSerializer

    def create(self, request, *args, **kwargs):
        """ Override method to customize response format """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'data': serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
