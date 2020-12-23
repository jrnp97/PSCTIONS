""" Module to define API Urls and routing """
from django.urls import path

from django.views.generic import TemplateView

from rest_framework.routers import SimpleRouter

from prescription.api.viewsets import PrescriptionViewSet

router = SimpleRouter(trailing_slash=False)
router.register(prefix='prescriptions', viewset=PrescriptionViewSet)

app_name = 'prescription_api'
urlpatterns = router.urls

urlpatterns.extend(
    [
        path('docs/', TemplateView.as_view(
            template_name='redoc.html',
            extra_context={
                'schema_static': 'prescription_api/openapi-schema.yml',
                'main_title': 'Prescription Service',
            },
        ), name='doc'),
    ]
)
