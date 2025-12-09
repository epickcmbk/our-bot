import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# DATABASE
DB_PATH = "bot_data.json"

# MESSAGES
START_MSG = """🚀 **Developer Team botiga xush kelibsiz!**

Biz professional dasturchi jamoasi bo'lib, web saytlar, 
mobil ilovalar, Telegram botlar va dizayn xizmatlarini taqdim etamiz.

Pastdagi menyu orqali biz haqimiz, xizmatlar va boshqa ma'lumotlarni 
bilib olishingiz mumkin. 😊"""

ABOUT_MSG = """👥 **Biz Haqimizda**

🎯 Biz 5+ yildan beri Uzbekistonda dasturiy ta'minot ishlab chiqish bo'ylab 
faoliyat olib vorbiyapman.

💪 Bizning jamoada:
• 10+ o'quvchi dasturchilar
• 3+ UI/UX dizaynerlar
• AWS, Google Cloud va Heroku kabi xizmatlardan foydalanuvchi

🏆 Yuzlagan mijozlar uchun muvaffaqiyatli loyihalarni yakunladik.
💼 E-commerce, logistika, SaaS sohalarda tajriba."""

PRICE_MSG = """💰 **Narxlar**

Narxlar loyiha murakkabligiga, o'lchamiga va vaqt jadvaliga qarab kelishiladi.

📌 **Taxminiy narxlar:**
• Landing page: 500,000 - 1,000,000 so'm
• Kichik web sayt: 2,000,000 - 5,000,000 so'm
• Murakkab web platforma: 10,000,000+ so'm
• Mobil ilova: 5,000,000 - 15,000,000 so'm
• Telegram bot: 1,000,000 - 3,000,000 so'm

📞 Aniq narx olish uchun buyurtma berish."""