# app/ui/stock/stock_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableView, QLineEdit, QLabel, QMessageBox, QHeaderView, QInputDialog)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from app.services.stock_service import StockService
from app.services.item_service import ItemService
from app.services.unit_service import UnitService

class StockTableModel(QAbstractTableModel):
    def __init__(self, items_with_stock):
        super().__init__()
        self.items = items_with_stock
        self.headers = ["کد کالا", "نام کالا", "واحد", "موجودی", "آخرین قیمت", "ارزش کل"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        item, stock, last_cost = self.items[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return item.sku
            elif col == 1: return item.name
            elif col == 2: return item.unit.name if hasattr(item, 'unit') else "نامشخص"  # ✅ واحد واقعی!
            elif col == 3: return f"{stock:.4f}"
            elif col == 4: return f"{last_cost:,.0f}" if last_cost else "-"
            elif col == 5: return f"{int(stock * last_cost):,.0f}" if last_cost else "-"
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class StockView(QWidget):
    def __init__(self):
        super().__init__()
        self.stock_service = StockService()
        self.item_service = ItemService()
        self.unit_service = UnitService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("📊 موجودی انبار")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("جستجو:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_data)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.adjust_btn = QPushButton("⚖️ تعدیل موجودی")
        self.adjust_btn.clicked.connect(self.adjust_stock)
        
        self.refresh_btn = QPushButton("🔄 تازه‌سازی")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.adjust_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        # بارگذاری کالاها + موجودی + آخرین قیمت
        all_items = self.item_service.get_all_items()
        items_with_stock = []

        for item in all_items:
            # ✅ بارگذاری واحد مرتبط — JOIN معادل
            unit = self.unit_service.get_unit_by_id(item.base_unit_id)
            item.unit = unit  # attach for display

            stock = self.stock_service.get_current_stock(item.id)
            
            # آخرین قیمت — آخرین تحرک ورودی
            last_movement = self.stock_service.get_movements_by_item(item.id)
            last_cost = None
            if last_movement:
                # آخرین تحرک ورودی را پیدا کن
                for m in reversed(last_movement):
                    if m.qty > 0:  # ورودی
                        last_cost = m.cost_per_unit
                        break

            items_with_stock.append((item, stock, last_cost))

        self.items = items_with_stock
        self.model = StockTableModel(self.items)
        self.table.setModel(self.model)
        
        # تنظیم عرض ستون‌ها
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # نام کالا

    def filter_data(self):
        text = self.search_input.text().lower()
        filtered = [
            (item, stock, cost) for item, stock, cost in self.items
            if text in item.sku.lower() or text in item.name.lower()
        ]
        self.model.items = filtered
        self.model.layoutChanged.emit()

    def adjust_stock(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "هشدار", "لطفاً یک کالا را انتخاب کنید.")
            return
        row = selected[0].row()
        item, current_stock, last_cost = self.items[row]
        
        # تبدیل current_stock به float
        current_stock_float = float(current_stock)
        
        # ایجاد دیالوگ تعدیل
        new_qty, ok = QInputDialog.getDouble(
            self,
            "تعدیل موجودی",
            f"موجودی فعلی: {current_stock}\nموجودی جدید را وارد کنید:",
            current_stock_float,  # استفاده از مقدار float
            0,
            999999,
            4
        )
        if not ok:
            return
        
        # محاسبه تفاوت - هر دو float هستند
        adjustment_qty = new_qty - current_stock_float
        if adjustment_qty == 0:
            QMessageBox.information(self, "اطلاع", "تغییری اعمال نشد.")
            return
        
        # دریافت واحد و قیمت
        unit_id = item.base_unit_id
        cost_per_unit = float(last_cost) if last_cost else 0.0  # تبدیل به float
        
        try:
            # ✅ ایجاد تحرک تعدیل
            from app.services.stock_service import StockService
            stock_service = StockService()
            movement_data = {
                "item_id": item.id,
                "qty": adjustment_qty,
                "unit_id": unit_id,
                "movement_type": "adjustment",
                "reference_type": "manual",
                "reference_id": None,
                "cost_per_unit": cost_per_unit,
            }
            stock_service.add_movement(movement_data)
            QMessageBox.information(self, "موفق", "موجودی با موفقیت تعدیل شد.")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تعدیل موجودی: {str(e)}")