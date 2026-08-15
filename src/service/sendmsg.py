from aiogram.types import Message


async def send_msg(message: Message, text: str, media: str = "", reply_markup=None, parse_mode: str | None = "HTML") -> Message:
    if media:
        return await message.answer_photo(photo=media, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    return await message.answer(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
