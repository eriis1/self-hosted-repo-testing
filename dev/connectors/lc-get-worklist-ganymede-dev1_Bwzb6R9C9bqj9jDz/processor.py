from ganymede_sdk.agent.models import FileParam
import pandas as pd
from io import BytesIO
from pathlib import Path
import os


def write_file_locally(fn: str, body: bytes):
    PATH = Path(
        'C:/Users/LabStation/Umoja Biopharma/Product Development - LC/PEI')
    subdir = fn.split('.')[0]
    full_subdir = PATH / subdir
    if not os.path.exists(full_subdir):
        os.makedirs(full_subdir)
    full_path = full_subdir / fn
    with full_path.open('wb') as fp:
        fp.write(body)
        print(f'wrote worklist file {fp} locally')
    return


def execute(new_file: FileParam, **kwargs) ->None:
    print('new_file.filename: ', new_file.filename)
    split = new_file.filename.split('/')
    if len(split) != 2:
        return
    flow = split[0]
    if flow != 'LC-test-luke':
        return
    filename = split[1]
    write_file_locally(filename, new_file.body)
