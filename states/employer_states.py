# states/employer_states.py
from aiogram.fsm.state import State, StatesGroup

class EmployerStates(StatesGroup):
    name = State()
    company = State()
    age = State()
    gender = State()
    experience = State()
    category = State()
    work_days = State()
    work_hours = State()
    location = State()
    salary = State()
    requirements = State()
    confirm = State()
    edit = State()
    edit_field = State() 