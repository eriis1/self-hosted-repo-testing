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
        message["attachments"][0]["blocks"].append(
            {"type": "section", "text": {"type": "mrkdwn", "text": f"```{error_message}```"}}
        )

    return message


def execute(csv_file: dict[str, BytesIO], ganymede_context: GanymedeContext) -> NodeReturn:
    """
    Processes CSV file(s) (passed to function as BytesIO file-like objects) into data tables
    stored in data lake

    Parameters
    ----------
    csv_file : dict[str, BytesIO]
        CSV files, indexed by file name
    ganymede_context : GanymedeContext
        Ganymede context variable, which stores flow run metadata

    Returns
    -------
    NodeReturn
        Object containing data to store in data lake and/or file storage.
    """

    slack_token = get_secret("test_slack_integration_token")
    client = WebClient(token=slack_token)

    url = "https://admin.dev.ganymede.bio/ganymede-dev-multi/flows/slack-test/runs"

    message = create_message(
        "#FFD700",
        ganymede_context["dag"]["dag_id"],
        ":hourglass_flowing_sand:",
        "Running",
        ganymede_context["inputs"]["initiator"]["initiatorId"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        url,
    )
    print(message)

    try:
        response = client.chat_postMessage(
            channel="C085GEWGJJ2", attachments=message["attachments"]
        )
        print(response)
    except SlackApiError as e:
        print(e)
        # You will get a SlackApiError if "ok" is False
        raise GanymedeException(exception_type="Validation", message=e.response["error"])

    messages_sent = pd.DataFrame(
        {"timestamp": response["ts"], "__run_id": ganymede_context.flow_run_id}, index=[0]
    )

    results_dict = dict()

    if len(csv_file) > 1:
        for filename, file_contents in csv_file.items():
            results_dict[filename] = pd.read_csv(file_contents)
    else:
        df = pd.read_csv(list(csv_file.values()).pop())
        df["__run_id"] = ganymede_context.flow_run_id
        return NodeReturn(
            tables_to_upload={
                "slack_integration_test": df,
                "slack_message_timestamps": messages_sent,
            }
        )

    return NodeReturn(tables_to_upload=results_dict)