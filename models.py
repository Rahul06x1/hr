import datetime
from typing import List

from sqlalchemy import String, Integer, Date, create_engine, ForeignKey, UniqueConstraint, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from flask_sqlalchemy import SQLAlchemy

class HRDBBase(DeclarativeBase):
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

class Employee(HRDBBase):
    __tablename__ = "hr_employees"
    __table_args__ = (        
        UniqueConstraint("email"),
        )
    id: Mapped[int] = mapped_column(primary_key=True)
    last_name: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(50))
    title_id: Mapped[int] = mapped_column(ForeignKey("hr_designations.id"))
    title: Mapped["Designation"] = relationship(back_populates="employees")

class Designation(HRDBBase):
    __tablename__ = "hr_designations"
    __table_args__ = (        
        UniqueConstraint("title"),
        )
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    max_leaves: Mapped[int] = mapped_column(Integer)
    employees: Mapped[List["Employee"]] = relationship(back_populates="title")

class Leave(HRDBBase):
    __tablename__ = "hr_leaves"
    __table_args__ = (        
        UniqueConstraint("employee_id", "date"),
        )
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date())
    employee_id: Mapped[int] = mapped_column(ForeignKey("hr_employees.id"))
    reason: Mapped[str] = mapped_column(String(200))

def create_all(db_uri):
    engine = create_engine(db_uri)
    HRDBBase.metadata.create_all(engine)

def get_session(db_uri):
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session