import pandas as pd
import numpy as np
def remove_continuous_columns(df):
    """
    Removes continuous columns from the dataframe, leaving only categorical columns with low cardinality

    Args:
        df ([dataframe]): initial dataset read from csv file
        
    Returns:
        Array with 2 elements
            First element: subarray with deleted columns names
            Second element: Final dataframe with only categorical columns with low cardinality
    """
        
    #Remove columns with float type
    output = [[],[]]
    float_types = ['float16', 'float32', 'float64']
    df_with_floats = df.select_dtypes(include=float_types)
    df_without_floats = df.select_dtypes(exclude=float_types)
    df_with_floats_columns = list(df_with_floats.columns)
    output[0].extend(df_with_floats_columns)
    for col in df_without_floats:
        cardinality = df_without_floats[col].nunique()
        if cardinality > 27:
            output[0].append(col)
            df_without_floats.drop(col, axis=1,inplace=True)
    output[1] = df_without_floats
    return output    
    
def impute_with_mode(df, empty_char = ""):
    df.replace(empty_char, np.nan, inplace=True)
    # we iterate over every column
    for name, values in df.iteritems():
        df[name] = df[name].fillna(df[name].mode()[0])
    return df