from rest_framework import serializers
from .models import Survey


class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['preferred_genres', 'viewing_reason', 'viewing_with',
                 'favorite_actor', 'movie_elements', 'favorite_movies']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance