import pytest
from app.models.units import Unit, UnitPydantic
from app.services.units_service import create_unit, get_all_units

def test_create_unit(test_session):
    data = {'code': 'pcs', 'name': 'Pieces', 'factor_to_base': 1.0}
    create_unit(data)
    units = get_all_units()
    assert len(units) == 1
    assert units[0].code == 'pcs'

def test_validation_factor(test_session):
    with pytest.raises(ValueError):
        UnitPydantic(code='m', name='Meter', factor_to_base=0.0)