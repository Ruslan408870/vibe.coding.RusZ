from pydantic import BaseModel, ConfigDict, Field, field_validator


class Order(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    order_id: int = Field(gt=0, description="Уникальный ID заказа")
    customer_name: str = Field(min_length=2, max_length=100)
    items: list[str] = Field(min_length=1)
    total_amount: float = Field(gt=0)

    @field_validator("customer_name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Имя клиента не может быть пустым")
        return value