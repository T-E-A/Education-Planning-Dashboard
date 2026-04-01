import pandas as pd
import polars as pl
import threading
import os 
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

Uni_Fee_Path = Path(
    os.getenv(
        "UNI_FEE_PATH",
        (BASE_DIR.parent/ "Repository" / "DataFlatFiles"/ "Tbl_University_Fees.csv")
    )
)

Career_Pathway_Path = Path(
    os.getenv(
        "CAREER_PATHWAYS",
        (BASE_DIR.parent/ "Repository" / "DataFlatFiles"/ "Tbl_CareerPathways.parquet")
    )
)

Career_Options_Path = Path(
    os.getenv(
        "CAREER_OPTIONS_PATH",
        (BASE_DIR.parent/ "Repository" / "Options"/ "Career_Options.json")
    )
)

Major_Options_Path = Path(
    os.getenv(
        "MAJOR_OPTIONS_PATH",
        (BASE_DIR.parent/ "Repository" / "Options"/ "Major_Options.json")
    )
)

Forecast_Eval_Path = Path(
    os.getenv(
        "FORECAST_EVAL",
        (BASE_DIR.parent/ "Repository" / "DataFlatFiles"/ "Tbl_Forecast_Evaluation_Metrics.csv")
    )
)




dp_All_KPI_Frame = None
dp_Latest_KPI_Frame = None
Budget_Data_Cache = None

dp_Forecast_Cache = None
dp_YoY_Forecast_Cache = None


dp_Univeristy_Fees = pl.scan_csv(Uni_Fee_Path)
dp_Career_Pathways = pl.scan_parquet(Career_Pathway_Path)
dp_Forecast_Evals = pl.scan_csv(Forecast_Eval_Path)

dp_Career_Pathways = dp_Career_Pathways.filter(pl.col('HighestEducation').is_in(["Bachelor's degree", 
                                                                                 "Master's degree", "Earned doctorate"]))

dp_Career_Pathways_Sub_Select = None
dp_Career_Pathways_Second_Sub_Select = None

with open(Career_Options_Path, 'r') as f:
    Career_Options = json.load(f)

with open(Major_Options_Path, 'r') as f:
    Major_Options = json.load(f)


Cluster_Dict_Options = None
dp_All_Clusters_Seasonal_Decomp = None

# print(f"Checking University Feeds Load for path {Uni_Fee_Path} =>\n{dp_Univeristy_Fees.collect().head(10)}")

def Create_Frame(Data):
    try:
        dp = pl.DataFrame(Data)
        return dp
    except Exception as e:
        print(f"Create frame Excpetion [{e}]")


def Load_All_KPI_Frame(Data):
    try:
        global dp_All_KPI_Frame
        dp_All_KPI_Frame = Create_Frame(Data)

        # print(dp_All_KPI_Frame.schema)
        if dp_All_KPI_Frame is not None:
            print("KPI Frame loaded successfully")
        else:
            print("KPI Frame loading failed")
    except Exception as e:
        print(f"Load_KPI_Frame Exception: {e}")


def Offload_All_KPI_Frame():
    try:
        global dp_All_KPI_Frame
        dp_All_KPI_Frame = None
        print("KPI Frame offloaded")
    except Exception as e:
        print(f"Offload_KPI_Frame Exception: {e}")


def Load_Latest_KPI_Frame(Data):
    try:
        global dp_Latest_KPI_Frame
        dp_Latest_KPI_Frame = Create_Frame(Data)

        # print(dp_Latest_KPI_Frame.schema)
        if dp_Latest_KPI_Frame is not None:
            print("KPI Frame loaded successfully")
        else:
            print("KPI Frame loading failed")
    except Exception as e:
        print(f"Load_KPI_Frame Exception: {e}")


def Offload_Latest_KPI_Frame():
    try:
        global dp_Latest_KPI_Frame
        dp_Latest_KPI_Frame = None
        print("KPI Frame offloaded")
    except Exception as e:
        print(f"Offload_KPI_Frame Exception: {e}")


# Threaded function to load both KPI frames
def Load_Both_KPI_Frames(latest_data, all_data):
    threads = [
        threading.Thread(target=Load_Latest_KPI_Frame, args=(latest_data,)),
        threading.Thread(target=Load_All_KPI_Frame, args=(all_data,))
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Both KPI Frames loaded via threading")

# Threaded function to offload both KPI frames
def Offload_Both_KPI_Frames():
    threads = [
        threading.Thread(target=Offload_Latest_KPI_Frame),
        threading.Thread(target=Offload_All_KPI_Frame)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Both KPI Frames offloaded via threading")