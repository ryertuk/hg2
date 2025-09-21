# app/ui/invoices/invoice_line_model.py
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from app.services.item_service import ItemService
from app.services.unit_service import UnitService
from app.utils.price_calculator import calculate_line_total

class InvoiceLineTableModel(QAbstractTableModel):
    def __init__(self, lines_data):
        super().__init__()
        self.lines_data = lines_data
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
            if col == 0:  # item_id
                if isinstance(value, int) and 0 <= value < len(self.items):
                    item = self.items[value]
                    self.lines_data[row]['item_id'] = item.id
                    # ✅ واحد پایه کالا به صورت خودکار تنظیم می‌شود
                    unit = next((u for u in self.units if u.id == item.base_unit_id), None)
                    if unit:
                        self.lines_data[row]['unit_id'] = unit.id
                    self.recalculate_line_total(row)
                elif isinstance(value, str):  # از طریق جستجو
                    selected_item = None
                    for item in self.items:
                        if f"{item.name} ({item.sku})" == value:
                            selected_item = item
                            break
                    if selected_item:
                        self.lines_data[row]['item_id'] = selected_item.id
                        unit = next((u for u in self.units if u.id == selected_item.base_unit_id), None)
                        if unit:
                            self.lines_data[row]['unit_id'] = unit.id
                        self.recalculate_line_total(row)
                    else:
                        self.lines_data[row]['item_id'] = None
                        self.lines_data[row]['unit_id'] = None
            elif col == 1:  # qty
                try:
                    self.lines_data[row]['qty'] = float(value)
                    self.recalculate_line_total(row)
                except ValueError:
                    return False
            elif col == 2:  # unit_id
                if isinstance(value, int) and 0 <= value < len(self.units):
                    self.lines_data[row]['unit_id'] = self.units[value].id
            elif col == 3:  # unit_price
                try:
                    clean_value = str(value).replace(',', '')
                    self.lines_data[row]['unit_price'] = int(float(clean_value))
                    self.recalculate_line_total(row)
                except ValueError:
                    return False
            elif col == 5:  # discount
                try:
                    clean_value = str(value).replace(',', '')
                    self.lines_data[row]['discount'] = int(float(clean_value))
                except ValueError:
                    return False
            elif col == 6:  # tax
                try:
                    clean_value = str(value).replace(',', '')
                    self.lines_data[row]['tax'] = int(float(clean_value))
                except ValueError:
                    return False
            elif col == 7:  # notes
                self.lines_data[row]['notes'] = str(value)

            self.dataChanged.emit(index, index)
            return True
        return False

    def recalculate_line_total(self, row):
        """محاسبه مجدد مبلغ کل خط فاکتور — با در نظر گرفتن نوع کالا"""
        line = self.lines_data[row]
        item_id = line.get('item_id')
        if not item_id:
            line['line_total'] = 0
            return

        item = next((i for i in self.items if i.id == item_id), None)
        if not item:
            line['line_total'] = 0
            return

        qty = line.get('qty', 0)
        unit_price = line.get('unit_price', 0)

        try:
            line_total = calculate_line_total(
                item=item,
                qty=qty,
                unit_price=unit_price,
                length=item.length if item.unit_type == "measure" else None,
                width=item.width if item.unit_type == "measure" else None
            )
            line['line_total'] = line_total
        except Exception as e:
            print(f"خطا در محاسبه line_total: {e}")
            line['line_total'] = 0

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
        self.beginInsertRows(QModelIndex(), len(self.lines_data), len(self.lines_data))
        self.lines_data.append(new_line)
        self.endInsertRows()

    def remove_line(self, row):
        """حذف یک خط"""
        if 0 <= row < len(self.lines_data):
            self.beginRemoveRows(QModelIndex(), row, row)
            self.lines_data.pop(row)
            self.endRemoveRows()