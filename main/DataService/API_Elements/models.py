# By: Tejas Kumar
# This is an auto-generated Django model module.
# Models were dynamically created by Django Framework based on the table names and schema. 

from django.db import models

#region Time Series Data 

# Economic Region Employment Estimates Per NOC Classes -- Time Series

class Economic_Region_Employment_Estimate(models.Model):
    datestamp = models.TextField(blank=True, null=True)  # This field type is a guess.
    dguid = models.TextField(db_column='DGUID', blank=True, null=True)  # Field name made lowercase.
    noc_groupingid = models.IntegerField(db_column='NOC_GroupingID', blank=True, null=True)  # Field name made lowercase.
    employment_estimate_3_month_moving_average = models.FloatField(db_column='Employment Estimate 3 Month Moving Average', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    month = models.IntegerField(db_column='Month', blank=True, null=True)  # Field name made lowercase.
    employment_pct_change = models.FloatField(db_column='Employment PCT Change', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    entryid = models.IntegerField(db_column='EntryID', blank=False, null=False, primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_Economic_Region_NOC_Employment_Estimate_TS'

# Economic Region Job Vacancies and Wage Estimates Per NOC Classes -- Time Series

class Economic_Region_Vacancy_Wage_Estimate(models.Model):
    datestamp = models.TextField(blank=True, null=True)
    dguid = models.TextField(db_column='DGUID', blank=True, null=True)  # Field name made lowercase.
    noc_code = models.TextField(db_column='NOC Code', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    average_offered_hourly_wage = models.FloatField(db_column='Average offered hourly wage', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    job_vacancies = models.FloatField(db_column='Job vacancies', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    classid = models.IntegerField(db_column='ClassID', blank=True, null=True)  # Field name made lowercase.
    entryid = models.IntegerField(db_column='EntryID', blank=False, null=False, primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_Economic_Region_NOC_Vacancy_And_Wage_Estimate_TS'

# Provincial Labor Market Statistics Per NOC Classes -- Time Series

class Provincial_NOC_Group_Labor_Statistic(models.Model):
    datestamp = models.TextField(blank=True, null=True)  # This field type is a guess.
    noc_groupingid = models.IntegerField(db_column='NOC_GroupingID', blank=True, null=True)  # Field name made lowercase.
    noc_grouping = models.TextField(db_column='NOC_Grouping', blank=True, null=True)  # Field name made lowercase.
    dguid = models.TextField(db_column='DGUID', blank=True, null=True)  # Field name made lowercase.
    labour_force = models.FloatField(db_column='Labour force', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    employment = models.FloatField(db_column='Employment', blank=True, null=True)  # Field name made lowercase.
    part_time_employment = models.FloatField(db_column='Part-time employment', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    full_time_employment = models.FloatField(db_column='Full-time employment', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    unemployment = models.FloatField(db_column='Unemployment', blank=True, null=True)  # Field name made lowercase.
    unemployment_rate = models.FloatField(db_column='Unemployment rate', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    employment_moving_average = models.FloatField(db_column='Employment Moving Average', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    employment_moving_sd = models.FloatField(db_column='Employment Moving SD', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    employment_upper_band = models.FloatField(db_column='Employment Upper Band', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    employment_lower_band = models.FloatField(db_column='Employment Lower Band', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    entryid = models.IntegerField(db_column='EntryID', blank=False, null=False, primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_Provincial_NOC_Labor_Statistics'
#endregion 


# region [Stats Canada Location Entities]

# Canadian Province Entity 

class Province(models.Model):
    provinceid = models.IntegerField(db_column='ProvinceID', blank=False, null=False, primary_key=True)  # Field name made lowercase.
    province_dguid = models.TextField(db_column='Province_DGUID', blank=True, null=True)  # Field name made lowercase.
    province = models.TextField(db_column='Province', blank=True, null=True)  # Field name made lowercase.
    province_shorthand = models.TextField(db_column='Province_Shorthand', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_Provinces'

# Economic Region Entity

class EconomicRegion(models.Model):
    economicregionid = models.IntegerField(db_column='EconomicRegionID', blank=False, null=False, primary_key=True)  # Field name made lowercase.
    economicregion_dguid = models.TextField(db_column='EconomicRegion_DGUID', blank=True, null=True)  # Field name made lowercase.
    economicregion = models.TextField(db_column='EconomicRegion', blank=True, null=True)  # Field name made lowercase.
    provinceid = models.IntegerField(db_column='ProvinceID', blank=True, null=True)  # Field name made lowercase.
    province_dguid = models.TextField(db_column='Province_DGUID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_Economic_Regions'

# NOC Hierarchy Level Identifiers

class NOC_Level(models.Model):
    levelid = models.IntegerField(db_column='LevelID', blank=True, null=True)  # Field name made lowercase.
    levelname = models.TextField(db_column='LevelName', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_NOC_Levels'

# NOC Grouping Entity used for time series analysis

class NOCGrouping(models.Model):
    noc_groupingid = models.IntegerField(db_column='NOC_GroupingID', blank=False, null=False, primary_key=True)  # Field name made lowercase.
    noc_grouping = models.TextField(db_column='NOC_Grouping', blank=True, null=True)  # Field name made lowercase.
    unnamed_2 = models.FloatField(db_column='Unnamed: 2', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'Tbl_NOC_TS_Groupings'

# specific NOC Occupation Class Entity 

class NOCClass(models.Model):
    classid = models.IntegerField(db_column='ClassID', blank=False, null=False, primary_key=True)  # Field name made lowercase.
    levelid = models.IntegerField(db_column='LevelID', blank=True, null=True)  # Field name made lowercase.
    noc_code = models.IntegerField(db_column='NOC Code', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    noc_class = models.TextField(db_column='NOC Class', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    class_definition = models.TextField(db_column='Class Definition', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'Tbl_Occupations'

# Canadian University Entity with location data

class University(models.Model):
    universityid = models.IntegerField(db_column='UniversityID', blank=False, null=False, primary_key=True)  # Field name made lowercase.
    university = models.TextField(db_column='University', blank=True, null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address', blank=True, null=True)  # Field name made lowercase.
    province = models.TextField(db_column='Province', blank=True, null=True)  # Field name made lowercase.
    city = models.TextField(db_column='City', blank=True, null=True)  # Field name made lowercase.
    postalcode = models.TextField(db_column='PostalCode', blank=True, null=True)  # Field name made lowercase.
    lat = models.FloatField(db_column='Lat', blank=True, null=True)  # Field name made lowercase.
    lon = models.FloatField(db_column='Lon', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_Universities'

# Program Category Entity, ex: Engineering, Business

class ProgramCategory(models.Model):
    programcategoryid = models.IntegerField(db_column='ProgramCategoryID', blank=False, null=False, primary_key=True)  # Field name made lowercase.
    programcategory = models.TextField(db_column='ProgramCategory', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_ProgramCategories'
# endregion

# Region [Program-NOC Linkings and University-Program KPI Entities]

# Program-NOC Link Entity; links a program to its related NOC Occupation pathways

class Program_NOC_Link(models.Model):
    linkid = models.IntegerField(db_column='LinkID', blank=False, null=False, primary_key=True)  # Field name made lowercase.
    programid = models.IntegerField(db_column='ProgramID', blank=True, null=True)  # Field name made lowercase.
    program = models.TextField(db_column='Program', blank=True, null=True)  # Field name made lowercase.
    broad_occupation_category_code = models.IntegerField(db_column='Broad Occupation Category Code', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    broad_occupation_category = models.TextField(db_column='Broad Occupation Category', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    major_group_code = models.IntegerField(db_column='Major Group Code', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    major_group = models.TextField(db_column='Major Group', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    sub_major_group_code = models.IntegerField(db_column='Sub-Major Group Code', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    sub_major_group = models.TextField(db_column='Sub-Major Group', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    minor_group_code = models.IntegerField(db_column='Minor Group Code', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    minor_group = models.TextField(db_column='Minor Group', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    unit_group_code = models.IntegerField(db_column='Unit Group Code', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    unit_group_occupation = models.TextField(db_column='Unit Group Occupation', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    unit_group_description = models.TextField(db_column='Unit Group Description', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'Tbl_ProgramOccupations'

# Program University KPI Entity ; KPI metrics for a program at a specific university per year

class Program_University_KPI(models.Model):
    entryid = models.IntegerField(db_column='EntryID', blank=False, null=False, primary_key=True)  # Field name made lowercase.
    universityid = models.IntegerField(db_column='UniversityID', blank=True, null=True)  # Field name made lowercase.
    university = models.TextField(db_column='University', blank=True, null=True)  # Field name made lowercase.
    programcategoryid = models.IntegerField(db_column='ProgramCategoryID', blank=True, null=True)  # Field name made lowercase.
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    employment_rate_2_years_after_graduating_field = models.TextField(db_column='Employment Rate (2 years after graduating)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    employment_rate_6_months_after_graduating_field = models.TextField(db_column='Employment Rate (6 months after graduating)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    graduation_rate = models.TextField(db_column='Graduation Rate', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'Tbl_ProgramUniversityKPI'
# endregion 

# Caching prediction model results to avoid rerunning the prediction model every time

class PredictionCache(models.Model):
    entryid = models.IntegerField(db_column='EntryID', blank=False, null=False, primary_key=True)
    datestamp = models.TextField(db_column='ds',blank=True, null=True)
    provinceid = models.IntegerField(db_column='ProvinceID', blank=True, null=True)
    dguid = models.TextField(db_column='dguid', blank=True, null=True)
    noc_groupingid = models.IntegerField(db_column='noc_groupingid', blank=True, null=True)
    y = models.FloatField(db_column='y', blank=True, null=True)
    yhat_lower = models.FloatField(db_column='yhat_lower', blank=True, null=True)
    yhat = models.FloatField(db_column='yhat', blank=True, null=True)
    yhat_upper = models.FloatField(db_column='yhat_upper', blank=True, null=True)
    set = models.TextField(db_column='Set', blank=True, null=True)

    class Meta:
        db_table = 'Tbl_Temp_Forecasts'


# Region [Seasonal Decomposed Provinical Data]

# Seasonal decomposition data for a NOC group in a province, includes trend clustering
class SeasonalDecomposition(models.Model):
    entryid = models.IntegerField(db_column='entryID', blank=False, null=False, primary_key=True)
    datestamp = models.TextField(db_column='ds',blank=True, null=True)
    provinceid = models.IntegerField(db_column='provinceID', blank=True, null=True)
    province = models.TextField(db_column='province', blank=True, null=True)  # Field name made lowercase.
    trend_cluster = models.IntegerField(db_column='Trend Cluster', blank=True, null=True)
    noc_groupingid = models.IntegerField(db_column='noc_groupingid', blank=True, null=True)
    noc_grouping = models.TextField(db_column='noc_grouping', blank=True, null=True)
    observed = models.FloatField(db_column='observed', blank=True, null=True)
    trend = models.FloatField(db_column='trend', blank=True, null=True)
    resid = models.FloatField(db_column='resid', blank=True, null=True)
    seasonal_3 = models.FloatField(db_column='seasonal_3', blank=True, null=True)
    seasonal_6 = models.FloatField(db_column='seasonal_6', blank=True, null=True)
    seasonal_12 = models.FloatField(db_column='seasonal_12', blank=True, null=True)

    class Meta:
        db_table= 'Tbl_Seasonal_Decomposition'
#endregion 

