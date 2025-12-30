"""Admin states"""
from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Admin states"""
    waiting_category_name = State()
    waiting_category_edit = State()
    waiting_student_reply = State()

