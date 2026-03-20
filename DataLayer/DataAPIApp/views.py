#By Tejas Kumar
#This module is where we declare the ViewPoints that use the serializers to prep the data and send through to the endpoints. 
#Using filterset_fields, we can dictate which arguments are sent for filtering. 

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from .models import (
    Economic_Region_Employment_Estimate,
    Economic_Region_Vacancy_Wage_Estimate,
    EconomicRegion,
    NOC_Level,
    NOCGrouping,
    NOCClass,
    ProgramCategory,
    Program_NOC_Link,
    Program_University_KPI,
    Province,
    Provincial_NOC_Group_Labor_Statistic,
    University,
    PredictionCache,
    SeasonalDecomposition
)
from .serializers import (
    Economic_Region_Employment_EstimateSerializer,
    Economic_Region_Vacancy_Wage_EstimateSerializer,
    EconomicRegionSerializer,
    NOC_LevelSerializer,
    NOCGroupingSerializer,
    NOCClassSerializer,
    ProgramCategorySerializer,
    Program_NOC_LinkSerializer,
    Program_University_KPISerializer,
    ProvinceSerializer,
    Provincial_NOC_Group_Labor_StatisticSerializer,
    UniversitySerializer,
    PredictionCacheSerializer,
    SeasonalDecompositionSerializer
)


# Enable filtering on all fields for each viewset
class Economic_Region_Employment_EstimateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Economic_Region_Employment_Estimate.objects.all()
    serializer_class = Economic_Region_Employment_EstimateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class Economic_Region_Vacancy_Wage_EstimateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Economic_Region_Vacancy_Wage_Estimate.objects.all()
    serializer_class = Economic_Region_Vacancy_Wage_EstimateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class EconomicRegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EconomicRegion.objects.all()
    serializer_class = EconomicRegionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class NOC_LevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NOC_Level.objects.all()
    serializer_class = NOC_LevelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class NOCGroupingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NOCGrouping.objects.all()
    serializer_class = NOCGroupingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class NOCClassViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NOCClass.objects.all()
    serializer_class = NOCClassSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class ProgramCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProgramCategory.objects.all()
    serializer_class = ProgramCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class Program_NOC_LinkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Program_NOC_Link.objects.all()
    serializer_class = Program_NOC_LinkSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class Program_University_KPIViewSet_Latest(viewsets.ReadOnlyModelViewSet):
    queryset = Program_University_KPI.objects.all()
    serializer_class = Program_University_KPISerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class Provincial_NOC_Group_Labor_StatisticViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Provincial_NOC_Group_Labor_Statistic.objects.all()
    serializer_class = Provincial_NOC_Group_Labor_StatisticSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class UniversityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

class PredictionCacheViewSet(viewsets.ModelViewSet):
    queryset = PredictionCache.objects.all()
    serializer_class = PredictionCacheSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

    def create(self, request, *args, **kwargs):
        data = request.data
        many = isinstance(data, list) 
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SeasonalDecompositionViewSet(viewsets.ModelViewSet):
    queryset = SeasonalDecomposition.objects.all()
    serializer_class = SeasonalDecompositionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

