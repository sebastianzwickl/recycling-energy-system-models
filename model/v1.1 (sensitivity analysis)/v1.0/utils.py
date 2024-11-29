import pandas as pd

def get_input_data_from_excel_sheets(name=None):
    _to_return = []
    for item in name:
        _get = pd.read_excel('input data/' + item)
        _to_return.append(_get)
    return _to_return


def fetch_data(_dict=None, data=None, choice=None, column=str):
    for  _index, _row in data.iterrows():
        if _row.Technology == choice:
            _dict[choice, _row.Year] = _row[column]
        else:
            pass
    return