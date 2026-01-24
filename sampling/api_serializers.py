from django.utils import timezone
from rest_framework import serializers
from sampling.models import FishSampling, PondFishStock
from sampling.services import create_sampling_from_batches


class PondFishStockSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = PondFishStock
        fields = ["id", "display_name"]

    def get_display_name(self, obj):
        return str(obj)


class FishSamplingSerializer(serializers.ModelSerializer):
    fish_stock = PondFishStockSerializer(read_only=True)

    average_weight = serializers.SerializerMethodField()
    growth_from_previous = serializers.SerializerMethodField()
    growth_percentage = serializers.SerializerMethodField()
    growth_status = serializers.SerializerMethodField()

    class Meta:
        model = FishSampling
        fields = [
            "id",
            "fish_stock",
            "sampled_on",
            "sample_fish_count",
            "sample_total_weight",
            "average_weight",
            "growth_from_previous",
            "growth_percentage",
            "growth_status",
        ]

    def get_average_weight(self, obj):
        return obj.average_weight

    def get_growth_from_previous(self, obj):
        return obj.growth_from_previous

    def get_growth_percentage(self, obj):
        return obj.growth_percentage

    def get_growth_status(self, obj):
        return obj.growth_status


class FishSamplingCreateSerializer(serializers.Serializer):
    fish_stock = serializers.PrimaryKeyRelatedField(
        queryset=PondFishStock.objects.all()
    )
    sampled_on = serializers.DateField()
    batch_size = serializers.IntegerField(min_value=1, write_only=True)
    batches = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        write_only=True,
    )

    def validate_sampled_on(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "Sampled date cannot be in the future."
            )
        return value

    def validate(self, attrs):
        exists = FishSampling.objects.filter(
            fish_stock=attrs["fish_stock"],
            sampled_on=attrs["sampled_on"]
        ).exists()

        if exists:
            raise serializers.ValidationError(
                "Sampling already exists for this fish stock on this date."
            )
        return attrs

    def create(self, validated_data):
        return create_sampling_from_batches(
            fish_stock=validated_data["fish_stock"],
            sampled_on=validated_data["sampled_on"],
            batch_size=validated_data["batch_size"],
            batches=validated_data["batches"],
        )


