from html import escape
from datetime import timezone

from aiogram.types import BufferedInputFile, Message

from src.database.models import Check
from src.service.vault.texts import txt_check_caption

RECEIPT_FORMAT = "html"


def receipt_filename(check: Check, ext: str = "html") -> str:
    return f"check_{check.id}.{ext}"


def build_receipt_txt(check: Check) -> bytes:
    created = check.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    else:
        created = created.astimezone(timezone.utc)
    lines = [
        "=== \u0427\u0415\u041a \u041f\u041e\u041a\u0423\u041f\u041a\u0418 ===",
        f"\u041d\u043e\u043c\u0435\u0440: {check.id}",
        f"\u0414\u0430\u0442\u0430: {created.strftime('%d.%m.%Y %H:%M:%S UTC')}",
        f"\u041f\u043e\u043a\u0443\u043f\u0430\u0442\u0435\u043b\u044c ID: {check.user_tg_id}",
        f"\u0422\u043e\u0432\u0430\u0440: {check.good_title} ({check.good_id})",
        f"\u041a\u043e\u043b-\u0432\u043e: {check.qty}",
        f"\u0421\u0443\u043c\u043c\u0430: {check.amount}",
        f"\u0411\u0430\u043b\u0430\u043d\u0441 \u043f\u043e\u0441\u043b\u0435: {check.balance_after}",
    ]
    meta = check.meta or {}
    for k, v in meta.items():
        lines.append(f"{k}: {v}")
    lines.append("==================")
    return "\n".join(lines).encode("utf-8")


def build_receipt_html(check: Check) -> bytes:
    created = check.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    else:
        created = created.astimezone(timezone.utc)
    rows = [
        ("\u041d\u043e\u043c\u0435\u0440", str(check.id)),
        ("\u0414\u0430\u0442\u0430", created.strftime("%d.%m.%Y %H:%M:%S UTC")),
        ("\u041f\u043e\u043a\u0443\u043f\u0430\u0442\u0435\u043b\u044c ID", str(check.user_tg_id)),
        ("\u0422\u043e\u0432\u0430\u0440", f"{check.good_title} ({check.good_id})"),
        ("\u041a\u043e\u043b-\u0432\u043e", str(check.qty)),
        ("\u0421\u0443\u043c\u043c\u0430", str(check.amount)),
        ("\u0411\u0430\u043b\u0430\u043d\u0441 \u043f\u043e\u0441\u043b\u0435", str(check.balance_after)),
    ]
    meta = check.meta or {}
    for k, v in meta.items():
        rows.append((str(k), str(v)))
    trs = "".join(
        f"<tr><td>{escape(label)}</td><td>{escape(value)}</td></tr>"
        for label, value in rows
    )
    html = (
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
        "<title>\u0427\u0435\u043a \u2116" + escape(str(check.id)) + "</title>"
        "<style>"
        "body{font-family:sans-serif;margin:24px;color:#111}"
        "h1{font-size:18px;margin:0 0 16px}"
        "table{border-collapse:collapse;width:100%;max-width:480px}"
        "td{border:1px solid #ccc;padding:8px 10px;vertical-align:top}"
        "td:first-child{font-weight:600;width:40%;background:#f7f7f7}"
        "</style></head><body>"
        f"<h1>\u0427\u0435\u043a \u043f\u043e\u043a\u0443\u043f\u043a\u0438 \u2116{escape(str(check.id))}</h1>"
        f"<table>{trs}</table>"
        "</body></html>"
    )
    return html.encode("utf-8")


def build_receipt(check: Check, fmt: str = "html") -> tuple[str, bytes, str]:
    fmt = fmt.lower()
    if fmt == "txt":
        return receipt_filename(check, "txt"), build_receipt_txt(check), "text/plain"
    return receipt_filename(check, "html"), build_receipt_html(check), "text/html"


async def send_check_file(message: Message, check: Check, fmt: str = RECEIPT_FORMAT) -> None:
    name, data, _ = build_receipt(check, fmt)
    await message.answer_document(document=BufferedInputFile(data, filename=name), caption=txt_check_caption(check.id))
