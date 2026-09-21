import glob
import io
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union, Tuple
from urllib import parse
import json

from ganymede_sdk.agent.models import (
    FileParam,
    FileWatcherResult,
    MultiFileParam,
    TriggerFlowParams,
)

SOURCE_BARCODE_COLUMN = "SRackBC"
TARGET_BARCODE_COLUMN = "TRackBC"

def fp(
    watch_dir: str, parent_dir: str, barcode: str, parent_dir_match: str
) -> Callable[[str], bool]:
    """
    This function returns a function that performs pattern matching against a file path.
    Use this function as a template for creating your own pattern matching functions, which
    you can then use in the values of the return object in the get_param_mapping function.

    Returns
    -------
    Callable[[str], bool]
        Function that takes a file as input and returns True if the file matches the pattern.
    """

    def fp_res(x: str):
        # parent_dir:  Mapping Files\Linearization
        parent_dir_file = x.split(os.sep)[-2]
        print("parent_dir:", parent_dir)
        print("parent_dir_file:", parent_dir_file)
        print("parent_dir_match:", parent_dir_match)
        if parent_dir_file != parent_dir.split(os.sep)[-1]:
            print(
                "PROBLEM++++++++++++++++++++++++++++PROBLEM++++++++++++++++++++++++++++++PROBLEM+++++++++++++++++++++++++++++"
            )
        if parent_dir_file == parent_dir_match:
            x = parse.unquote(x)
            matches_barcode = barcode in Path(x).stem
            print(
                f"Found {parent_dir_match} file {x}, with barcode {barcode}, checking if barcode is in {Path(x).stem}: {matches_barcode} "
            )
            if parent_dir_match == "Stunner Output":
                return matches_barcode and "Quant_DNA" in Path(x).stem
            else:
                return matches_barcode
        else:
            return False

    return fp_res


# Required Function
def get_param_mapping(
    watch_dir: str,
    parent_dir: str = "",
    file_name: str = "",
    modified_time: str = "",
    body: bytes = bytes(),
) -> Dict[str, Union[Callable[[str], bool], List[Callable[[str], bool]]]]:
    """
    This function is called when a file is added or modified in the watch directory.
    Modify this function to capture the files you want to trigger the flow;
    the function should return a dictionary where the keys are <node name>.<param name>
    and values are functions for performing pattern matching against the target file.

    For nodes that accept multiple inputs, specify a list of functions to match against;
    each specified function should uniquely match 1 file.
    """

    def get_or_update_barcode_mapping(
        barcode1: str, stage_key1: str, barcode2: str, stage_key2: str
    ) -> Optional[dict]:
        for json_filename in glob.glob("*_tracking.json"):
            with open(json_filename, "w+") as f:
                mapping = json.loads(f.read())
                if barcodes_complete(mapping):
                    return mapping
                if mapping[stage_key1] == barcode1:
                    # update the tracking json file
                    mapping[stage_key2] = barcode2
                    f.write(mapping)
                    return None
                if mapping[stage_key2] == barcode2:
                    # update the tracking json file
                    mapping[stage_key1] = barcode1
                    f.write(mapping)
                    return None

    def barcodes_complete(mapping: dict) -> bool:
        print("mapping json:", mapping)
        return "lin_cleanup2" in mapping and "leftover3" in mapping and "stunner4" in mapping
    

    def get_barcodes_from_mapping_file(file: bytes) -> Tuple[str, str]:
        mapping_df = pd.read_excel(io.BytesIO(file))
        source_barcode = mapping_df[SOURCE_BARCODE_COLUMN].values[0]
        target_barcode = mapping_df[TARGET_BARCODE_COLUMN].values[0]
        return source_barcode, target_barcode

    complete_json = None
    sub_parent_dir = parent_dir.split(os.sep)[-1]

    if file_name.endswith(".xls"):
        source_barcode, target_barcode = get_barcodes_from_mapping_file(body)
        if sub_parent_dir == "Lin":
            json_filename = f"{source_barcode}_tracking.json"
            # TODO: change to LAST barcode for easier finding in next method
            if not os.path.exists(json_filename):
                with open(json_filename, "w+") as f:
                    barcode_map = {
                        "benchling1": source_barcode,
                        "lin_cleanup2": target_barcode,
                    }
                    barcode_map_str = json.dumps(barcode_map)
                    f.write(barcode_map_str)
            else:
                with open(json_filename, "w+") as f:
                    mapping = json.loads(f.read())
                    if not barcodes_complete(mapping):
                        if mapping["lin_cleanup2"] == target_barcode:
                            # update the tracking json file
                            mapping["benchling_barcode1"] = source_barcode
                            f.write(mapping)
                    else:
                        complete_json = mapping
        elif sub_parent_dir == "Lin Clean":
            complete_json = get_or_update_barcode_mapping(
                source_barcode, "lin_cleanup2", target_barcode, "leftover3"
            )
        elif sub_parent_dir == "Stunner Stamp":
            complete_json = get_or_update_barcode_mapping(source_barcode, "leftover3", target_barcode, "stunner4")
        else:
            return {}
    elif file_name.endswith(".csv"):
        
       
    if complete_json:
        return {
            "Linearization_Mapping.file_pattern": fp(
                watch_dir, parent_dir, f"{complete_json['lin_cleanup2']}", "Linearization"
            ),
            # parent_dir:  Mapping Files\Linearization Cleanup
            "Linearization_Cleanup_Mapping.file_pattern": fp(
                watch_dir, parent_dir, f"{complete_json['leftover3']}", "Linearization Cleanup"
            ),
            # parent_dir:  Mapping Files\DNA Stamp
            "Stunner_DNA_Stamp_Mapping.file_pattern": fp(
                watch_dir, parent_dir, f"{complete_json['stunner4']}", "DNA Stamp"
            ),
            # parent_dir:  Stunner Output, DNA
            "Stunner_DNA_Results.file_pattern": fp(
                watch_dir, parent_dir, f"{complete_json['stunner4']}", "Stunner Output"
            ),
        }
    else:
        return {
            # Hack to always match the file, but always have an incomplete matching group
            # this way the file will be held until the tracking json file is complete
            "wait.hold": lambda x: True,
            "hold.hold": lambda x: False,
        }


def execute(flow_params_fw: FileWatcherResult, **kwargs) -> TriggerFlowParams:  # type: ignore
    """
    Called when all glob patterns specified by get_param_mapping have been matched.

    Parameters
    ----------
    flow_params_fw : FileWatcherResult
        Dict of FileParam objects indexed by <node name>.<param name>
    """
    m = MultiFileParam.from_file_param(list(flow_params_fw.files.values()))
    m.param = "Input_File.file_pattern"

    return TriggerFlowParams(
        # single_file_params=flow_params_fw.files,
        single_file_params=None,
        multi_file_params={"fix.fix": m},  # the key is not used later, shoud be removed
        benchling_tag=None,
        additional_params={},
    )
