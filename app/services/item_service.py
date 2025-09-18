# app/services/item_service.py
from app.database import SessionLocal
from app.models.item import Item

class ItemService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_items(self):
        return self.db.query(Item).all()

    def create_item(self, data):
        item = Item(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item_id, data):
        item = self.db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise Exception("کالا یافت نشد.")
        for key, value in data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item_id):
        item = self.db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise Exception("کالا یافت نشد.")
        self.db.delete(item)
        self.db.commit()