from ganymede_sdk.api.tempo.apprentice_tempo_sync import run_tempo_sync_all
from ganymede_sdk.io import NodeReturn


def execute(df_sql_result, ganymede_context) -> NodeReturn:
    return run_tempo_sync_all(ganymede_context)
