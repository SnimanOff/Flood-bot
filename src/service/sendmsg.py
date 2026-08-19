from aiogram.enums import ChatType
from aiogram.types import InputMediaPhoto, Message

from src.service.logger import log_tech


def _preview(text: str, limit: int = 80) -> str:
    t = text.replace("\n", " ")
    if len(t) <= limit:
        return t
    return t[:limit] + "..."


async def send_msg(message: Message, text: str, media: str = "", reply_markup=None, parse_mode: str | None = "HTML", only_caller: bool = False, edit: bool = False) -> Message:
    kwargs = {"reply_markup": reply_markup, "parse_mode": parse_mode}
    chat_id = message.chat.id

    if only_caller and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        kwargs["receiver_user_id"] = message.from_user.id

    if edit:
        log_tech.debug("send_msg edit chat_id={} preview={}", chat_id, _preview(text))
        try:
            if media:
                if message.photo:
                    await message.edit_media(media=InputMediaPhoto(media=media, caption=text, parse_mode=parse_mode), reply_markup=reply_markup)
                else:
                    await message.delete()
                    return await message.answer_photo(photo=media, caption=text, **kwargs)
            else:
                if message.photo:
                    await message.edit_caption(caption=text, parse_mode=parse_mode, reply_markup=reply_markup)
                else:
                    await message.edit_text(text=text, parse_mode=parse_mode, reply_markup=reply_markup)
            return message
        except Exception:
            log_tech.warning("send_msg edit failed chat_id={}, fallback send", chat_id)
            pass

        try:
            await message.delete()
        except Exception:
            pass

        if media:
            return await message.answer_photo(photo=media, caption=text, **kwargs)
        return await message.answer(text=text, **kwargs)

    log_tech.debug("send_msg send chat_id={} edit={} preview={}", chat_id, edit, _preview(text))
    if media:
        return await message.answer_photo(photo=media, caption=text, **kwargs)
    return await message.answer(text=text, **kwargs)
