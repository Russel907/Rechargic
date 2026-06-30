from rest_framework import serializers
from .models import LegalDocument

class LegalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = ['doc_type', 'title', 'content_html', 'version', 'effective_date', 'last_updated']