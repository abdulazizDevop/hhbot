"""Student states"""
from aiogram.fsm.state import State, StatesGroup


class StudentStates(StatesGroup):
    """Student message states"""
    name = State()
    direction = State()
    group_number = State()
    type = State()
    message = State()
    confirm = State()

