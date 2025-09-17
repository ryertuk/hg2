import click
from app.utils.db import SessionLocal
from app.models.parties import Party

@click.command()
def seed_parties():
    with SessionLocal.begin() as session:
        parties = [
            Party(code='C001', name='Customer A', party_type='customer', credit_limit=5000.0),
            Party(code='S001', name='Supplier B', party_type='supplier', credit_limit=0.0),
            # 3 more...
            Party(code='C002', name='Customer C', party_type='both', credit_limit=10000.0),
            Party(code='S002', name='Supplier D', party_type='supplier', credit_limit=0.0),
            Party(code='C003', name='Customer E', party_type='customer', credit_limit=2000.0),
        ]
        session.add_all(parties)
    print("Seeded 5 parties.")

if __name__ == '__main__':
    seed_parties()
    
    
    
import click
from app.utils.db import SessionLocal
from app.models.parties import Party
from app.models.units import Unit
from app.models.items import Item

@click.command()
def seed_data():
    with SessionLocal.begin() as session:
        # Parties از مرحله 1
        parties = [
            Party(code='C001', name='Customer A', party_type='customer', credit_limit=5000.0),
            Party(code='S001', name='Supplier B', party_type='supplier', credit_limit=0.0),
            # 3 more...
            Party(code='C002', name='Customer C', party_type='both', credit_limit=10000.0),
            Party(code='S002', name='Supplier D', party_type='supplier', credit_limit=0.0),
            Party(code='C003', name='Customer E', party_type='customer', credit_limit=2000.0),
        ]
        ]
        session.add_all(parties)

        # Units
        units = [
            Unit(code='pcs', name='Pieces', factor_to_base=1.0),
            Unit(code='m', name='Meter', factor_to_base=1.0),
            Unit(code='m2', name='Square Meter', factor_to_base=1.0),
            Unit(code='kg', name='Kilogram', factor_to_base=1.0),
            Unit(code='cm', name='Centimeter', factor_to_base=0.01),  # نسبت به m
        ]
        session.add_all(units)

        # Items (10 تا، mix)
        items = [
            Item(sku='SKU001', name='Book', unit_type='count', base_unit_id=1, barcode='123456'),  # count
            Item(sku='SKU002', name='Fabric', unit_type='measure', base_unit_id=2, length=10.0, width=1.5, barcode='654321'),  # measure
            # 8 تا دیگه...
            Item(sku='SKU003', name='Pen', unit_type='count', base_unit_id=1),
            Item(sku='SKU004', name='Paper Roll', unit_type='measure', base_unit_id=2, length=50.0),
            Item(sku='SKU005', name='Tile', unit_type='measure', base_unit_id=3, length=0.5, width=0.5),
            Item(sku='SKU006', name='Sugar', unit_type='measure', base_unit_id=4),
            Item(sku='SKU007', name='Notebook', unit_type='count', base_unit_id=1),
            Item(sku='SKU008', name='Wire', unit_type='measure', base_unit_id=2, length=100.0),
            Item(sku='SKU009', name='Paint', unit_type='measure', base_unit_id=4),
            Item(sku='SKU010', name='Chair', unit_type='count', base_unit_id=1),
        ]
        session.add_all(items)
    print("Seeded data for parties, units, and items.")

if __name__ == '__main__':
    seed_data()