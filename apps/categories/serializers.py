from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('code',)

class CategoryDetailSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    asset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('code',)
    
    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.all(), many=True).data 