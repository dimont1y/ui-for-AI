from typing import Optional

from agents import function_tool

from api_client.multiplex_api_client import get_schedule


@function_tool
def cinema_schedule_tool(date: Optional[str] = None) -> str:
    """
    This tool is used to get the cinema schedule.
    :param date: The date for which to get the schedule. The format is "ddmmyyyy".
    :return: The cinema schedule (in JSON format)
    """
    return get_schedule(date)
