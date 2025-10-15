from aiogram import Router, F
import asyncio
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from app.database.models import db
import app.keyboards as kb
from app.state import Reg
from aiogram.types import ReplyKeyboardRemove

handlers = Router()

@handlers.message(CommandStart())
async def cmd_start(message: Message):
    tg_id = message.from_user.id
    user_row = await db.pool.fetchrow('''SELECT id FROM students WHERE tg_id = $1''', tg_id)

    if user_row:
        await message.answer("✅ Вы уже зарегистрированы \n", reply_markup=kb.kb_main_menu)
        return

    else:
        user_name = message.from_user.full_name
        await message.answer(f"Здравствуйте {user_name}!\n"
                             f"Информационный бот создан для студентов группы ИСТз-22.\n"
                             f" Данный бот поможет:\n"
                             f"- Найти расписание занятий\n"
                             f"- Найти расписание звонков\n"
                             f"- Узнать ФИО преподавателей\n"
                             f"- Найти расписание экзаменов и зачетов\n"
                             f"- Найти учебные и методические материалы\n"
                             f"- Найти полезные ссылки\n"
                             f"- Посмотреть сроки сдачи курсовых и других видов работ\n"
                             f"- Узнать сроки проведения сессии\n\n"
                             f"Для продолжения пройдите регистрацию",
                             reply_markup=kb.reg_kb)


@handlers.callback_query(F.data == 'reg')
async def reg(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите Ваше имя")
    await state.set_state(Reg.name)


@handlers.message(Reg.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.phone)
    await message.answer(
        "Теперь укажите номер телефона.\n"
        "Вы можете отправить свой номер из Telegram или ввести вручную:",
        reply_markup=kb.share_phone_kb)


@handlers.message(Reg.phone, F.text)
async def reg_phone_text(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not phone.startswith('+') or not phone[1:].isdigit():
        await message.answer("❌ Введите корректный номер (например: +79991234567)")
        return
    await state.update_data(phone=phone)

    await message.answer(
        f"Мы получили ваш номер: {phone}\n\n"
        f"Хотите оставить его или ввести другой?",
        reply_markup=kb.confirm_phone_kb)


@handlers.message(Reg.phone, F.contact)
async def reg_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await message.answer(
        f"Мы получили ваш номер: {phone}\n\n"
        f"Хотите оставить его или ввести другой?",
        reply_markup=kb.confirm_phone_kb)


@handlers.callback_query(F.data == "phone_confirm")
async def phone_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")

    await db.pool.fetchrow('''
    INSERT INTO students (tg_id, name, phone)
    VALUES ($1, $2, $3) 
    ON CONFLICT (tg_id) DO NOTHING''',
    callback.from_user.id,
    data["name"],
    phone)

    await callback.message.answer(
        f"✅ Номер {phone} сохранён!\n"
        f"Регистрация завершена\n",
        reply_markup=kb.kb_main_menu)
    await state.clear()


@handlers.callback_query(F.data == "phone_change")
async def phone_change(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "✍️ Введите другой номер телефона:",
        reply_markup=ReplyKeyboardRemove())
    await state.set_state(Reg.phone)


@handlers.message(Command('main_menu'))
async def cmd_menu(message: Message):
    await message.answer("Выберите интересующий Вас пункт меню", reply_markup=kb.kb_main_menu)



@handlers.callback_query(F.data == 'main_menu')
async def cmd_main_menu(callback: CallbackQuery):
    await callback.message.edit_text("Выберите интересующий Вас пункт меню", reply_markup=kb.kb_main_menu)


@handlers.callback_query(F.data == 'useful_links')
async def cmd_useful_links(callback: CallbackQuery):
    await callback.message.edit_text("Выберите интересующую Вас ссылку:", reply_markup=kb.kb_urls)

@handlers.callback_query(F.data == 'duration_session')
async def duration_session(callback: CallbackQuery):
    rows = await db.pool.fetch('''
    SELECT name, start_date, end_date FROM session_periods ORDER BY start_date DESC''')

    if not rows:
        await callback.message.edit_text("❌ Данные о сессиях отсутствуют.", reply_markup=kb.back_stud_menu)
        return
    text = "📅 Даты проведения сессий:\n\n"
    for row in rows:
        name = row['name']
        start_date = row[1]
        end_date = row[2]

        text += f"🔹 {name}: {start_date} — {end_date}\n"
    await callback.message.edit_text(text, reply_markup=kb.back_stud_menu)


@handlers.callback_query(F.data == 'deadlines_info')
async def deadlines_info(callback: CallbackQuery):
    rows = await db.pool.fetch('''
    SELECT subject_name, deadline_date, description FROM deadlines ORDER BY subject_name DESC''')
    if not rows:
        await callback.message.answer("❌ Данные о установленных сроках отсутствуют", reply_markup=kb.back_stud_menu)
        return
    text = "Поставленные задачи и сроки их выполнения:\n\n"
    for row in rows:
        name = row['subject_name']
        deadline_date = row['deadline_date']
        description = row['description']

        text += (f"🔹 {name}\n"
                 f"🪦 {deadline_date if deadline_date else '—'}\n"
                 f"📋 {description}\n\n")
    await callback.message.edit_text(text, reply_markup=kb.back_stud_menu)


# РАСПИСАНИЕ ЗВОНКОВ
@handlers.callback_query(F.data == 'call_schedule')
async def call_schedule(callback: CallbackQuery):
    await callback.message.edit_text("⏰ 1 пара: 8.30 -- 10.05\n"
                                     "⏰ 2 пара: 10.15 -- 11.50\n"
                                     "⏰ 3 пара: 12.35 -- 14.10\n"
                                     "⏰ 4 пара: 14.20 -- 15.55\n"
                                     "⏰ 5 пара: 16.05 -- 17.40\n"
                                     "⏰ 6 пара: 17.50 -- 19.25\n"
                                     "⏰ 7 пара: 19.35 -- 21.10\n"
                                     "☕ БОЛЬШОЙ ПЕРЕРЫВ: 11.50 -- 12.35", reply_markup=kb.back_stud_menu)


@handlers.callback_query(F.data == 'exam schedule')
async def exam_schedule(callback: CallbackQuery):
    rows = await db.pool.fetch('''
    SELECT certification, subject_name, exam_date, teacher_name FROM exams_schedule ORDER BY subject_name DESC''')
    if not rows:
        await callback.message.answer("❌ Данные по срокам сдачи экзаменов и зачетов отсутствуют", reply_markup=kb.back_stud_menu)
        return

    text = f"График проведения аттестаций: \n\n"
    for row in rows:
        certification = row['certification']
        name = row['subject_name']
        date = row['exam_date']
        t_name = row['teacher_name']

        text += (f"❗ {certification} -- 📅 {date}\n"
                 f"🔹 {name}\n" 
                 f"👨‍🏫 {t_name}\n\n")
    await callback.message.edit_text(text, reply_markup=kb.back_stud_menu)


@handlers.callback_query(F.data == 'teacher')
async def choose_subject(callback: CallbackQuery):
    rows = await db.pool.fetch("SELECT DISTINCT subject_name FROM teacher ORDER BY subject_name ASC")

    if not rows:
        await callback.message.answer("❌ В базе нет данных о преподавателях.", reply_markup=kb.back_stud_menu)
        return

    kb_teacher = InlineKeyboardBuilder()
    for row in rows:
        kb_teacher.button(text=row["subject_name"], callback_data=f"subject_{row['subject_name']}")
        kb_teacher.adjust(2)

    await callback.message.answer("Выбери предмет:", reply_markup=kb_teacher.as_markup())

@handlers.callback_query(F.data.startswith("subject_"))
async def show_teacher(callback: CallbackQuery):
    subject = callback.data.replace("subject_", "")

    rows = await db.pool.fetch(
        "SELECT teacher_name FROM teacher WHERE subject_name = $1",
        subject
        )

    if not rows:
        await callback.message.edit_text(f"❌ Нет данных по предмету: {subject}",reply_markup=kb.back_stud_menu)
        return

    text = f"👩‍🏫 Преподаватель по предмету *{subject}:*\n\n"
    for row in rows:
        text += f" {row['teacher_name']}"
    await callback.message.edit_text(text,reply_markup=kb.back_stud_menu, parse_mode="Markdown")


@handlers.callback_query(F.data == 'lesson_schedule')
async def lesson_schedule(callback: CallbackQuery):
    rows = await db.pool.fetch('''
    SELECT DISTINCT day_of_week FROM schedule ORDER BY day_of_week ASC''')

    if not rows:
        await callback.message.answer("❌ Данные о расписании не найдены", reply_markup=kb.back_stud_menu)
        return

    kb_schedule = InlineKeyboardBuilder()
    for row in rows:
        kb_schedule.button(text=row['day_of_week'], callback_data=f"day_{row['day_of_week']}")
        kb_schedule.adjust(2)
    await callback.message.answer("Выбери дату:", reply_markup=kb_schedule.as_markup())


@handlers.callback_query(F.data.startswith("day_"))
async def show_schedule(callback: CallbackQuery):
    day = callback.data.replace('day_', '')

    rows = await db.pool.fetch(
        '''SELECT num_subject, subject_name, room_number FROM schedule WHERE day_of_week = $1''', day)

    if not rows:
        await callback.message.edit_text(f"❌ Нет данных по расписанию на {day}", reply_markup=kb.back_stud_menu)
        return

    text = f"Расписание на *{day}:*\n\n"
    for row in rows:
        text += f"{row['num_subject']}. {row['subject_name']} - {row['room_number']} аудитория\n\n"
        await callback.message.edit_text(text, reply_markup=kb.back_stud_menu, parse_mode="Markdown")





