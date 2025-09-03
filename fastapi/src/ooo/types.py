from pydantic import BaseModel


class CounterUpdate(BaseModel):
    name: str
    value: int


class CounterCreate(CounterUpdate):
    pass


class CounterRead(CounterCreate):
    pass
