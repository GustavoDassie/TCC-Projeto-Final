from sqlalchemy import *
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import session
from database import Base

class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    raw_data = Column(LargeBinary(length=(2**32)-1),nullable=False)
    file_name = Column(String(255))
    file_ext = Column(String(255))
    treated_data = Column(LargeBinary(length=(2**32)-1),nullable=True)
    charset = Column(String(255))
    insert_date = Column(DATETIME,server_default=func.now())
