import copy
from io import BytesIO

import pandas as pd
from ganymede_sdk import GanymedeContext
from ganymede_sdk import get_secret
from ganymede_sdk.io import NodeReturn
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from ganymede_sdk.flow_runtime import GanymedeException
from datetime import datetime


def create_message(
    color,
    flow_name,
    state,
    state_emoji,
    username,
    start_time,
    flow_run_url,
    end_time=None,
    errors=[],
):

    message = {
        "attachments": [
            {
                "color": color,
                "blocks": [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Flow:*\n{flow_name}"},
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*State:*\n{state_emoji} {state}"},
                            {"type": "mrkdwn", "text": f"*Run By:*\n{username}"},
                            {"type": "mrkdwn", "text": f"*Started:*\n {start_time}"},
                            {"type": "mrkdwn", "text": f"*Ended:*\n{end_time}"},
                        ],
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"<{flow_run_url}|View Flow>"},
                    },
                ],
            }
        ]
    }

    if len(errors) > 0:
        error_message = "\n".join(errors)
        users_to_notify = ["U05PWRF8EPR", "U06FT7GB154"]
        message["attachments"][0]["blocks"].append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<@{users_to_notify[0]}> <@{users_to_notify[1]}> Following errors were found ```{error_message}```",
                },
            }
        )

    else:
        message["attachments"][0]["blocks"].append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Trigger next flow"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Trigger Flow", "emoji": True},
                    "value": "{'test':'1'}",
                    "action_id": "button-action",
                    "url": "https://beb1-12-15-124-177.ngrok-free.app/",
                },
            }
        )

    return message


def execute(
    df_sql_result: pd.DataFrame | list[pd.DataFrame], ganymede_context: GanymedeContext
) -> NodeReturn:
    """
    Process tabular data from user-defined SQL query, writing results back to data lake.  Data
    is written to the output bucket.

    Parameters
    ----------
    df_sql_result : pd.DataFrame | list[pd.DataFrame]
        Table(s) or list of tables retrieved from user-defined SQL query
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.  NodeReturn object takes
        2 parameters:
        - tables_to_upload: dict[str, pd.DataFrame]
            keys are table names, values are pandas DataFrames to upload
        - files_to_upload: dict[str, bytes]
            keys are file names, values are file data to upload

    Notes
    -----
    Files can also be retrieved and processed using the list_files and retrieve_files functions.
    Documentation on these functions can be found at https://docs.ganymede.bio/sdk/GanymedeClass
    """
    df_sql_result = copy.deepcopy(df_sql_result)
    print(df_sql_result)

    df_data, slack_message_timestamps = df_sql_result

    slack_token = get_secret("test_slack_integration_token")
    client = WebClient(token=slack_token)
    errors = []

    too_low = df_data[df_data["value"] < 100]
    if not too_low.empty:
        errors.append(
            f"Value was below range for timestamp(s) {','.join(too_low['timestamp'].values)}"
        )

    too_high = df_data[df_data["value"] > 110]
    if not too_high.empty:
        errors.append(
            f"Value was above range for timestamp(s) {','.join(too_high['timestamp'].values)}"
        )

    previous_message_ts = slack_message_timestamps.loc[0]["timestamp"]

    start_time = datetime.fromtimestamp(int(ganymede_context.flow_run_id) / 1000)

    url = "https://admin.dev.ganymede.bio/ganymede-dev-multi/flows/slack-test/runs"

    if len(errors) > 0:
        message = create_message(
            "#e74c3c",
            ganymede_context["dag"]["dag_id"],
            ":x:",
            "Failed",
            ganymede_context["inputs"]["initiator"]["initiatorId"],
            start_time,
            url,
            end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            errors=errors,
        )

    else:
        message = create_message(
            "#2ecc71",
            ganymede_context["dag"]["dag_id"],
            ":white_check_mark:",
            "Success",
            ganymede_context["inputs"]["initiator"]["initiatorId"],
            start_time,
            url,
            end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            errors=errors,
        )

    try:
        response = client.chat_update(
            channel="C085GEWGJJ2", ts=previous_message_ts, attachments=message["attachments"]
        )
        print(response)
    except SlackApiError as e:
        print(e)
        # You will get a SlackApiError if "ok" is False
        raise GanymedeException(exception_type="Validation", message=e.response["error"])

    if len(errors) > 0:
        raise GanymedeException(exception_type="Validation", message=", ".join(errors))
    else:
        return NodeReturn()