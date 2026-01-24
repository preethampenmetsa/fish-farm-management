from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from sampling.models import FishSampling
from sampling.api_serializers import (
    FishSamplingSerializer,
    FishSamplingCreateSerializer,
)


class FishSamplingListAPI(ListAPIView):
    # queryset = FishSampling.objects.all().order_by("-sampled_on")
    serializer_class = FishSamplingSerializer

    def get_queryset(self):
        queryset = FishSampling.objects.all().order_by("-sampled_on")

        fish_stock = self.request.query_params.get("fish_stock")
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")

        if fish_stock:
            queryset = queryset.filter(fish_stock_id=fish_stock)

        if from_date:
            queryset = queryset.filter(sampled_on__gte=from_date)

        if to_date:
            queryset = queryset.filter(sampled_on__lte=to_date)

        return queryset


class FishSamplingDetailAPI(RetrieveAPIView):
    queryset = FishSampling.objects.all()
    serializer_class = FishSamplingSerializer

class FishSamplingCreateAPI(CreateAPIView):
    queryset = FishSampling.objects.all()
    serializer_class = FishSamplingCreateSerializer

    def create(self, request, *args, **kwargs):
        # 1. Validate + save using CREATE serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # 2. Serialize response using READ serializer
        response_serializer = FishSamplingSerializer(instance)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )