import pandas as pd
from io import BytesIO
from typing import Union, Dict
from ganymede_sdk.analytics import parse_fcs


def execute(
    fcs_file: Dict[str, BytesIO], ganymede_context=None
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    fcs_file_bytes = list(fcs_file.values()).pop().read()
    fcs_object = parse_fcs(fcs_file_bytes)

    print("a")
    return fcs_object.data