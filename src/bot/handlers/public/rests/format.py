from src.database.models import User
from src.service.vault.texts import txt_rests_line, txt_rests_list


def format_rests(users: list[User]) -> str:
    lines = []

    for u in users:
        if u.rest_until is None:
            continue

        until_str = u.rest_until.strftime("%d.%m.%Y")
        lines.append(txt_rests_line(u.tg_id, u.username, until_str))

    return txt_rests_list(lines)
