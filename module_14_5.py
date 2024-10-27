from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from crud_functions import *


logging.basicConfig(level=logging.INFO)

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Создание клавиатуры
kb = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация')
        ],
        [
            KeyboardButton(text='Купить'),
            KeyboardButton(text='Регистрация')
        ]
    ],
    resize_keyboard=True
)

# Формируем inline-клавиатуру
ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
        InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')]
    ]
)


kb1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Продукт 1', callback_data='product_buying'),
         InlineKeyboardButton(text='Продукт 2', callback_data='product_buying'),
         InlineKeyboardButton(text='Продукт 3', callback_data='product_buying'),
         InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')]
    ]
)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


# Хэндлер команды /start
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.',reply_markup=kb)


# Хэндлер для запроса "Рассчитать"
@dp.message_handler(text=['Рассчитать'])
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=ikb)


@dp.message_handler(text=['Информация'])
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=ikb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer('Формула Миффлина-Сан Жеора: '
                                 '(10 * вес + 6.25 * рост - 5 * возраст + 5)')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст: (лет)')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(text='Купить')
async def get_buying_list(message: types.Message):
    base = get_all_products()
    for number in base:
        await message.answer(f'Название:Продукт {number[1]} / Описание: описание {number[2]} / Цена: {number[3]}')
        with open(f'{number[0]}.jpg', 'rb') as file:
            await message.answer_photo(file)

    await message.answer('Выберите продукт для покупки:', reply_markup=kb1)
# @dp.message_handler(text='Купить')
# async def get_buying_list(message: types.Message):
#     # Получаем свежие данные из базы
#     products = get_all_products()
#
#     for product in products:
#         await message.answer(f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}')
#
#         try:
#             with open(f'{product[0]}.jpg', 'rb') as file:
#                 await message.answer_photo(file)
#         except FileNotFoundError:
#             await message.answer('Изображение для этого продукта не найдено.')
#
#     await message.answer('Выберите продукт для покупки:', reply_markup=kb1)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт.')
    await call.answer()


# Хэндлер для состояния age
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост: (в см)')
    await UserState.growth.set()


# Хэндлер для состояния growth
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес: (кг)')
    await UserState.weight.set()


# Хэндлер для состояния weight и расчет калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    result = int(10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5)
    await message.answer(f'Ваша норма калорий: {result} в день.')
    await state.finish()


@dp.message_handler(text=['Регистрация'])
async def sing_up(message: types.Message):
    await message.answer('Введите имя пользователя (только латинский алфавит): ')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    if is_included(message.text):
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()
    else:
        await state.update_data(username=message.text)
        await message.answer('Введите свой email: ')
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст: ')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.update_data(balance=1000)
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'], data['balance'])
    await message.answer("Регистрация прошла успешно")
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)