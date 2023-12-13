def check_string_for_null(txt: str) -> bool:
    return txt in ["", "None", None]


def convert_string_to_float(txt: str) -> float:
    try:
        return float(txt) if txt is not None and txt != '' else 0
    except ValueError:
        return 0