from rest_framework import serializers
from .models import User


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone']

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)