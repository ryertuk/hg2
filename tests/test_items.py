import pytest
from app.models.items import Item, ItemPydantic
from app.services.items_service import create_item, get_all_items
from app.services.units_service import create_unit

def test_create_item(test_session):
    # اول یک unit بساز
    create_unit({'code': 'm', 'name': 'Meter', 'factor_to_base': 1.0})
    data = {'sku': 'SKU001', 'name': 'Item1', 'unit_type': 'measure', 'base_unit_id': 1, 'barcode': '123456'}
    create_item(data)
    items = get_all_items()
    assert len(items) == 1
    assert items[0].sku == 'SKU001'

def test_validation_unit_type(test_session):
    with pytest.raises(ValueError):
        ItemPydantic(sku='SKU001', name='Test', unit_type='invalid', base_unit_id=1)