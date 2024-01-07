import pandas as pd

def get_logins(path: str) -> list[str]:
    """Get logins from csv file

    Args:
        path (str): path to csv file

    Returns:
        list[str]: list of logins
    """
    return list(pd.read_csv(path)["login"])
