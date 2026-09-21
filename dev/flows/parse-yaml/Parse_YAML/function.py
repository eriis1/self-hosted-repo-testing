import pandas as pd
import yaml
from io import BytesIO

def execute(yaml_file: BytesIO, ganymede_context=None) -> pd.DataFrame:
    """
    Parses YAML file, returning contents as a Pandas DataFrame
    """
    operators = yaml.safe_load(yaml_file)
    df = pd.DataFrame(operators).T
    df.index.rename('class', inplace=True)
    return df.reset_index()
