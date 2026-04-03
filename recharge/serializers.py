from rest_framework import serializers
from .models import Operator, Circle, Plan


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['id', 'name', 'code', 'logo']


class CircleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circle
        fields = ['id', 'name', 'code']


class PlanSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    circle_name = serializers.CharField(source='circle.name', read_only=True)

    class Meta:
        model = Plan
        fields = [
            'id',
            'operator_name',
            'circle_name',
            'plan_type',
            'price',
            'validity',
            'data',
            'calls',
            'includes',
            'is_trending',
            'is_best_value',
        ]