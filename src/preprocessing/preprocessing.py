import pandas as pd
import numpy as np
def remove_continuous_columns(df,maxValues):
    """
    Removes continuous columns from the dataframe, leaving only categorical columns with cardinality lower than a max value

    Args:
        df ([dataframe]): initial dataset read from csv file
        maxValues([int]): maximum cardinality of the categorical columns to be kept
        
    Returns:
        Array with 2 elements
            First element: subarray with deleted columns names
            Second element: Final dataframe with only categorical columns with cardinality lower than maxValues
    """
        
    #Remove columns with float type
    output = [[],[]]
    float_types = ['float16', 'float32', 'float64']
    df_with_floats = df.select_dtypes(include=float_types)
    df_without_floats = df.select_dtypes(exclude=float_types)
    df_with_floats_columns = list(df_with_floats.columns)
    #Add the remaining columns (non float) to the output
    output[0].extend(df_with_floats_columns)
    #Check the cardinality for each column
    for col in df_without_floats:
        cardinality = df_without_floats[col].nunique()
        #If cardinality is equal to the len of the dataset, it could be an index, so we remove it.
        if cardinality > maxValues:
            output[0].append(col)
            df_without_floats.drop(col, axis=1,inplace=True)
    # Add the filtered dataframe to the second subarray of the output
    output[1] = df_without_floats
    return output    
    
def impute_with_mode(df, empty_char = ""):
    """Inputes missing values with the mode of the column

    Args:
        df ([DataFrame]): initial dataset with categorical columns
        empty_char (str, optional): Value to be replaced with the mode. Defaults to "".

    Returns:
        [DataFrame]: Dataframe with imputed values
    """    
    #Replace missing values with the NaN value, which allows us to use the fillna function to replace them with the mode
    df.replace(empty_char, np.nan, inplace=True)
    # we iterate over every column
    for name, values in df.iteritems():
        df[name] = df[name].fillna(df[name].mode()[0])
    return df