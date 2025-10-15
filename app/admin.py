from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import os


import app.keyboards as kb

from app.state import SessionPeriods, Deadlines, ExamCshedule, TeacherInfo, ScheduleInfo
from app.database.models import db


load_dotenv()
admin = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
HEADMAN_ID = int(os.getenv("HEADMAN_ID", 0))

admin_ids = [ADMIN_ID, HEADMAN_ID ]

async def is_admin(user_id: int) -> bool:
    return user_id in admin_ids

@admin.message(Command('admin'))
async def admin_(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещен.", reply_markup=kb.kb_main_menu)
        return
    await message.answer("Панель администратора.\nВыберите действие:",
        reply_markup=kb.kb_admin)


@admin.callback_query(F.data == 'admin')
async def admin_panel(callback: CallbackQuery):
    await callback.message.answer("Панель администратора.\nВыберите действие:",
        reply_markup=kb.kb_admin)


@admin.message(Command('admin_panel'))
async def full_admin(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещен.", reply_markup=kb.kb_main_menu)
        return
    await message.answer("Выберите действие:\n",
                         reply_markup=kb.full_admin)


@admin.callback_query(F.data == 'admin_panel')
async def back_full_admin_menu(callback: CallbackQuery):
    await callback.message.answer("Выберите действие:\n",
                         reply_markup=kb.full_admin)



# ВВОД ДАННЫХ О СРОКАХ СЕССИИ
@admin.callback_query(F.data == 'session_name')
async def session_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите название семестра:")
    await state.set_state(SessionPeriods.waiting_for_name)


@admin.message(SessionPeriods.waiting_for_name)
async def save_session_name(message: Message, state: FSMContext):
    await state.update_data(session_name=message.text)
    await state.set_state(SessionPeriods.waiting_for_start_date)
    await message.answer("Введите дату начала сессии:")

@admin.message(SessionPeriods.waiting_for_start_date)
async def start_date(message: Message, state: FSMContext):
    await state.update_data(start_date=message.text)
    await state.set_state(SessionPeriods.waiting_for_end_date)
    await message.answer("Введите дату окончания сессии:")


@admin.message(SessionPeriods.waiting_for_end_date)
async def end_date(message: Message, state: FSMContext):
    await state.update_data(end_date=message.text)
    data = await state.get_data()

    await db.pool.fetchrow('''
        INSERT INTO session_periods (name, start_date, end_date)
        VALUES ($1,$2, $3) ON CONFLICT (id) DO NOTHING
        ''', data['session_name'],
            data['start_date'],
            data['end_date'])

    await message.answer("✅ Данные о сроках проведения сессии внесены", reply_markup=kb.back_admin_menu)
    await state.clear()



# ВВОД ДАННЫХ О ДЭДЛАЙНАХ
@admin.callback_query(F.data == 'dead_lines')
async def subject_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите данные о поставленной задаче:")
    await state.set_state(Deadlines.waiting_for_subject_name)

@admin.message(Deadlines.waiting_for_subject_name)
async def save_subject_name(message: Message, state: FSMContext):
    subject_name = message.text
    await state.update_data(subject_name=subject_name)
    await state.set_state(Deadlines.waiting_for_deadline_date)
    await message.answer("Введите сроки сдачи задания:")

@admin.message(Deadlines.waiting_for_deadline_date)
async def deadline_date(message: Message, state: FSMContext):
    await state.update_data(deadline_date=message.text)
    await state.set_state(Deadlines.waiting_for_description)
    await message.answer("Введите описание поставленной задачи:")

@admin.message(Deadlines.waiting_for_description)
async def description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()

    await db.pool.fetchrow('''
    INSERT INTO deadlines (subject_name, deadline_date, description)
    VALUES ($1, $2, $3) ON CONFLICT (id) DO NOTHING''',
    data['subject_name'],
    data['deadline_date'],
    data['description'])

    await message.answer("✅ Данные о поставленных задач сохранены", reply_markup=kb.back_admin_menu)
    await state.clear()


# ВВОД ДАННЫХ О ДАТАХ ЗАЧЕТОВ И ЭКЗАМЕНОВ
@admin.callback_query(F.data == 'certification')
async def add_certification(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите вид аттестации:")
    await state.set_state(ExamCshedule.waiting_for_certification)

@admin.message(ExamCshedule.waiting_for_certification)
async def add_exam_schedule(message: Message, state: FSMContext):
    await state.update_data(certification=message.text)
    await message.answer("Введите название учебного предмета:")
    await state.set_state(ExamCshedule.waiting_for_subject_name)

@admin.message(ExamCshedule.waiting_for_subject_name)
async def edit_subject_name(message: Message, state: FSMContext):
    await state.update_data(subject_name=message.text)
    await state.set_state(ExamCshedule.waiting_for_exam_date)
    await message.answer("Введите дату проведения аттестации:")

@admin.message(ExamCshedule.waiting_for_exam_date)
async def edit_exam_date(message: Message, state: FSMContext):
    await state.update_data(exam_date=message.text)
    await state.set_state(ExamCshedule.waining_for_teacher_name)
    await message.answer("Введите ФИО преподавателя:")

@admin.message(ExamCshedule.waining_for_teacher_name)
async def edit_teacher_name(message: Message, state: FSMContext):
    await state.update_data(teacher_name=message.text)
    await state.set_state()

    data = await state.get_data()
    await db.pool.fetchrow('''
    INSERT INTO exams_schedule (certification, subject_name, exam_date, teacher_name)
    VALUES ($1, $2, $3, $4)''',
    data['certification'],
    data['subject_name'],
    data['exam_date'],
    data['teacher_name'])

    await message.answer("✅ Данные успешно сохранены", reply_markup=kb.back_admin_menu)
    await state.clear()


# ВВОД ДАННЫХ О ФИО ПРЕПОДАВАТЕЛЯ И ПРЕДМЕТЕ
@admin.callback_query(F.data == 'teacher_info')
async def teacher_info(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите название название учебной дисциплины:")
    await state.set_state(TeacherInfo.waiting_for_subject_name)

@admin.message(TeacherInfo.waiting_for_subject_name)
async def subject_name(message: Message, state: FSMContext):
    await state.update_data(subject_name=message.text)
    await message.answer("Введите ФИО преподавателя:")
    await state.set_state(TeacherInfo.waiting_for_teacher_name)

@admin.message(TeacherInfo.waiting_for_teacher_name)
async def teacher_name(message: Message, state: FSMContext):
    await state.update_data(teacher_name=message.text)
    data = await state.get_data()

    await db.pool.fetchrow('''
    INSERT INTO teacher (subject_name, teacher_name)
    VALUES ($1, $2)''',
    data['subject_name'],
    data['teacher_name'])

    await message.answer("✅ Данные успешно сохранены", reply_markup=kb.back_admin_menu)
    await state.clear()


# ВВОД ДАННЫХ О РАСПИСАНИИ
@admin.callback_query(F.data == 'add_schedule')
async def add_schedule(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите дату:")
    await state.set_state(ScheduleInfo.waiting_for_day_of_week)

@admin.message(ScheduleInfo.waiting_for_day_of_week)
async def save_day(message: Message, state: FSMContext):
    await state.update_data(day_of_week=message.text)
    await message.answer("Введите номер занятия(пары):")
    await state.set_state(ScheduleInfo.waiting_for_num_subject)

@admin.message(ScheduleInfo.waiting_for_num_subject)
async def save_num_subject(message: Message, state: FSMContext):
    await state.update_data(num_subject=message.text)
    await message.answer("Введите название учебного предмета:")
    await state.set_state(ScheduleInfo.waiting_for_subject_name)

@admin.message(ScheduleInfo.waiting_for_subject_name)
async def save_subject_name(message: Message, state: FSMContext):
    await state.update_data(subject_name=message.text)
    await message.answer("введите номер аудитории в которой будет проходить занятие:")
    await state.set_state(ScheduleInfo.waiting_for_room_number)

@admin.message(ScheduleInfo.waiting_for_room_number)
async def save_room_number(message: Message, state: FSMContext):
    await state.update_data(room_number=message.text)

    data = await state.get_data()

    await db.pool.fetchrow('''
    INSERT INTO schedule (day_of_week, num_subject, subject_name, room_number) VALUES ($1, $2, $3, $4)''',
                           data['day_of_week'],
                           data['num_subject'],
                           data['subject_name'],
                           data['room_number'])
    await message.answer("✅ Данные успешно сохранены", reply_markup=kb.edit_schedule)
    await state.clear()