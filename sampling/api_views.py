from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from sampling.models import FishSampling
from .models import PondFishStock
from .api_serializers import PondFishStockSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
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


class PondStockListCreateAPI(ListCreateAPIView):
    serializer_class = PondFishStockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PondFishStock.objects.filter(
            user=self.request.user,
            status=PondFishStock.ACTIVE
        ).select_related("pond", "species")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class PondStockCloseAPI(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            stock = PondFishStock.objects.get(pk=pk, user=request.user)
        except PondFishStock.DoesNotExist:
            return Response(
                {"error": "Stock not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        stock.close()  # uses your model method
        return Response(
            {"message": "Stock closed successfully"},
            status=status.HTTP_200_OK
        )
