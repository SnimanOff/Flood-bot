from aiogram.enums import ChatType
from aiogram.types import Message


async def send_msg(message: Message, text: str, media: str = "", reply_markup=None, parse_mode: str | None = "HTML", only_caller: bool = False) -> Message:
    kwargs = {"reply_markup": reply_markup, "parse_mode": parse_mode}

    if only_caller and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        kwargs["receiver_user_id"] = message.from_user.id

    if media:
        return await message.answer_photo(photo=media, caption=text, **kwargs)

    return await message.answer(text=text, **kwargs)
