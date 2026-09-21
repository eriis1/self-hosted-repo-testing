"""

TODO and AIs:
- Can make the file pattern selectable if we support other "querying"/parsing
    - XML could accept XPath instead of col number


"""

from urllib import parse

import agent.logger as agent_logger
from agent_sdk import TriggerFlowParams
import agent_sdk
from agent_sdk.files import (
    MetadataFileManager,
    find_matching_flow_param,
    handle_metadata_file,
    handle_data_file,
)
from event_listeners.file_watcher import FileEvent

# These should be converted to configuration options:
filename_col = 2
well_metadata_param_key = "CSV_Read.csv"
well_metadata_file_pattern = "*.csv"  # Must be CSV but can have other filtering
fcs_files_param_key = "Ingest_Inst_Data.file_pattern"
fcs_files_file_pattern = "*.fcs"  # Can this be locked?


mgr = MetadataFileManager(filename_col)

# keys are the <node name>.<param name> to match against
# values are the regex patterns to match against
patterns_expected = {
    well_metadata_param_key: well_metadata_file_pattern,
    fcs_files_param_key: fcs_files_file_pattern,
}


# user-defined function to map files to flow parameters
def execute(new_event: FileEvent) -> TriggerFlowParams | None:
    agent_logger.debug(f"starting execute {new_event}")

    file_current = new_event.new_file
    watch_dir = new_event.input_dir

    # Escape paths for spaces and punctuation
    file_detected_sanitized = parse.unquote(str(file_current.file_path))
    matched_flow_param = find_matching_flow_param(
        watched_dir=watch_dir,
        file_detected_sanitized=file_detected_sanitized,
        patterns_available=patterns_expected,
    )

    if matched_flow_param is None:
        agent_logger.debug(f"There was no param that matched {file_detected_sanitized}")
        return None

    correct_group = None
    if matched_flow_param is well_metadata_param_key:
        correct_group = handle_metadata_file(mgr, file_current)
    else:
        correct_group = handle_data_file(mgr, file_current)

    ready_for_execution = len(correct_group.files_to_find) == 0
    if not ready_for_execution:
        return None

    tp = TriggerFlowParams()
    tp.add_file_param(param_node_key=well_metadata_param_key, file=correct_group.metadata_file)
    tp.add_file_param(param_node_key=fcs_files_param_key, files=correct_group.files_to_find)
    return tp

