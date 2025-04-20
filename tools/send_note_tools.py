from agents import function_tool

from api_client.telegram_api_client import send_message


@function_tool
def send_note(note: str) -> str:
    """
    This tool is used to send a note to the user.
    :param note: The note to send.
    :return: The result of execution. Success or fail.
    """

    try:
        send_message(note)
    except Exception as e:
        return f"Failed to send note. Error: {e}"
    return "Note sent successfully!"
