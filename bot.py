import asyncio
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID, START_MSG, ABOUT_MSG, PRICE_MSG
from database import Database
from satates import OrderForm, AdminAddService, AdminEditService, AdminDeleteService

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Ma'lumotlar
data = Database.load()


# ===== KLAVIATURALAR =====
def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menu"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="👥 Biz haqimizda")
    kb.button(text="🛠️ Xizmatlar")
    kb.button(text="💰 Narxlar")
    kb.button(text="📋 Buyurtma berish")
    kb.button(text="📞 Aloqa")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Admin paneli"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="➕ Xizmat qo'shish")
    kb.button(text="✏️ Xizmat tahrir")
    kb.button(text="❌ Xizmat o'chirish")
    kb.button(text="📊 Buyurtmalar")
    kb.button(text="🔙 Orqaga")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


# ===== BOSHLASH =====
@router.message(Command("start"))
async def start_handler(message: types.Message):
    """Start komandasi"""
    if message.from_user.id == ADMIN_ID:
        await message.answer("👋 Admin Paneliga xush kelibsiz!", reply_markup=get_admin_keyboard())
    else:
        await message.answer(START_MSG, reply_markup=get_main_keyboard(), parse_mode="Markdown")


# ===== USER MENYU =====
@router.message(F.text == "👥 Biz haqimizda")
async def about_handler(message: types.Message):
    """Biz haqimizda"""
    await message.answer(ABOUT_MSG, reply_markup=get_main_keyboard(), parse_mode="Markdown")


@router.message(F.text == "🛠️ Xizmatlar")
async def services_handler(message: types.Message):
    """Xizmatlar"""
    data = Database.load()
    services = Database.get_services(data)
    
    if not services:
        text = "🛠️ **Xizmatlar**\n\nHozircha xizmat yo'q"
    else:
        text = "🛠️ **Bizning Xizmatlar:**\n\n"
        for service in services:
            text += f"🔸 **{service['name']}**\n{service['description']}\n\n"
    
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="Markdown")


@router.message(F.text == "💰 Narxlar")
async def prices_handler(message: types.Message):
    """Narxlar"""
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Buyurtma berish", callback_data="order_start")
    kb.adjust(1)
    
    await message.answer(PRICE_MSG, reply_markup=kb.as_markup(), parse_mode="Markdown")


@router.message(F.text == "📞 Aloqa")
async def contact_handler(message: types.Message):
    """Aloqa"""
    data = Database.load()
    contacts = Database.get_contacts(data)
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💬 Telegram", url=contacts["telegram"])
    kb.button(text="📞 Qo'ng'iroq", url=f"tel:{contacts['phone']}")
    kb.button(text="✉️ Email", url=f"mailto:{contacts['email']}")
    kb.adjust(1)
    
    text = (
        f"📞 **Bizning Kontaktlar:**\n\n"
        f"💬 Telegram: {contacts['telegram']}\n"
        f"☎️ Telefon: {contacts['phone']}\n"
        f"✉️ Email: {contacts['email']}"
    )
    
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")


# ===== BUYURTMA FORMASI =====
@router.callback_query(F.data == "order_start")
async def order_start(callback: types.CallbackQuery, state: FSMContext):
    """Buyurtma formasini boshlash"""
    await callback.message.answer(
        "📋 **Buyurtma Forması**\n\n1️⃣ Ismingizni yozing:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await callback.answer()
    await state.set_state(OrderForm.waiting_for_name)


@router.message(OrderForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Ismni saqlash"""
    await state.update_data(name=message.text)
    await message.answer("2️⃣ Telefon raqamingizni yozing (+998...):")
    await state.set_state(OrderForm.waiting_for_phone)


@router.message(OrderForm.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    """Telefon raqamni saqlash"""
    await state.update_data(phone=message.text)
    
    data = Database.load()
    services = Database.get_services(data)
    
    if not services:
        await message.answer("❌ Hozircha xizmat yo'q. Iltimos, keyinroq urinib ko'ring.")
        await state.clear()
        return
    
    kb = InlineKeyboardBuilder()
    for service in services:
        kb.button(text=f"🔹 {service['name']}", callback_data=f"service_{service['id']}")
    kb.adjust(1)
    
    await message.answer("3️⃣ Qaysi xizmatga ehtiyoj bor?", reply_markup=kb.as_markup())
    await state.set_state(OrderForm.waiting_for_service)


@router.callback_query(OrderForm.waiting_for_service)
async def process_service(callback: types.CallbackQuery, state: FSMContext):
    """Xizmatni tanlash"""
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)
    await callback.message.answer("4️⃣ Loyihaning qisqa tavsifini yozing:")
    await callback.answer()
    await state.set_state(OrderForm.waiting_for_task)


@router.message(OrderForm.waiting_for_task)
async def process_task(message: types.Message, state: FSMContext):
    """Tavsifni saqlash va buyurtmani yakunlash"""
    order_data = await state.get_data()
    await state.clear()
    
    # Buyurtmani saqla
    data = Database.load()
    order = Database.add_order(
        data,
        order_data["name"],
        order_data["phone"],
        order_data["service_id"],
        message.text,
        message.from_user.id
    )
    
    # Xizmat nomini topish
    service_name = "Noma'lum"
    for service in data["services"]:
        if service["id"] == order_data["service_id"]:
            service_name = service["name"]
            break
    
    # Foydalanuvchiga javob
    confirm_text = (
        f"✅ **Buyurtma Qabul Qilindi!**\n\n"
        f"🆔 Buyurtma #: {order['id']}\n"
        f"👤 Ism: {order['name']}\n"
        f"📞 Telefon: {order['phone']}\n"
        f"🛠️ Xizmat: {service_name}\n"
        f"📝 Tavsif: {order['task']}\n"
        f"📅 Sana: {order['date']}\n\n"
        f"Tez orada biz siz bilan bog'lanamiz! 😊"
    )
    await message.answer(confirm_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    
    # KANALGA YUBORISH
    if CHANNEL_ID:
        channel_text = (
            f"📨 **YANGI BUYURTMA** #{order['id']}\n\n"
            f"👤 Ism: {order['name']}\n"
            f"📞 Telefon: {order['phone']}\n"
            f"🛠️ Xizmat: {service_name}\n"
            f"📝 Tavsif: {order['task']}\n"
            f"📅 Sana: {order['date']}"
        )
        try:
            await bot.send_message(CHANNEL_ID, channel_text, parse_mode="Markdown")
        except Exception as e:
            print(f"Kanal xatosi: {e}")


# ===== ADMIN XIZMATLAR =====
@router.message(F.text == "📊 Buyurtmalar")
async def admin_orders(message: types.Message):
    """Barcha buyurtmalar"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q!")
        return
    
    data = Database.load()
    orders = Database.get_orders(data)
    
    if not orders:
        await message.answer("📊 Hozircha buyurtma yo'q", reply_markup=get_admin_keyboard())
        return
    
    text = "📊 **BARCHA BUYURTMALAR:**\n\n"
    for order in orders:
        # Xizmat nomini topish
        service_name = "Noma'lum"
        for service in data["services"]:
            if service["id"] == order["service_id"]:
                service_name = service["name"]
                break
        
        text += (
            f"🆔 #{order['id']} | {order['status']}\n"
            f"👤 {order['name']} | {order['phone']}\n"
            f"🛠️ {service_name}\n"
            f"📝 {order['task']}\n"
            f"📅 {order['date']}\n"
            f"─────────────────\n"
        )
    
    await message.answer(text, reply_markup=get_admin_keyboard())


@router.message(F.text == "➕ Xizmat qo'shish")
async def admin_add_service(message: types.Message, state: FSMContext):
    """Xizmat qo'shish"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q!")
        return
    
    await message.answer("📌 Xizmat nomini yozing:")
    await state.set_state(AdminAddService.waiting_for_name)


@router.message(AdminAddService.waiting_for_name)
async def add_service_name(message: types.Message, state: FSMContext):
    """Xizmat nomi"""
    await state.update_data(name=message.text)
    await message.answer("📝 Xizmat tavsifini yozing:")
    await state.set_state(AdminAddService.waiting_for_description)


@router.message(AdminAddService.waiting_for_description)
async def add_service_desc(message: types.Message, state: FSMContext):
    """Xizmat tavsifi"""
    service_data = await state.get_data()
    await state.clear()
    
    data = Database.load()
    service = Database.add_service(data, service_data["name"], message.text)
    
    await message.answer(
        f"✅ Xizmat qo'shildi!\n\n🔸 {service['name']}\n{service['description']}",
        reply_markup=get_admin_keyboard()
    )


@router.message(F.text == "✏️ Xizmat tahrir")
async def admin_edit_service_list(message: types.Message, state: FSMContext):
    """Xizmatni tahrir qilish uchun ro'yxat"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q!")
        return
    
    data = Database.load()
    services = Database.get_services(data)
    
    if not services:
        await message.answer("🛠️ Xizmat yo'q", reply_markup=get_admin_keyboard())
        return
    
    text = "Qaysi xizmatni tahrir qilish kerak?\n\n"
    kb = InlineKeyboardBuilder()
    
    for service in services:
        text += f"• {service['name']}\n"
        kb.button(text=f"✏️ {service['name']}", callback_data=f"edit_service_{service['id']}")
    
    kb.adjust(1)
    await message.answer(text, reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("edit_service_"))
async def edit_service_select(callback: types.CallbackQuery, state: FSMContext):
    """Tahrir qilish xizmatni tanlash"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!")
        return
    
    service_id = int(callback.data.split("_")[2])
    await state.update_data(service_id=service_id)
    await callback.message.answer("📌 Yangi xizmat nomini yozing:")
    await callback.answer()
    await state.set_state(AdminEditService.waiting_for_name)


@router.message(AdminEditService.waiting_for_name)
async def edit_service_name(message: types.Message, state: FSMContext):
    """Xizmat nomini tahrir"""
    await state.update_data(name=message.text)
    await message.answer("📝 Yangi xizmat tavsifini yozing:")
    await state.set_state(AdminEditService.waiting_for_description)


@router.message(AdminEditService.waiting_for_description)
async def edit_service_desc(message: types.Message, state: FSMContext):
    """Xizmat tavsifini tahrir"""
    service_data = await state.get_data()
    await state.clear()
    
    data = Database.load()
    service = Database.update_service(data, service_data["service_id"], service_data["name"], message.text)
    
    await message.answer(
        f"✅ Xizmat yangilandi!\n\n🔸 {service['name']}\n{service['description']}",
        reply_markup=get_admin_keyboard()
    )


@router.message(F.text == "❌ Xizmat o'chirish")
async def admin_delete_service_list(message: types.Message, state: FSMContext):
    """Xizmatni o'chirish uchun ro'yxat"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Ruxsat yo'q!")
        return
    
    data = Database.load()
    services = Database.get_services(data)
    
    if not services:
        await message.answer("🛠️ Xizmat yo'q", reply_markup=get_admin_keyboard())
        return
    
    text = "Qaysi xizmatni o'chirish kerak?\n\n"
    kb = InlineKeyboardBuilder()
    
    for service in services:
        text += f"• {service['name']}\n"
        kb.button(text=f"❌ {service['name']}", callback_data=f"delete_service_{service['id']}")
    
    kb.adjust(1)
    await message.answer(text, reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("delete_service_"))
async def delete_service(callback: types.CallbackQuery):
    """Xizmatni o'chirish"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!")
        return
    
    service_id = int(callback.data.split("_")[2])
    data = Database.load()
    Database.delete_service(data, service_id)
    
    await callback.message.edit_text("✅ Xizmat o'chirildi!")
    await callback.answer()


@router.message(F.text == "🔙 Orqaga")
async def go_back(message: types.Message):
    """Orqaga"""
    if message.from_user.id == ADMIN_ID:
        await message.answer("👋 Admin Paneli", reply_markup=get_admin_keyboard())
    else:
        await message.answer("👋 Asosiy Menyu", reply_markup=get_main_keyboard())


@router.message()
async def unknown_handler(message: types.Message):
    """Noma'lum buyruq"""
    if message.from_user.id == ADMIN_ID:
        await message.answer("❌ Noto'g'ri buyruq!", reply_markup=get_admin_keyboard())
    else:
        await message.answer("❌ Bunday buyruq tanmayapman!", reply_markup=get_main_keyboard())


# ===== BOT ISHGA TUSHISH =====
async def main():
    """Botni ishga tushirish"""
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())