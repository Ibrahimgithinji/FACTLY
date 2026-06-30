from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Classification(models.TextChoices):
    TRUE = 'true', 'True'
    MOSTLY_TRUE = 'mostly_true', 'Mostly True'
    HALF_TRUE = 'half_true', 'Half True'
    MISLEADING = 'misleading', 'Misleading'
    FALSE = 'false', 'False'
    UNVERIFIABLE = 'unverifiable', 'Unverifiable'
    UNKNOWN = 'unknown', 'Unknown'


class VerificationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    claim = models.TextField()
    overall_confidence = models.FloatField(default=0.0)
    factly_score = models.IntegerField(default=0)
    classification = models.CharField(
        max_length=20,
        choices=Classification.choices,
        default=Classification.UNKNOWN,
    )
    source = models.CharField(max_length=100, default='api')
    api_sources = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.claim[:60]}... ({self.classification})'

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self):
        return self.deleted_at is not None


class PasswordResetToken(models.Model):
    """Model to store password reset tokens for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='password_reset_token')
    token = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Password reset token for {self.user.email}"
    
    def is_valid(self):
        """Check if token is still valid (not expired and not used)"""
        return not self.is_used and timezone.now() < self.expires_at
    
    class Meta:
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"
