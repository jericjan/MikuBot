import toolz
from modules.paginator import text_splitter


def search(storage, s_filter=None, show_numbers=True):
    Statement = storage.get_model("statement")
    session = storage.Session()
    statements = session.query(Statement).filter()
    if s_filter is None:
        text_list = list(statements)
    else:
        text_list = [x for x in statements if s_filter in x.text]
    print(f"{len(text_list)} found")
    text_list.sort(key=lambda x: x.text)
    text_list_str = toolz.unique(text_list, key=lambda x: x.text)
    if show_numbers:
        text_list_str = "\n".join(
            [
                f"{idx+1}. {x.text} ({x.conversation})"
                for idx, x in enumerate(text_list_str)
            ]
        )
    else:
        text_list_str = "\n".join(
            [f"{x.text} ({x.conversation})" for idx, x in enumerate(text_list_str)]
        )
    text_list = [x.text for x in text_list]
    session.close()
    splitted_text = text_splitter(text_list_str)
    return text_list, splitted_text


def delete(storage, text_list):
    errors = 0
    for text in text_list:
        try:
            print(f'Deleting "{text}"')
            storage.remove(text)
        except Exception as e:
            print(f"Exception: {e}")
            errors += 1
    return errors
