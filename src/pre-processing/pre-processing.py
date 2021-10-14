import pandas as pd
import numpy as np
def imputation_mode(df, empty_char = ""):
    df.replace(empty_char, np.nan, inplace=True)
    # we iterate over every column
    for name, values in df.iteritems():
        df[name] = df[name].fillna(df[name].mode()[0])
    return df