from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.database.repositories import UserRepository

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: Message, users: UserRepository) -> None:

    user, created = UserRepository.get_or_create(message.from_user.id)

    if created == True:
        ... 
    else:
        ...