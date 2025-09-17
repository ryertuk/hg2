from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os

DB_URL = os.getenv('DB_URL', 'sqlite:///smart_accountant.db')
engine = create_engine(DB_URL, echo=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


# Base class برای timestamps
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Event listener برای audit (در مراحل بعدی گسترش)
@listens_for(Base, 'before_update')
def before_update(mapper, connection, target):
    # TODO: ذخیره snapshot و diff در audit_logs
    pass