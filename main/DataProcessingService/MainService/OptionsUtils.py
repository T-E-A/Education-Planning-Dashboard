from MainService import DataRequester as DataService
import inspect
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

#region [Defined Options]
# maps KPI metric IDs to their readable label for the latest year (2020)

Program_Post_Grad_Employment_Rate_Latest_Dict = {
    1: '2020 Employment Rate 6 Months after Graduation',
    2: '2020 Employment Rate 2 Years after Graduation',
    3: '2020 Graduation Rate',
}

# same as above but without the year prefix, used when pulling all years
Program_Post_Grad_Employment_Rate_All_Dict = {
    1: 'Employment Rate 6 Months after Graduation',
    2: 'Employment Rate 2 Years after Graduation',
    3: 'Graduation Rate',
}
#endregion 

#region [Auxilary Functions]
def Get_Program_Options():
    """
    Returns: a dict mapping program category IDs to their names, ex. {1: 'Engineering', 2: 'Business'}, empty dict on failure
    Args: none
    """
    method = inspect.currentframe().f_code.co_name
    try:
        df = DataService.RequestProgramCategories()
        # df = df.loc[df['programcategoryid'].isin([3,4])]

        print(f"Recieved Programs\n{df}")
        ProgramOptions = df.set_index('programcategoryid')['programcategory'].to_dict()
        return ProgramOptions
    except Exception as e:
        logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
        return {}

def Get_NOC_GroupOptions():
    """
    Returns: a dict mapping NOC grouping IDs to their names, ex. {1: 'Management', 2: 'Sciences'}, empty dict on failure
    Args: none
    """
    method = inspect.currentframe().f_code.co_name
    try:
        df = DataService.RequestNOCGroupingOptions()
        NOC_Grouping_Options = df.set_index('noc_groupingid')['noc_grouping'].to_dict()
        return NOC_Grouping_Options
    except Exception as e:
        logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
        return {}

def Get_Province_Options():
    """
    Returns: a dict mapping province IDs to their names, ex. {35: 'Ontario', 24: 'Quebec'}, empty dict on failure
    Args: none
    """
    method = inspect.currentframe().f_code.co_name
    try:
        df = DataService.RequestProvince()
        ProvinceOptions = df.set_index('provinceid')['province'].to_dict()
        return ProvinceOptions
    except Exception as e:
        logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
        return {}

def Get_Province_DGUID_Options():
    """
    Returns: a dict mapping province IDs to their DGUIDs, ex. {35: '2021A000235'}, empty dict on failure
    Args: none
    """
    method = inspect.currentframe().f_code.co_name
    try:
        df = DataService.RequestProvince()
        ProvinceOptions = df.set_index('provinceid')['province_dguid'].to_dict()
        return ProvinceOptions
    except Exception as e:
        logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
        return {}

def Get_University_Options():
    """
    Returns: a dict mapping university IDs to their names, ex. {1: 'University of Toronto'}, empty dict on failure
    Args: none
    """
    method = inspect.currentframe().f_code.co_name
    try:
        df = DataService.RequestUniversities()
        UniversityOptions = df.set_index('universityid')['university'].to_dict()
        return UniversityOptions

    except Exception as e:
        logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
        return {}
#endregion 

#region [Main Function]

def Get_All_Options_Dicts():
    """
    Returns: a dict with keys 'Programs', 'Universities', 'Provinces', 'Provinces_DGUID', and 'NOCGrouping', each containing their respective ID to name mappings, empty dict on failure
    Args: none
    """
    method = inspect.currentframe().f_code.co_name
    try:
        Options_Directory = {
            'Programs': {},
            'Universities': {},
            'Provinces': {},
            'Provinces_DGUID':{},
            'NOCGrouping': {}
        }

        # Map each key to its fetch function so we can run them all in parallel
        Directory_Threads = {
            'Programs': Get_Program_Options,
            'Universities': Get_University_Options,
            'Provinces': Get_Province_Options,
            'Provinces_DGUID': Get_Province_DGUID_Options,
            'NOCGrouping': Get_NOC_GroupOptions
        }

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            future_to_key = {
                executor.submit(func): key
                for key, func in Directory_Threads.items()
            }

            # Collect results as each one finishes
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    Options_Directory[key] = future.result()
                except Exception as e:
                    logging.getLogger(__name__).exception(
                        f"{method} => Error in {key} thread [{e}]"
                    )
                    Options_Directory[key] = {}

        return Options_Directory

    except Exception as e:
        logging.getLogger(__name__).exception(f'{method} => Error [{e}]')
        return {}
#endregion 
