from dataclasses import dataclass
from typing import Optional, List, Union, Dict
from io import BytesIO
import pandas as pd


@dataclass
class FlowInputFile:
    node_name: str
    param_name: str
    files: Dict[str, bytes]


@dataclass
class FlowInputParam:
    node_name: str
    param_name: str = "file_pattern"
    param_value: str


@dataclass
class Tag:
    node_name: str
    display_tag: str
    run_tag: str


class FlowInputs:
    files: Optional[List[FlowInputFile]]
    params: Optional[List[FlowInputParam]]
    tags: Optional[List[Tag]]

    def __init__(self, files=None, params=None, tags=None):
        """
        Representation of all inputs for a flow

        files: Optional[List[FlowInputFile]]
            list of files for flow
        params: Optional[List[FlowInputParam]]
            list of params for flow
        tags: Optional[List[Tag]]
            list of tags for flow
        """
        print("Did this change?");
        print(files)

        self.files = files if not files or isinstance(files, list) else [files]
        self.params = params if not params or isinstance(params, list) else [params]
        self.tags = tags if not tags or isinstance(tags, list) else [tags]

    def __repr__(self):
        if self.files:
            file_names = ""
            file_names += "\n".join(
                [
                    f"File name: { list(f.files.keys()) }; Node name: {f.node_name}; Param name: {f.param_name}"
                    for f in self.files
                ]
            )
        else:
            file_names = None

        if self.params:
            param_names = "\n".join(
                [
                    f"File name: {f.filename}; Node name: {f.node_name}; Param name: {f.param_name}"
                    for f in self.params
                ]
            )
        else:
            param_names = None

        if self.tags:
            tags = "\n".join(
                [
                    f"Node name: {f.node_name}; Display Tag: {f.display_tag}; Run Tag: {f.run_tag}"
                    for f in self.tags
                ]
            )
        else:
            tags = None

        return f"Files:\n{file_names}\n\nParams:\n{param_names}\n\nTags:\n{tags}"


def execute(
    df_sql_result: Union[pd.DataFrame, List[pd.DataFrame]], ganymede_context=None
) -> FlowInputs:
    """
    Calls Benchling to get data for flow to trigger

    Parameters
    ----------
    df_sql_result : Union[pd.DataFrame, List[pd.DataFrame]]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : Optional[GanymedeContext]
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    FlowInputs
        FlowInputs class for kicking off subsequent Flow
    """

    bio = BytesIO()
    table_out = df_sql_result[0] if isinstance(df_sql_result, list) else df_sql_result

    table_out.to_csv(bio)
    bio.seek(0)

    files_out = [
        FlowInputFile(
            node_name="CSV_Read",
            param_name="csv",
            files={"demo_file.csv": bio.read()},
        )
    ]

    # populate FlowInputs object based on event_data to return
    f = FlowInputs(files=files_out, params=None, tags=None)

    return f

