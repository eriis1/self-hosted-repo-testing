# import custom lib function
from lib.e2e_test_functions import e2e_test
from lib.nested.nested import e2e_test_nested

from ganymede_sdk import GanymedeContext


def execute(
    df_sql_result, ganymede_context: GanymedeContext
):
    # verify lib function runs
    assert e2e_test()
    assert e2e_test_nested()
    return


