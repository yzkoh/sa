from dataclasses import dataclass
from datetime import datetime

@dataclass
class Deposit:
    """
    Represents a deposit made by user.
    
    Attributes:
        id (str): The unique identifier of the deposit.
        amount (float): The amount of the deposit.
        reference_code (str): A unique reference code for the deposit.
        deposited_at (datetime): The date and time when the deposit was made.
    """
    id: str
    amount: float
    reference_code: str
    deposited_at: datetime
    