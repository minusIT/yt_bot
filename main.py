import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from downloader import Downloader
import os

token = os.environ['ID']

# Configure logging
logging.basicConfig(level=logging.INFO)



points = ["Get Subs"]

keyboards = {'main': types.ReplyKeyboardMarkup(resize_keyboard=True).add("Get Subs", "Refresh"),
			'cancel': types.ReplyKeyboardMarkup(resize_keyboard=True).add("Cancel")}

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

dw = Downloader();

# States
class Form(StatesGroup):
	link = State()
	start_time = State()
	stop_time = State()


@dp.message_handler(lambda message: message.text not in points)
async def cmd_start(message: types.Message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
	markup.add("Get Subs", "Refresh")
	await message.reply("Choose option", reply_markup=markup)


@dp.message_handler(Text(equals='Get Subs', ignore_case=True), state='*')
async def start_getting_sub(message: types.Message):
	await Form.link.set()
	await message.reply("Paste the link of the video you want to get subtitles from. \n",
		reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    await message.reply('Cancelled.', reply_markup=keyboards['main'])


@dp.message_handler(state=Form.link)
async def getting_link(message: types.Message):
	if dw.set_url(message.text):
		await Form.next()
		await message.reply("Write start time in format:\n 12:15:22", reply_markup=keyboards['cancel'])
	else:
		await message.answer("Wrong link. Send again.", reply_markup=keyboards['cancel'])

@dp.message_handler(state=Form.start_time)
async def getting_start_time(message: types.Message):
	try:
		dw.set_time("start", message.text)
		await Form.next()
		await message.reply("Write end time in format:\n 12:16:22", reply_markup=keyboards['cancel'])
	except Exception:
		await message.answer("Wrong time format. Send again", reply_markup=keyboards['cancel'])

@dp.message_handler(state=Form.stop_time)
async def getting_start_time(message: types.Message, state: FSMContext):
	try:
		dw.set_time("end", message.text)
		await state.finish()
	except Exception:
		await message.answer("Wrong time format. Send again", reply_markup=keyboards['cancel'])
	subs = await dw.get_titles()
	await message.reply(subs,
			reply_markup=keyboards['main'])

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):

	await message.reply("Hi!\nIn this bot you can getting subs from YT.")

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)
