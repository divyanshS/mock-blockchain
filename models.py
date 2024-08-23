from typing import List, Optional

from pydantic import BaseModel


class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: int
    comment: Optional[str] = None


class Block(BaseModel):
    id: int
    timestamp: int
    transactions: List[Transaction]
    proof: str
    previous_hash: str
    comment: Optional[str] = None
