import glob
import os
import re
from typing import Callable, Dict

from ganymede_sdk.agent.models import FileWatcherResult, TriggerFlowParams


def fp(watch_dir: str, parent_dir: str, pattern: str) -> Callable[[str], bool]:
    def fp_res(x: str):
        return x in glob.glob(os.path.join(watch_dir, pattern), recursive=True)

    return fp_res


# Required Function
# Must return a dictionary where key is the parameter
# and value is the lambda for files that match that parameter
def get_param_mapping(
    watch_dir: str,
    parent_dir: str = "",
    file_name: str = "",
    modified_time: str = "",
    body: bytes = bytes(),
) -> Dict[str, Callable[[str], bool]]:
    # Use regex to extract the word characters in the file name
    id_group = re.search(r"^(\w+)", file_name)
    if id_group == None:
        return {}
    id = id_group.group()
    return {
        "CSV_Read.csv": fp(watch_dir, parent_dir, f"*1.csv"),
        "CSV_Read1.csv": fp(watch_dir, parent_dir, f"*2.csv"),
    }


# Required Function
def execute(flow_params_fw: FileWatcherResult, **kwargs) -> TriggerFlowParams:
    # import tkinter as tk

    # def on_button_click():
    #     label.config(text="Hello World!")

    # root = tk.Tk()
    # root.title("Hello World!")

    # label = tk.Label(root, text="Hello World!")
    # label.pack()

    # button = tk.Button(root, text="Click Me!", command=on_button_click)
    # button.pack()

    # close_button = tk.Button(root, text="Close", command=root.destroy)
    # close_button.pack()

    # root.mainloop()

    return TriggerFlowParams(
        single_file_params=flow_params_fw.files,
        multi_file_params=None,
        benchling_tag=None,
        additional_params={},
    )