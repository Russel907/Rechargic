from django.urls import path
from .views import LegalDocumentView, LegalDocumentListView

urlpatterns = [
    path('all/', LegalDocumentListView.as_view(), name='legal-all'),
    path('<str:doc_type>/', LegalDocumentView.as_view(), name='legal-detail'),
]