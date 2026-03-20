#By: Tejas Kumar
#This module allows us to declare and regist the the routs for each view
#After writing this module, we register this a entrypoint in the urls.py inside of the DataLayer folder. 

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    Economic_Region_Employment_EstimateViewSet,
    Economic_Region_Vacancy_Wage_EstimateViewSet,
    EconomicRegionViewSet,
    NOC_LevelViewSet,
    NOCGroupingViewSet,
    NOCClassViewSet,
    ProgramCategoryViewSet,
    Program_NOC_LinkViewSet,
    Program_University_KPIViewSet_Latest,
    ProvinceViewSet,
    Provincial_NOC_Group_Labor_StatisticViewSet,
    UniversityViewSet,
    PredictionCacheViewSet,
    SeasonalDecompositionViewSet
)


router = DefaultRouter()
router.register(r'economic_region_employment_estimate', Economic_Region_Employment_EstimateViewSet, basename='economic_region_employment_estimate')
router.register(r'economic_region_vacancy_wage_estimate', Economic_Region_Vacancy_Wage_EstimateViewSet, basename='economic_region_vacancy_wage_estimate')
router.register(r'economicregion', EconomicRegionViewSet, basename='economicregion')
router.register(r'noc_level', NOC_LevelViewSet, basename='noc_level')
router.register(r'noc_grouping', NOCGroupingViewSet, basename='noc_grouping')
router.register(r'noc_class', NOCClassViewSet, basename='noc_class')
router.register(r'program_category', ProgramCategoryViewSet, basename='program_category')
router.register(r'program_noc_link', Program_NOC_LinkViewSet, basename='program_noc_link')
router.register(r'program_university_kpi_latest', Program_University_KPIViewSet_Latest, basename='program_university_kpi_latest')
router.register(r'province', ProvinceViewSet, basename='province')
router.register(r'provincial_noc_group_labor_statistic', Provincial_NOC_Group_Labor_StatisticViewSet, basename='provincial_noc_group_labor_statistic')
router.register(r'university', UniversityViewSet, basename='university')
router.register(r'prediction_cache', PredictionCacheViewSet, basename='prediction_cache')
router.register(r'seasonal_decomposition', SeasonalDecompositionViewSet, basename='seasonal_decomposition')

urlpatterns = [
    path('api/', include(router.urls)),
]
