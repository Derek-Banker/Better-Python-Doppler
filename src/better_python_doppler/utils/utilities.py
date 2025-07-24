def list_to_comma_string(input_list: list) -> str:
    if len(input_list) == 0:
        return ""

    result: str = ""
    for item in input_list:
        result += str(item) +","

    return result