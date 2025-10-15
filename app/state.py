from aiogram.fsm.state import StatesGroup, State

class SessionPeriods(StatesGroup):
    waiting_for_name = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()


class Deadlines(StatesGroup):
    waiting_for_subject_name = State()
    waiting_for_deadline_date = State()
    waiting_for_description = State()


class ExamCshedule(StatesGroup):
    waiting_for_certification = State()
    waiting_for_subject_name = State()
    waiting_for_exam_date = State()
    waining_for_teacher_name = State()

class TeacherInfo(StatesGroup):
    waiting_for_subject_name = State()
    waiting_for_teacher_name = State()


class ScheduleInfo(StatesGroup):
    waiting_for_day_of_week = State()
    waiting_for_num_subject = State()
    waiting_for_subject_name = State()
    waiting_for_room_number = State()


class EditDateSession(StatesGroup):
    edit_name = State()
    edit_start_date = State()
    edit_end_date = State()


class EditDeadline(StatesGroup):
    waiting_for_edit_value = State()


class EditCertification(StatesGroup):
    edit_value = State()


class EditTeacher(StatesGroup):
    edit_teacher_value = State()


class EditSchedule(StatesGroup):
    edit_schedule = State()


class Reg(StatesGroup):
    name = State()
    phone = State()
