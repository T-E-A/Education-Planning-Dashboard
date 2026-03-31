# By: Tejas Kumar
# This module is where we declare the ViewPoints that use the serializers to prep the data and send through to the endpoints. 
# Using filterset_fields, we can dictate which arguments are sent for filtering. 

from rest_framework import viewsets
from django.http import JsonResponse
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

# viewset for econmic region employment estimate records
class Economic_Region_Employment_EstimateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Economic_Region_Employment_Estimate.objects.all()
    serializer_class = Economic_Region_Employment_EstimateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for economic region vacancy and wage estimate records, supports filtering on all fields 
class Economic_Region_Vacancy_Wage_EstimateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Economic_Region_Vacancy_Wage_Estimate.objects.all()
    serializer_class = Economic_Region_Vacancy_Wage_EstimateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for NOC level records
class EconomicRegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EconomicRegion.objects.all()
    serializer_class = EconomicRegionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for NOC level records
class NOC_LevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NOC_Level.objects.all()
    serializer_class = NOC_LevelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for NOC grouping records 
class NOCGroupingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NOCGrouping.objects.all()
    serializer_class = NOCGroupingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for NOC class records
class NOCClassViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NOCClass.objects.all()
    serializer_class = NOCClassSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for program category records
class ProgramCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProgramCategory.objects.all()
    serializer_class = ProgramCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for program to NOC link records
class Program_NOC_LinkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Program_NOC_Link.objects.all()
    serializer_class = Program_NOC_LinkSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for program university KPI records 
class Program_University_KPIViewSet_Latest(viewsets.ReadOnlyModelViewSet):
    queryset = Program_University_KPI.objects.all()
    serializer_class = Program_University_KPISerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for province records
class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for provincial NOC group labour statistic records 
class Provincial_NOC_Group_Labor_StatisticViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Provincial_NOC_Group_Labor_Statistic.objects.all()
    serializer_class = Provincial_NOC_Group_Labor_StatisticSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# viewset for university records, supports filtering on all fields
class UniversityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

# full CRUD viewset for prediction cache records
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

# full CRUD viewset for seasonal decomposition records
class SeasonalDecompositionViewSet(viewsets.ModelViewSet):
    queryset = SeasonalDecomposition.objects.all()
    serializer_class = SeasonalDecompositionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

def Health_Check(request):
    """
    Returns: a JSON response with a simple ok status to confirm the Django API is alive
    Args:
        request: Request => the incoming GET request
    """
    return JsonResponse({"status": "ok"})