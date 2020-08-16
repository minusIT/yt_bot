import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

import config

token = config.token

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher


link = ''
start = ''
stop = ''

points = ["Get Subs", "Refresh"]

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
	link = State()  
	start_time = State()
	stop_time = State()


@dp.message_handler(lambda message: message.text not in points)
async def cmd_start(message: types.Message):
	"""
	Conversation's entry point
	"""
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
	markup.add("Get Subs", "Refresh")
	await message.reply("Choose option", reply_markup=markup)


@dp.message_handler(Text(equals='Get Subs', ignore_case=True), state='*')
async def start_getting_sub(message: types.Message):
	await Form.link.set()
	await message.reply("Send link on video", 
		reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=Form.link) #^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$
async def getting_link(message: types.Message):
	link = message.text
	await Form.next()
	await message.reply("Write start time")

@dp.message_handler(state=Form.start_time)
async def getting_start_time(message: types.Message):
	start = message.text
	await Form.next()
	await message.reply("Write stop time")

@dp.message_handler(state=Form.stop_time)
async def getting_start_time(message: types.Message, state: FSMContext):
	stop = message.text
	await state.finish()
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
	markup.add("Get Subs", "Refresh")
	await message.reply("Your youtube", 
		reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
	"""
	This handler will be called when user sends `/start` or `/help` command
	"""
	await message.reply("Hi!\nI'm EchoBot!")

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)



