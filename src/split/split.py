import pandas as pd
def split_dataset(df, percentage):
    df_train = df.sample(frac = percentage)
    df_test = df.drop(df_train.index)
    return (df_train, df_test)
