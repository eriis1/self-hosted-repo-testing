import time
import ganymede_api
import pandas as pd
from ganymede_sdk import GanymedeContext, lib
from ganymede_sdk.editor import get_secret
from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import NodeReturn


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    lib_config = lib.config()

    api_key = get_secret("ganymede_api_key_e2e_flows")
    public_api_config = ganymede_api.Configuration(
        host="dev.ganymede.bio",
        api_key={"api-key": api_key},
    )
    public_api_client = ganymede_api.ApiClient(configuration=public_api_config)
    flows_api = ganymede_api.FlowsApi(api_client=public_api_client)

    call_count = 30
    for i in range(call_count):
        try:
            response = flows_api.get_flows(environment=lib_config.env)
            print(f"Call {i + 1}/{call_count}: retrieved {len(response)} flows")
            time.sleep(10)
        except ganymede_api.ApiException as e:
            raise GanymedeException(
                exception_type="Validation",
                message=f"getFlows API call failed on attempt {i + 1}/{call_count} with status {e.status}",
            )

    return NodeReturn()
