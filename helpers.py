import os
from typing import Literal

import pandas as pd
import requests

DATA_PATH="./data"

def transformLbmaData(data, fix_type):
    df = pd.DataFrame(data)
    df_transformed = pd.DataFrame({
        'date': pd.to_datetime(df['d']),
        f'{fix_type.lower()}_fix': df['v'].apply(lambda x: x[0])
    })
    return df_transformed


def loadLbmaData(metal: str) -> pd.DataFrame:

    am_data = requests.get(f"https://prices.lbma.org.uk/json/{metal}_am.json").json()
    pm_data = requests.get(f"https://prices.lbma.org.uk/json/{metal}_pm.json").json()

    am_df = transformLbmaData(am_data, 'AM')
    pm_df = transformLbmaData(pm_data, 'PM')
    combined_df = pd.merge(am_df, pm_df, on='date', how='inner').sort_values(by='date')
    combined_df.set_index('date', inplace=True)
    assert combined_df['am_fix'].notna().all(), "Some AM fixes are missing."
    assert combined_df['pm_fix'].notna().all(), "Some PM fixes are missing."
    return combined_df


def loadLbmaAmPMFixes(metal: Literal["gold", "palladium", "platinum"], cached=True) -> pd.DataFrame:
    filePath = os.path.join(DATA_PATH, f"lbma_{metal}_fixes.csv")
    if cached and os.path.exists(filePath):
        return pd.read_csv(filePath, parse_dates=['date'], index_col='date')
    data = loadLbmaData(metal)
    data.to_csv(filePath)
    return data
