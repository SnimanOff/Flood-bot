from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.database.models import User
from src.database.repositories import UserRepository
from src.service.sendmsg import send_msg
from src.service.vault.media import GM_DENIED_MEDIA, GM_MEDIA, GM_OK_MEDIA, GM_USAGE_MEDIA
from src.service.vault.roles import Role


router = Router(name="rests")

