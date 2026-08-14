from pydantic import BaseModel, ConfigDict


class ItemCreate(BaseModel):
    name: str
    description: str | None = None


class Item(ItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
