def get_all_stripped(node, query: str) -> str | None:
    lst = get_list(node, query)
    if lst is not None and len(lst) > 0:
        return ' '.join(lst)
    return None


def get_stripped(node, query: str) -> str | None:
    value = node.css(query).get()
    if value is not None:
        return value.strip()
    return None


def get_any(node, queries: list[str]) -> str | None:
    for query in queries:
        v = get_stripped(node, query)
        if v is not None:
            return v
    return None


def get_list(node, query: str) -> list[str] | None:
    values = node.css(query).getall()
    if values is None or len(values) == 0:
        return None
    return [
        value.strip()
        for value in values
        if value is not None and len(value.strip()) > 0
    ]
