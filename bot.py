import os
import logging.config

import aiohttp
import environ
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.emoji import emojize
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from translators import get_translate_ru_to_en, get_translate_en_to_ru

env = environ.Env()
environ.Env.read_env()

logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

TRANSLATE_BOT_TELEGRAM_TOKEN = os.environ.get('TRANSLATE_BOT_TELEGRAM_TOKEN')
CATS_URL = 'https://loremflickr.com/320/240'

bot_translator = Bot(token=TRANSLATE_BOT_TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot_translator, storage=storage)

dp.middleware.setup(LoggingMiddleware())


class Form(StatesGroup):
    first_choice = State()
    language_choice = State()
    text_to_translate = State()


async def get_cats_image():
    async with aiohttp.ClientSession() as session:
        async with session.get(CATS_URL, allow_redirects=True) as response:
            return await response.read()


@dp.message_handler(state='*', commands='start')
async def send_welcome(message: types.Message):
    user = message.from_user.first_name

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Нужно кое-что перевести.')
    markup.add('Покажи котика!')

    await Form.first_choice.set()
    await message.answer(
        emojize(f'Привет, {user}!\nЯ - бот-переводчик :sunglasses:\n'
                'Чем могу помочь?\nСписок доступных команд /help'),
        reply_markup=markup
    )


@dp.message_handler(state='*', commands='help')
async def help_handler(message: types.Message, state: FSMContext):

    await bot_translator.send_message(
        message.chat.id,
        md.text(
            md.text('/start- запуск Бота.'),
            md.text('/help - список команд.'),
            md.text('/cancel - отменить выбор.'),
            md.text('/translate - начать перевод.'),
            md.text('/cats - котики.'),
            sep='\n'
        ),
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()


@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('Начать сначала /start, /help',
                         reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(
    lambda message:
    message.text not in ['Покажи котика!', 'Нужно кое-что перевести.'],
    state=Form.first_choice
)
async def process_first_choice_invalid(message: types.Message):
    return await message.answer(emojize('Не понятно :face_with_monocle:'))


@dp.message_handler(state='*', commands='cats')
@dp.message_handler(lambda message: message.text == 'Покажи котика!',
                    state=Form.first_choice)
async def send_cat_image(message: types.Message, state: FSMContext):
    await state.update_data(first_choice=message.text)
    image = await get_cats_image()
    await bot_translator.send_photo(message.chat.id, image, caption='Котик')


@dp.message_handler(state='*', commands='translate')
@dp.message_handler(lambda message: message.text == 'Нужно кое-что перевести.',
                    state=Form.first_choice)
async def choice_translation_language(message: types.Message,
                                      state: FSMContext):
    await state.update_data(first_choice=message.text)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('русский >> английский')
    markup.add('английский >> русский')

    await state.finish()
    await Form.language_choice.set()
    await message.answer('Выбери язык.', reply_markup=markup)


@dp.message_handler(
    lambda message:
    message.text not in ['русский >> английский', 'английский >> русский'],
    state=Form.language_choice
)
async def process_language_choice_invalid(message: types.Message):
    return await message.answer(emojize('Не понятно :face_with_monocle:'))


@dp.message_handler(
    lambda message:
    message.text == 'русский >> английский' or 'английский >> русский',
    state=Form.language_choice)
async def process_translate(message: types.Message, state: FSMContext):
    await state.update_data(language_choice=message.text)
    async with state.proxy() as data:
        data['language'] = message.text

    await Form.text_to_translate.set()
    await message.answer('Отличный выбор!\nВведи текст.',
                         reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.text_to_translate)
async def send_translate_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text

    if data['language'] == 'русский >> английский':
        translated_text = get_translate_ru_to_en(data['text'])
    else:
        translated_text = get_translate_en_to_ru(data['text'])

    await message.answer(translated_text)


@dp.message_handler()
async def process_message_out_of_state(message: types.Message):
    await message.answer(emojize(':yum:'))


if __name__ == '__main__':
    logger.debug('Запуск Бота')
    executor.start_polling(dp, skip_updates=True)
