import json
import os
from datetime import datetime
from config import DB_PATH


class Database:
    """Botning ma'lumotlarini boshqaruvchi klass"""
    
    @staticmethod
    def load():
        """Ma'lumotlarni yuklash"""
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        
        return {
            "services": [],
            "orders": [],
            "contacts": {
                "telegram": "https://t.me/devteamcontact",
                "phone": "+998 99 123 45 67",
                "email": "info@devteam.uz"
            }
        }
    
    @staticmethod
    def save(data):
        """Ma'lumotlarni saqlash"""
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ===== XIZMATLAR =====
    @staticmethod
    def add_service(data, name: str, description: str):
        """Yangi xizmat qo'shish"""
        service = {
            "id": len(data["services"]) + 1,
            "name": name,
            "description": description
        }
        data["services"].append(service)
        Database.save(data)
        return service
    
    @staticmethod
    def get_services(data):
        """Barcha xizmatlarni olish"""
        return data["services"]
    
    @staticmethod
    def delete_service(data, service_id: int):
        """Xizmatni o'chirish"""
        data["services"] = [s for s in data["services"] if s["id"] != service_id]
        Database.save(data)
    
    @staticmethod
    def update_service(data, service_id: int, name: str, description: str):
        """Xizmatni tahrir qilish"""
        for service in data["services"]:
            if service["id"] == service_id:
                service["name"] = name
                service["description"] = description
                Database.save(data)
                return service
        return None
    
    # ===== BUYURTMALAR =====
    @staticmethod
    def add_order(data, name: str, phone: str, service_id: int, task: str, user_id: int):
        """Yangi buyurtma qo'shish"""
        order = {
            "id": len(data["orders"]) + 1,
            "name": name,
            "phone": phone,
            "service_id": service_id,
            "task": task,
            "user_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "yangi"
        }
        data["orders"].append(order)
        Database.save(data)
        return order
    
    @staticmethod
    def get_orders(data):
        """Barcha buyurtmalarni olish"""
        return data["orders"]
    
    @staticmethod
    def get_order_by_id(data, order_id: int):
        """ID bo'yicha buyurtmani olish"""
        for order in data["orders"]:
            if order["id"] == order_id:
                return order
        return None
    
    # ===== KONTAKTLAR =====
    @staticmethod
    def update_contact(data, contact_type: str, value: str):
        """Kontaktni yangilash"""
        data["contacts"][contact_type] = value
        Database.save(data)
    
    @staticmethod
    def get_contacts(data):
        """Kontaktlarni olish"""
        return data["contacts"]