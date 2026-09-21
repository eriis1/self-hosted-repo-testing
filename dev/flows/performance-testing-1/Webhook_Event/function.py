import copy
from io import BytesIO
import api_server
import pandas as pd
from ganymede_sdk import Ganymede, GanymedeContext

# from ganymede_sdk.flow_runtime import GanymedeException
from ganymede_sdk.io import NodeReturn
from openapi_client.models.run_conf import RunConf
from openapi_client.models.run_conf_initiator import RunConfInitiator
from openapi_client.models.run_conf_params import RunConfParams
from openapi_client.models.initiator_types import InitiatorTypes
from ganymede_sdk import lib

def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    df_sql_result = copy.deepcopy(df_sql_result)

    # Example of how to use the Ganymede object to retrieve files and tables
    g = Ganymede(ganymede_context)

    initiator = RunConfInitiator(
                    initiator_type=InitiatorTypes.FLOW, initiator_id='performance-testing-1'
                )
    run_conf = RunConf(
        run_tag=None,
        display_tag=None,
        run_id=g.flow_run_id,
        initiator=initiator,
    )

    
    api_requests = api_server.ApiServerRequests(lib.config())
    api_requests.trigger_flow_run('performance-testing', run_conf)

    return NodeReturn()
