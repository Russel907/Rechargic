from django.db import models

class LegalDocument(models.Model):
    DOC_TYPES = [
        ('terms', 'Terms and Conditions'),
        ('privacy', 'Privacy Policy'),
        ('refund', 'Refund and Cancellation Policy'),
    ]

    doc_type = models.CharField(max_length=20, choices=DOC_TYPES, unique=True)
    title = models.CharField(max_length=200)
    content_html = models.TextField()  # full HTML content
    version = models.CharField(max_length=20, default='1.0')
    effective_date = models.DateField()
    last_updated = models.DateField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (v{self.version})"