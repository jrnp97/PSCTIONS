""" Module to define viewsets """

from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from prescription.models import Prescription

from prescription.api.serializers import PrescriptionSerializer


class PrescriptionViewSet(GenericViewSet, CreateModelMixin):
    """ Class to manage view set logic """
    queryset = Prescription.objects.none()
    serializer_class = PrescriptionSerializer
