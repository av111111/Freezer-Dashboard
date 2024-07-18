import pandas as pd

def load_data():
    freezer_status_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTBqu3473l0OMMlicoERthxkIYTneF9fh9jy958Q0zAb5NwVCeSDsIYUsxpnBzgl4rDoMJ7P7E1W2lM/pubhtml?gid=0&single=true"
    freezer_database_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSgeAPBmFPRxaRHnoHLG7Xt5wT_gr5A0gkgfgjiT1mLFBPgQsXFa2k9wriUvZtkl1_DB7fcrTnV0DUj/pubhtml?gid=0&single=true"

    freezer_status = pd.read_html(freezer_status_url)[0]
    freezer_database = pd.read_html(freezer_database_url)[0]

    freezer_status.columns = freezer_status.iloc[0]
    freezer_status = freezer_status.drop(freezer_status.index[0])

    freezer_database.columns = freezer_database.iloc[0]
    freezer_database = freezer_database.drop(freezer_database.index[0])

    freezer_status = freezer_status.reset_index(drop=True)
    freezer_database = freezer_database.reset_index(drop=True)

    return freezer_status, freezer_database
