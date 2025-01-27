from sqlalchemy import Column, Integer, String, Float
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy.orm import DeclarativeBase


# базовый класс для модели
class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    article = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    rating = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(),
                        onupdate=datetime.utcnow().isoformat())


class ProductRequest(BaseModel):
    article: int = Field(..., example=211695539)
