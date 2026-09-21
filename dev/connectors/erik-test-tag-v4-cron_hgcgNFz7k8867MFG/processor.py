from ganymede_sdk.agent.models import FileParam, UploadFileParams
from ganymede_sdk.file_tag import add_file_tag
import time

from google.auth import crypt, jwt
from google.oauth2 import service_account

import agent.sys_env as env
import openapi_client

jwt_expiry_length = 5000


# Required Function
def execute(**kwargs) -> UploadFileParams:
    filename = "changeme.txt"
    body = bytes("Hello, World!", "utf-8")

    logger = kwargs["logger"]
    logger("Hello from processor!")

    jwt = get_sa_jwt("dev.ganymede.bio")
    logger("JWT: ", jwt)

    try:
        add_file_tag(
            input_file_path="gs://ganymede-ganymede-dev-lab-ingest/_agents/erik_test_tag_v4/0f2c257d-52eb-44b8-bd6f-0ac01646f941/changeme_20240607_191602.txt",
            tag_type_id="multi",
            display_value="test1",
            bucket="input",
        )
    except Exception as error:
        logger("TAG ERROR: ", error)

    new_file_param = FileParam(filename=filename, body=body)

    return UploadFileParams(files=[new_file_param])


def get_sa_jwt(host: str) -> str:
    sa = env.get_sa()
    credentials = service_account.Credentials.from_service_account_info(info=sa)
    credentials._create_self_signed_jwt(audience=host)

    sa_email = sa["client_email"]
    audience = host

    now = int(time.time())

    # build payload
    payload = {
        **sa,
        "iat": now,
        # expires after 'expiry_length' seconds.
        "exp": now + jwt_expiry_length,
        # iss must match 'issuer' in the security configuration in your
        # swagger spec (e.g. service account email). It can be any string.
        "iss": sa_email,
        # aud must be either your Endpoints service name, or match the value
        # specified as the 'x-google-audience' in the OpenAPI document.
        "aud": audience,
        # sub and email should match the service account's email address
        "sub": sa_email,
        "email": sa_email,
    }

    # sign with keyfile
    signer = crypt.RSASigner.from_service_account_info(sa)
    jwt_token = jwt.encode(signer=signer, payload=payload)
    return jwt_token.decode("utf-8")

