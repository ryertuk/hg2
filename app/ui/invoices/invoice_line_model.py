# app/ui/invoices/invoice_line_model.py
from PySide6.QtCore import QAbstractTableModel, Qt
from app.services.item_service import ItemService
from app.services.unit_service import UnitService

class InvoiceLineTableModel(QAbstractTableModel):
    def __init__(self, lines_data):
        super().__init__()
        self.lines_data = lines_data  # لیست دیکشنری‌ها — داده‌های خطوط فاکتور
        self.item_service = ItemService()
        self.unit_service = UnitService()
        self.items = self.item_service.get_all_items()
        self.units = self.unit_service.get_all_units()
        self.headers = ["کالا", "تعداد", "واحد", "قیمت واحد", "مبلغ کل", "تخفیف", "مالیات", "یادداشت"]

    def rowCount(self, parent=None):
        return len(self.lines_data)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        line = self.lines_data[row]

        if role == Qt.DisplayRole:
            if col == 0:
                item_id = line.get('item_id')
                if item_id:
                    item = next((i for i in self.items if i.id == item_id), None)
                    return item.name if item else ""
                return ""
            elif col == 1:
                return str(line.get('qty', 0))
            elif col == 2:
                unit_id = line.get('unit_id')
                if unit_id:
                    unit = next((u for u in self.units if u.id == unit_id), None)
                    return unit.name if unit else ""
                return ""
            elif col == 3:
                return f"{int(line.get('unit_price', 0)):,}"
            elif col == 4:
                return f"{int(line.get('line_total', 0)):,}"
            elif col == 5:
                return f"{int(line.get('discount', 0)):,}"
            elif col == 6:
                return f"{int(line.get('tax', 0)):,}"
            elif col == 7:
                return line.get('notes', '')
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            col = index.column()
            if col == 0:  # item_id — از ایندکس ComboBox
                self.lines_data[row]['item_id'] = self.items[value].id
                # بروزرسانی واحد پایه کالا
                item = self.items[value]
                base_unit = next((u for u in self.units if u.id == item.base_unit_id), None)
                if base_unit:
                    self.lines_data[row]['unit_id'] = base_unit.id
            elif col == 1:
                self.lines_data[row]['qty'] = float(value)
            elif col == 2:
                self.lines_data[row]['unit_id'] = self.units[value].id
            elif col == 3:
                self.lines_data[row]['unit_price'] = int(value.replace(',', ''))
            # محاسبه مجدد line_total
            self.recalculate_line_total(row)
            self.dataChanged.emit(index, index)
            return True
        return False

    def recalculate_line_total(self, row):
        """محاسبه مجدد مبلغ کل خط فاکتور — با در نظر گرفتن نوع کالا"""
        line = self.lines_data[row]
        item_id = line.get('item_id')
        if not item_id:
            return
        item = next((i for i in self.items if i.id == item_id), None)
        if not item:
            return

        qty = line.get('qty', 0)
        unit_price = line.get('unit_price', 0)

        if item.unit_type == "measure" and item.length and item.width:
            area = item.length * item.width
            line_total = int(unit_price * area * qty)
        else:
            line_total = int(unit_price * qty)

        line['line_total'] = line_total

    def add_line(self):
        """افزودن یک خط خالی جدید"""
        new_line = {
            'item_id': None,
            'qty': 0.0,
            'unit_id': None,
            'unit_price': 0,
            'discount': 0,
            'tax': 0,
            'line_total': 0,
            'notes': ''
        }
        self.beginInsertRows(Qt.QModelIndex(), len(self.lines_data), len(self.lines_data))
        self.lines_data.append(new_line)
        self.endInsertRows()

    def remove_line(self, row):
        """حذف یک خط"""
        self.beginRemoveRows(Qt.QModelIndex(), row, row)
        self.lines_data.pop(row)
        self.endRemoveRows()