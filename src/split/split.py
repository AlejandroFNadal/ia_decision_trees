import pandas as pd
def split_dataset(df, percentage,target):
    """Splits a dataset into train and test sets.

    Args:
        df (DataFrame): The dataset to split.
        percentage ([int]): The percentage of the dataset to use for training.

    Returns:
        [set]: Returns the train and test sets.
    """    
    df_train = df.sample(frac = percentage)
    df_test = df.drop(df_train.index)
    return (df_train, df_test)
