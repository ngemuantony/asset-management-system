from rest_framework import serializers
from .models import Tag

class TagSerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('code',)

    def validate_color(self, value):
        """Validate color hex code"""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError(
                "Color must be a valid hex code (e.g., #FF0000)"
            )
        return value 