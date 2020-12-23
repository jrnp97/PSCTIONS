from rest_framework.routers import SimpleRouter

from prescription.api.viewsets import PrescriptionViewSet

router = SimpleRouter()
router.register(prefix='prescriptions', viewset=PrescriptionViewSet)

app_name = 'prescription_api'
urlpatterns = router.urls
