from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LegalDocument
from .serializers import LegalDocumentSerializer


class LegalDocumentView(APIView):
    """
    GET /api/legal/terms/
    GET /api/legal/privacy/
    GET /api/legal/refund/
    """
    permission_classes = []  # public — no login needed, app store reviewers need access too

    def get(self, request, doc_type):
        try:
            doc = LegalDocument.objects.get(doc_type=doc_type, is_active=True)
        except LegalDocument.DoesNotExist:
            return Response(
                {"error": "Document not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = LegalDocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LegalDocumentListView(APIView):
    """
    GET /api/legal/all/  -> returns all 3 docs at once
    """
    permission_classes = []

    def get(self, request):
        docs = LegalDocument.objects.filter(is_active=True)
        serializer = LegalDocumentSerializer(docs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)