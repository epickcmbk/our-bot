from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    """Buyurtma formasining holatlari"""
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_service = State()
    waiting_for_task = State()


class AdminAddService(StatesGroup):
    """Xizmat qo'shish"""
    waiting_for_name = State()
    waiting_for_description = State()


class AdminEditService(StatesGroup):
    """Xizmat tahrir"""
    choosing_service = State()
    waiting_for_name = State()
    waiting_for_description = State()


class AdminDeleteService(StatesGroup):
    """Xizmat o'chirish"""
    choosing_service = State()