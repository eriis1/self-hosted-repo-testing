import pandas as pd
import itertools

import sendgrid
from IPython.core.display import HTML
from jinja2 import Template
from sendgrid.helpers.mail import (
    Content,
    CustomArg,
    Email,
    Mail,
    MailSettings,
    Personalization,
    SandBoxMode,
)

from ganymede_sdk import GanymedeContext, get_secret, NodeReturn
from ganymede_sdk.lib import _is_airflow

HTML_TEMPLATE = """
<style>
  .image-container {
    padding: 50px; /* Adjust the padding value as needed */
  }
</style>

<div style="background-color:white;margin:0px" bgcolor="white">
    <div style="color:transparent;opacity:0;font-size:0px;border:0;max-height:1px;width:1px;margin:0px;padding:0px;border-width:0px!important;display:none!important;line-height:0px!important">
      <img border="0" width="1" height="1" src="" alt="">
    </div>
    <table cellspacing="0" border="0" cellpadding="0" align="center" width="600" class="" style="background-color:white;border-collapse:separate;border-spacing:0;font-family:Helvetica,Arial,sans-serif;letter-spacing:0;max-width:100%;table-layout:fixed" bgcolor="white">
      <tbody>
        <tr>
          <td style="font-family:Helvetica,Arial,sans-serif;font-size:16px;padding:60px 0 0">
            <table width="100%" style="border-collapse:separate;border-spacing:0;max-width:100%;table-layout:fixed">
              <tbody>
                <tr>
                  <td style="font-family:Helvetica,Arial,sans-serif;font-size:16px;padding:0;text-align:center" align="center">
                    <div class="image-container">
                        <img src='https://storage.googleapis.com/ganymede-bio-website/public/logo/Ganymede_logo-02.png' width=35% height=auto/img>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            <table width="100%" class="" style="border-collapse:separate;border-spacing:0;max-width:100%;table-layout:fixed">
              <tbody>
                <tr>
                  <td class="" style="color:#818181;font-family:Helvetica,Arial,sans-serif;font-size:16px;line-height:150%;padding:0 0 60px">

                    <p style="font-size:16px;margin:0 0 13px;padding-left:10%;padding-right:10%">Ganymede Flow <b> {{ dag_id }} </b> custom email alert:</p>

                    <p style="font-size:16px;margin:0 0 13px;padding-left:10%;padding-right:10%"> {{ message }} </p>

                    <table class="" align="center" style="border-collapse:collapse;border-spacing:0;margin:30px auto;max-width:100%;padding:0 10%;table-layout:fixed;text-align:center!important">
                    </table>
                    <p style="font-size:16px;margin:0 0 13px;padding-left:10%;padding-right:10%"></p>
                    <p style="font-size:16px;margin:0 0 13px;padding-left:10%;padding-right:10%">
                      <b style="color:#606060">Details:</b>
                      <br>Flow: {{ dag_id }}
                      <br>User: {{ initiatorId }}
                      <br>Flow Run ID: {{ run_id }}
                    </p>
                  </td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
      </tbody>
    </table>
    <table cellspacing="0" border="0" cellpadding="0" align="center" width="100%" bgcolor="transparent" class="" style="background-color:#f8f8f8;border-collapse:separate;border-spacing:0;font-family:Helvetica,Arial,sans-serif;letter-spacing:0;max-width:800px;table-layout:fixed">
      <tbody>
        <tr>
          <td style="font-family:Helvetica,Arial,sans-serif;font-size:16px;padding:26px 30px 22px;text-align:center;width:100%" align="center">
            <p style="color:#a8a8a8;font-size:13px;font-weight:300;line-height:1.5;margin:0 0 10px;text-decoration:none">Ganymede Bio 3000 El Camino Real Bldg. 4, Suite 200 Palo Alto, CA 94306</p>
            </p>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  </div>
  </div>
  </div>
"""  # noqa: E501


def get_email_address_list(emails: str | list[str] | None) -> list[str]:
    if not emails:
        return []
    if isinstance(emails, str):
        emails = [emails]

    return emails


class GanymedeEmailAlert:
    """
    Send custom email alerts from Ganymede flows

    Attributes:
    ----------
    ganymede_context : GanymedeContext

    Methods:
    -------
    send_email
    convert_message_to_html

    Examples:
    --------
    from ganymede_sdk import Ganymede
    from ganymede_sdk.util.email import GanymedeEmailAlert

    g = Ganymede()

    email_alert = GanymedeEmailAlert(g.ganymede_context)
    email_alert.send_email(
        "user@email.com", "My subject", "My message to send",
        cc="user@ganymede.bio",
        bcc="user@email.com"
    )
    """

    def __init__(self, ganymede_context: GanymedeContext, html_template=HTML_TEMPLATE):
        """
        Construct the emailer object

        Parameters:
        ----------
        ganymede_context : GanymedeContext
            Ganymede context to get run attributes
        html_template : str
            HTML Jinja template to use for the email content. The default template can be found by
            importing the module and accessing the `HTML_TEMPLATE` attribute.
        """
        self.ganymede_context = ganymede_context
        self.html_template = html_template

    def _send_email(
        self,
        to: str | list[str],
        subject: str,
        html_content: HTML,
        cc: str | list[str] = None,
        bcc: str | list[str] = None,
        from_name: str = "notifications@ganymede.bio",
        from_email: str = "notifications@ganymede.bio",
        sandbox_mode: bool = not _is_airflow(),
        **kwargs,
    ) -> None:
        """
        Send an email if the current environment is running in airflow.
        """
        mail = Mail()
        mail.from_email = Email(from_email, from_name)
        mail.subject = subject
        mail.mail_settings = MailSettings()

        if sandbox_mode:
            print("Running in sandbox mode...")
            mail.mail_settings.sandbox_mode = SandBoxMode(enable=True)

        personalization = Personalization()
        to = get_email_address_list(to)
        for to_address in to:
            personalization.add_to(Email(to_address))
        if cc:
            cc = get_email_address_list(cc)
            for cc_address in cc:
                personalization.add_cc(Email(cc_address))
        if bcc:
            bcc = get_email_address_list(bcc)
            for bcc_address in bcc:
                personalization.add_bcc(Email(bcc_address))

        # Add custom_args to personalization if present
        pers_custom_args = kwargs.get("personalization_custom_args")
        if isinstance(pers_custom_args, dict):
            for key, val in pers_custom_args.items():
                personalization.add_custom_arg(CustomArg(key, val))

        mail.add_personalization(personalization)
        mail.add_content(Content("text/html", html_content))

        mail_data = mail.get()

        sendgrid_client = sendgrid.SendGridAPIClient(api_key=get_secret("sendgrid_api_key"))
        response = sendgrid_client.client.mail.send.post(request_body=mail_data)

        # 2xx status code.
        if 200 <= response.status_code < 300:
            print(
                f"Email with subject {mail_data['subject']} is successfully sent to recipients: {mail_data['personalizations']}"
            )
        else:
            print(
                f"Failed to send out email with subject {mail_data['subject']}, status code: {response.status_code}"
            )

    def send_email(
        self,
        to: str | list[str],
        subject: str,
        message: str,
        cc: str | list[str] | None = None,
        bcc: str | list[str] | None = None,
        **kwargs,
    ) -> HTML:
        """
        Sets up an email to specified recipients and will send it only if the
        current environment is running in Airflow. Returns the HTML object
        of the email.

        Requires Sendgrid API key to be set for the environment.

        Parameters:
        ----------
        to : str | list[str]
            The recipient(s) of the email. This can be a single email address (str) or
            a list of email addresses (List).
        subject : str
            The subject of the email.
        message : str
            The plain text message content of the email.
        cc : str | list[str] | None
            The recipient(s) to be copied on the email (CC), by default None.
            This can be a single email address or a list of email addresses.
        bcc : str | list[str] | None
            The recipient(s) to be blindly copied on the email (BCC), by default None.
            This can be a single email address or a list of email addresses.

        Returns:
        -------
        HTML
            An HTML object containing information about the email and its
            content. This is useful when running object in a notebook.

        Raises:
        ------
        ValueError
            Raises an error when duplicated emails are found between recipients, cc, and bcc. This
            will crash the airflow emailer.

        Notes:
        -----
        If the function is called within an Airflow context, it uses Airflow's
        email module to send the email configurations. If not within an Airflow
        context, the function constructs the email content and information and
        returns it as an HTML object.

        Examples:
        --------
        ```python
        from ganymede_sdk import Ganymede
        from ganymede_sdk.util.email import GanymedeEmailAlert

        g = Ganymede()

        email_alert = GanymedeEmailAlert(g.ganymede_context)

        # To send to single users
        email_alert.send_email(
            "user@email.com", "My subject", "My message to send",
            cc="user@ganymede.bio",
            bcc="user@email.com"
        )

        # To send to multiple users
        email_alert.send_email(
            "user@email.com", "My subject", "My message to send",
            cc="user@ganymede.bio",
            bcc="user@email.com"
        )
        ```
        """
        if has_duplicated_email_recipients(to, cc, bcc):
            raise ValueError(f"Duplicate recipients found: to = {to}, cc = {cc}, bcc = {bcc}")

        html_content = self.convert_message_to_html(message)

        self._send_email(
            to=to,
            subject=subject,
            html_content=html_content,
            cc=cc,
            bcc=bcc,
            **kwargs,
        )

        return HTML(html_content)

    def convert_message_to_html(self, message: str) -> str:
        """
        This function takes a plain text message and converts it to an
        HTML-formatted message by replacing placeholders in an HTML template
        with provided values. Other placeholders in the HTML template are taken
        from the ganymede_context.

        Parameters:
        ----------
        message : str
            The plain text message to be placed in the HTML template

        Returns:
        -------
        str
            An HTML-formatted message.
        """
        dag_id = self.ganymede_context.dag.dag_id
        initiator_id = self.ganymede_context.params.get("initiator", {}).get("initiatorId", "")
        flow_run_id = self.ganymede_context.flow_run_id
        return Template(self.html_template).render(
            {
                "dag_id": dag_id,
                "message": message,
                "initiatorId": initiator_id,
                "run_id": flow_run_id,
            }
        )


def has_duplicated_email_recipients(*emails) -> bool:
    """
    Check if there are any duplicate recipients in the given list of emails.

    Parameters
    ----------
    *emails : tuple
        Variable number of email addresses. Each email address can be a string or a list of strings.

    Returns
    -------
    bool
        True if there are no duplicate recipients, False otherwise.
    """
    emails = [
        recipient if isinstance(recipient, list) else [recipient]
        for recipient in emails
        if recipient is not None
    ]
    emails = list(itertools.chain(*emails))
    return len(emails) != len(set(emails))


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
    Documentation on these functions can be found at https://docs.ganymede.bio/api/GanymedeClass
    """

    email_alert = GanymedeEmailAlert(ganymede_context)
    email_alert.send_email(
        to="benson@ganymede.bio", subject="My subject", message="My message to send"
    )

    return NodeReturn()
