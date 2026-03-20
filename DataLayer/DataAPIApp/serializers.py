#By: Tejas Kumar
#This module helps serialize the classes for data transportation.
#Each serilization class inherits from 'ModelSerializer' and 'Meta' allows us to indicate which model is being serialized.  

from rest_framework import serializers
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

#region Serializers 
class Economic_Region_Employment_EstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Economic_Region_Employment_Estimate
        fields = '__all__'


class Economic_Region_Vacancy_Wage_EstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Economic_Region_Vacancy_Wage_Estimate
        fields = '__all__'


class EconomicRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicRegion
        fields = '__all__'


class NOC_LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NOC_Level
        fields = '__all__'


class NOCGroupingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NOCGrouping
        fields = '__all__'


class NOCClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = NOCClass
        fields = '__all__'


class ProgramCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramCategory
        fields = '__all__'


class Program_NOC_LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program_NOC_Link
        fields = '__all__'


class Program_University_KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Program_University_KPI
        fields = '__all__'


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'


class Provincial_NOC_Group_Labor_StatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincial_NOC_Group_Labor_Statistic
        fields = '__all__'


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'

class PredictionCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionCache
        fields = '__all__'

class SeasonalDecompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeasonalDecomposition
        fields = '__all__'
#endregion 