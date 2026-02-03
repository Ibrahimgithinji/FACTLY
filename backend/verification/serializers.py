from rest_framework import serializers
from typing import Dict, Any, List
from datetime import datetime


class VerificationRequestSerializer(serializers.Serializer):
    """Serializer for verification request data."""
    text = serializers.CharField(required=False, allow_blank=True)
    url = serializers.URLField(required=False, allow_blank=True)
    language = serializers.CharField(required=False, default='en', max_length=10)

    def validate(self, data):
        """Validate that either text or url is provided."""
        if not data.get('text') and not data.get('url'):
            raise serializers.ValidationError("Either 'text' or 'url' must be provided.")
        return data


class ComponentScoreSerializer(serializers.Serializer):
    """Serializer for component score data."""
    name = serializers.CharField()
    score = serializers.FloatField()
    weight = serializers.FloatField()
    weighted_score = serializers.FloatField()
    justification = serializers.CharField()
    evidence = serializers.ListField(child=serializers.CharField())


class FactlyScoreResultSerializer(serializers.Serializer):
    """Serializer for Factly Score™ result."""
    factly_score = serializers.IntegerField()
    classification = serializers.CharField()
    confidence_level = serializers.CharField()
    components = ComponentScoreSerializer(many=True)
    justifications = serializers.ListField(child=serializers.CharField())
    evidence_summary = serializers.DictField()
    timestamp = serializers.DateTimeField()
    metadata = serializers.DictField()


class VerificationResponseSerializer(serializers.Serializer):
    """Serializer for complete verification response."""
    original_text = serializers.CharField()
    extracted_content = serializers.DictField(required=False)
    nlp_analysis = serializers.DictField(required=False)
    fact_checking_results = serializers.DictField()
    factly_score = FactlyScoreResultSerializer()
    processing_time = serializers.FloatField()
    api_sources = serializers.ListField(child=serializers.CharField())
    timestamp = serializers.DateTimeField()