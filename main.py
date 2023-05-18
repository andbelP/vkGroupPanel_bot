import traceback

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher,executor,types
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.utils.exceptions import BotBlocked
from configs.bot_token import TOKEN
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import random
import asyncio
import time
from aiogram.dispatcher import FSMContext
from datetime import datetime
from aiogram.utils.helper import Helper, HelperMode, ListItem
from vk.mainVk import deleteposts,deletecomments
bot=Bot(TOKEN)
storage=MemoryStorage()
dp=Dispatcher(bot=bot, storage=storage)
scheduler=AsyncIOScheduler()
data=0
from Bases.sqlExample import DataBase
from configs.vktoken import MAINID,ADMINID
#----------------------------------------------on_startup, on_shutdown, botblocked---------------------------------
async def shutdown(dp):

    await bot.close()

async def on_startup(_):
    print('ALL GOOD')


@dp.errors_handler(exception=BotBlocked)
async def bot_block(update:types.Update,exception:BotBlocked)-> bool:
    print('Нельзя отправить сообщение потому что нас заблокировали')
    return True


def startKeyboard()->ReplyKeyboardMarkup:
    kb=ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row('/checking','/cancel').row('/clearcomm','/clearposts','/getbase','/newbanword')
    return kb
# ---------------------------------

@dp.message_handler(commands='start')
async def start(msg:types.Message):
    await msg.answer('Привет. \n/checking чтобы начать слежку за группой\n/cancel для отмены слежки\n/clearComm для подчистки комментов\n/clearPosts для подчистки постов\n/getbase для получения списка запрещенных слов\n/newbanword для добавления запрещенного слова\n/deletebanword для удаления запрещенного слова',reply_markup=startKeyboard())


class newBanwords(StatesGroup):
    banword=State()
async def checkAll(msg,kqb):
    deletecomments(MAINID)
    deleteposts(MAINID)
    await msg.answer('Группа почищена')

@dp.message_handler(commands='checking')
async def checking(msg:types.Message):
    if msg.from_user.id == ADMINID:
        kqb=1
        scheduler.add_job(checkAll,"interval",seconds=10,args=(msg,kqb))
        await msg.answer('Группа подчищается',reply_markup=startKeyboard())



@dp.message_handler(commands='cancel')
async def cancelChecking(msg:types.Message):
    if msg.from_user.id == ADMINID:
        scheduler.shutdown()
        await msg.answer('Редактирование группы прекращено',reply_markup=startKeyboard())




@dp.message_handler(commands='clearcomm')
async def clearComm(msg:types.Message):
    if msg.from_user.id == ADMINID:
        deletecomments(MAINID)
        await msg.answer('Комментарии почищены',reply_markup=startKeyboard())
    else:await msg.answer(msg.from_user.id)




@dp.message_handler(commands='clearposts')
async def clearComm(msg:types.Message):
    if msg.from_user.id == ADMINID:
        deleteposts(MAINID)
        await msg.answer('Посты почищены',reply_markup=startKeyboard())



@dp.message_handler(commands='newbanword',state=None)
async def newBanword(msg:types.Message,state:FSMContext):
    if msg.from_user.id == ADMINID:
        await msg.answer('Напиши новый банворд',reply_markup=startKeyboard())
        await newBanwords.banword.set()

@dp.message_handler(state=newBanwords.banword)
async def addingBanword(msg:types.Message,state:FSMContext):
    if msg.from_user.id == ADMINID:
        banwordsList=[]
        banwordsList.append(msg.text)
        banwordsBase=DataBase('banwordsBase')
        banwordsBase.create_table('banwords','id PRIMARY KEY AUTOINCREMENT, banword TEXT')
        banwordsBase.insert_into('banwords','NULL, ?',banwordsList)
        await msg.answer('Слово добавлено')
        await state.finish()

@dp.message_handler(commands='getbase')
async def getBanwords(msg:types.Message):
    if msg.from_user.id == ADMINID:
        banwordsBase=DataBase('banwordsBase')
        banwords=banwordsBase.request('SELECT banword FROM banwords')
        await msg.answer(banwords,reply_markup=startKeyboard())

class deleteBanwordState(StatesGroup):
    get=State()
@dp.message_handler(commands='deletebanword',state=None)
async def gettingWord(msg:types.Message,state:FSMContext):
    if msg.from_user.id == ADMINID:
        try:
                await msg.answer('Напиши запрещенное слово, которое стоит удалить')
                await deleteBanwordState.get.set()
        except:
            await msg.answer('Ошибка',reply_markup=startKeyboard())

            await state.finish()

@dp.message_handler(state=deleteBanwordState.get)
async def deleteWord(msg:types.Message,state:FSMContext):
    if msg.from_user.id == ADMINID:
        try:
            banwordsBase=DataBase('banwordsBase')
            banwordsBase.requestWithoutFetch(f"DELETE FROM banwords WHERE banword = '{msg.text}'")
            await msg.answer('Слово удалено',reply_markup=startKeyboard())
            await state.finish()
        except:
            await state.finish()
            await msg.answer('Ошибка',reply_markup=startKeyboard())
            traceback.print_exc(limit=None, file=None, chain=True)

if __name__=='__main__':
    scheduler.start()
    executor.start_polling(dp,on_startup=on_startup,skip_updates=True,on_shutdown=shutdown)

