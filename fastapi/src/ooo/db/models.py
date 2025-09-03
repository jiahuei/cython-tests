from sqlalchemy.orm import declared_attr
from sqlmodel import Field as SqlField
from sqlmodel import MetaData, SQLModel


class OooSQLModel(SQLModel):
    metadata = MetaData()

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__


class Counter(OooSQLModel, table=True):
    name: str = SqlField(primary_key=True)
    value: int = SqlField(0)
