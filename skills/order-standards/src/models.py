from pydantic import BaseModel, ConfigDict, Field, field_validator


class RefundRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: int
    reason: str = Field(min_length=10)
    refund_amount: float = Field(gt=0, allow_inf_nan=False)

    @field_validator("refund_amount", mode="before")
    @classmethod
    def _refund_amount_is_not_bool(cls, value: object) -> object:
        if isinstance(value, bool):
                        raise ValueError("refund_amount must be a number greater than 0")
        return value

