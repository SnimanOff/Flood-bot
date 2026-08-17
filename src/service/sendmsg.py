from aiogram.enums import ChatType
from aiogram.types import InputMediaPhoto, Message


async def send_msg(message: Message, text: str, media: str = "", reply_markup=None, parse_mode: str | None = "HTML", only_caller: bool = False, edit: bool = False) -> Message:
    kwargs = {"reply_markup": reply_markup, "parse_mode": parse_mode}

    if only_caller and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        kwargs["receiver_user_id"] = message.from_user.id

    if edit:
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
            pass

        try:
            await message.delete()
        except Exception:
            pass

        if media:
            return await message.answer_photo(photo=media, caption=text, **kwargs)
        return await message.answer(text=text, **kwargs)

    if media:
        return await message.answer_photo(photo=media, caption=text, **kwargs)
    return await message.answer(text=text, **kwargs)
