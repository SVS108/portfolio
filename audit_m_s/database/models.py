from sqlalchemy import DateTime, BigInteger, Integer, Float, String, func, ForeignKey, Identity
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from enum import Enum


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True, nullable=False)

class Account_type_default(Base):
    __tablename__ = "account_types_default"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)    

class Account_type(Base):
    __tablename__ = "account_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

class Account_currency_default(Base):
    __tablename__ = "account_currencies_default"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    cod: Mapped[str] = mapped_column(String(3), nullable=False)

class Account_currency(Base):
    __tablename__ = "account_currencies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cod: Mapped[str] = mapped_column(String(3), nullable=False)

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey(Account_type.id), nullable=False)
    currency_id: Mapped[int] = mapped_column(ForeignKey(Account_currency.id), nullable=False)
    limit: Mapped[int] = mapped_column(Float, nullable=True)

class Account_default(Base):
    __tablename__ = "accounts_default"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey(Account_type_default.id), nullable=False)
    currency_id: Mapped[int] = mapped_column(ForeignKey(Account_currency_default.id), nullable=False)

class Operation(Enum):
    earnings = "Доходы"
    expenses = "Расходы"

class Category_default(Base):
    __tablename__ = "categories_default"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_type: Mapped[Operation]
    name: Mapped[str] = mapped_column(String(50), nullable=False)       

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    category_type: Mapped[Operation]
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    
class Place_default(Base):
    __tablename__ = "place_default"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)    

class Place(Base):
    __tablename__ = "places"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)    


class Budget(Base):
    __tablename__ = "budget"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)    
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey(Account.id), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey(Category.id), nullable=False)
    place_id: Mapped[int] = mapped_column(ForeignKey(Place.id), nullable=False)
    sum: Mapped[float] = mapped_column(Float, nullable=False) 
    comment: Mapped[str] = mapped_column(String(50), nullable=True) 