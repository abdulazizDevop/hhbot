"""Graduate states"""
from aiogram.fsm.state import State, StatesGroup


class GraduateStates(StatesGroup):
    """Graduate ad creation states"""
    name = State()
    age = State()
    technologies = State()
    contact = State()
    region = State()
    price = State()
    profession = State()
    contact_time = State()
    goal = State()
    resume = State()
    confirm = State()
    edit = State()
    edit_field = State()