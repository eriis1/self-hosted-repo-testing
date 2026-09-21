import pandas as pd
import re
from typing import Dict


def rename_column_for_bigquery(s: str):
    """
    Replaces column name for consumption by BigQuery
    """
    return re.sub(r"\W+", "_", s)


def parse_metadata(metadata: dict) -> dict:
    """
    Parses FCS file metadata

    Parameters
    ----------
    metadata : dict
        Metadata contained within FCS file, as parsed by the fcsparser python package

    Returns
    -------
    dict
        FCS metadata

    Notes
    -----
    FCS metadata is returned as a dictionary with the following components

    dict
        header: describes FCS version and byte offsets of TEXT, DATA, and ANALYSIS segments in FCS file
    dict
        system_metadata: contains system metadata as specified by the FCS file format
    pd.DataFrame
        channels: describes characteristics for each channel
    Tuple
        channel_names: contains flow cytometer channel names
    """

    header_dict = metadata["__header__"]

    for k in header_dict.keys():
        if isinstance(header_dict[k], bytes):
            header_dict[k] = header_dict[k].decode()
    header_dict = {rename_column_for_bigquery(k): v for k, v in header_dict.items()}

    sys_metadata_dict = {
        rename_column_for_bigquery(k): v
        for k, v in metadata.items()
        if k not in ["__header__", "_channels_", "_channel_names_"]
    }

    channels_df = metadata["_channels_"]
    channels_df.columns = [rename_column_for_bigquery(c) for c in channels_df.columns]
    channels_df.reset_index(inplace=True)

    channel_names = metadata["_channel_names_"]

    return {
        "header": header_dict,
        "system_metadata": sys_metadata_dict,
        "channels": channels_df,
        "channel_names": channel_names,
    }


def execute(
    metadata: Dict[str, pd.DataFrame], data: pd.DataFrame, ganymede_context=None
) -> Dict[str, pd.DataFrame]:
    """
    Process FCS data/metadata file

    Parameters
    ----------
    metadata : Dict[str, pd.DataFrame]
        Metadata from FCS file
    data : pd.DataFrame

    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    Dict[str, pd.DataFrame]
        Tables containing data and metadata parsed from FCS file
    """
    metadata_parsed = parse_metadata(metadata)
    metadata_file = pd.DataFrame.from_records(metadata_parsed["header"], index=[0])
    metadata_fcs = pd.DataFrame.from_records(metadata_parsed["system_metadata"], index=[0])
    channels = metadata_parsed["channels"]

    result = {
        "data": data,
        "metadata_file": metadata_file,
        "metadata_fcs": metadata_fcs,
        "metadata_channels": channels,
    }

    for k, df in result.items():
        result[k].columns = [rename_column_for_bigquery(c) for c in df.columns]

    data.columns = [rename_column_for_bigquery(c) for c in data.columns]

    return result
