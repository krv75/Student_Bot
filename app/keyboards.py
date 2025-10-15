from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

kb_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="️🗓️ Расписание занятий", callback_data='lesson_schedule')],
    [InlineKeyboardButton(text="🛎️ Расписание звонков", callback_data='call_schedule')],
    [InlineKeyboardButton(text="👩‍🏫 Узнать ФИО преподавателя", callback_data='teacher')],
    [InlineKeyboardButton(text="📋 Расписание экзаменов и зачетов", callback_data='exam schedule')],
    [InlineKeyboardButton(text="📚 Учебные материалы и методички", callback_data='materials')],
    [InlineKeyboardButton(text="💻 Полезные ссылки", callback_data='useful_links')],
    [InlineKeyboardButton(text="🪦 deadline", callback_data='deadlines_info')],
    [InlineKeyboardButton(text="📅 Срок проведения сессии",callback_data='duration_session')]
])


kb_urls = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=" Сайт ЗабГУ", url='https://zabgu.ru/php/index.php')],
    [InlineKeyboardButton(text="Личный кабинет", url='https://social.zabgu.ru/login')],
    [InlineKeyboardButton(text="Юрайт - образовательная платформа", url='https://www.urait.ru/')],
    [InlineKeyboardButton(text="ЭБС Консультант студента", url='https://www.studentlibrary.ru/')],
    [InlineKeyboardButton(text="ЭБС Лань", url='https://e.lanbook.com/?ref=dtf.ru')],
    [InlineKeyboardButton(text="Электронная библиотека ЗабГУ", url='https://mpro.zabgu.ru/MegaPro/Web')],
    [InlineKeyboardButton(text="⬅ Назад в главное меню", callback_data='main_menu')]
])


# КЛАВИАТУРА АДМИНИСТРАТОРА ДЛЯ ВВОДА ДАННЫХ
kb_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить сроки проведения сессии", callback_data='session_name')],
    [InlineKeyboardButton(text="Добавить данные по deadlines", callback_data='dead_lines')],
    [InlineKeyboardButton(text="Добавить график проведения зачетов и экзаменов", callback_data='certification')],
    [InlineKeyboardButton(text="Добавить ФИО преподавателя", callback_data='teacher_info')],
    [InlineKeyboardButton(text="Добавить расписание занятий", callback_data='add_schedule')],
    [InlineKeyboardButton(text="⬅ Назад", callback_data='admin_panel')]
])

# КЛАВИАТУРА ДЛЯ ВОХВРАЩЕНИЯ НАЗАД В ГЛАВНОЕ МЕНЮ СТУДЕНТА

back_stud_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='⬅ Назад в меню', callback_data='main_menu')
    ]
])

# КЛАВИАТУРА ДЛЯ ВОЗВРАЩЕНИЯ НАЗАД В МЕНЮ АДМИНИСТРАТОРА

back_admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='⬅ Назад в меню', callback_data='admin')
    ]
])


# КЛАВИАТУРА ДЛЯ ВВОДА РАСПИСАНИЯ

edit_schedule = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить ввод данных по расписанию:", callback_data='add_schedule')],
    [InlineKeyboardButton(text='⬅ Назад в меню', callback_data='admin')]
])



# КЛАВИАТУРА АДМИНИСТРАТОРА ДЛЯ ВВОДА ДАННЫХ
kb_edit_data = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Редактировать сроки проведения сессии", callback_data='edit_date_session')],
    [InlineKeyboardButton(text="Редактировать данные по deadlines", callback_data='view_deadlines')],
    [InlineKeyboardButton(text="Редактировать график проведения зачетов и экзаменов", callback_data='view_certification')],
    [InlineKeyboardButton(text="Редактировать ФИО преподавателей", callback_data='view_teacher')],
    [InlineKeyboardButton(text="Редактировать расписание занятий", callback_data='edit_schedule')],
    [InlineKeyboardButton(text="⬅ Назад", callback_data='admin_panel')]
])

# КЛАВИАТУРА ДЛЯ ВОЗВРАЩЕНИЯ НАЗАД В МЕНЮ ИЗМЕНЕНИЯ ДАННЫХ
back_edit_data = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='⬅ Назад в меню', callback_data='edit_data')
    ]
])



# КНОПКА РЕГИСТРАЦИИ
reg_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝 Регистрация', callback_data= 'reg')]
])

# КЛАВИАТУРА ДЛЯ ОТПРАВКИ ТЕЛЕФОНА
share_phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить мой номер", request_contact=True)],
        [KeyboardButton(text="✍️ Ввести вручную")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


# Подтверждение номера телефона
confirm_phone_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="✅ Оставить этот номер", callback_data="phone_confirm"),
        InlineKeyboardButton(text="🔄 Ввести другой", callback_data="phone_change")
    ]
])


# МЕНЮ ПОЛНОЙ ПАНЕЛИ АДМИНИСТРАТОРА

full_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить данные", callback_data='admin')],
    [InlineKeyboardButton(text="Редактировать данные", callback_data='edit_data')]
])

back_full_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅ Назад", callback_data='admin_panel')]
])