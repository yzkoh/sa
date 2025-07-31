from dataclasses import dataclass
from typing import Dict, Literal, Union


@dataclass
class DepositPlan:
    """
    Represents a deposit plan for a user.
    
    Attributes:
        plan_type (str): The type of the deposit plan, either 'one_time' or 'monthly'.
        portfolio_allocation (Dict[str, float]): A dictionary representing the allocation of the deposit across different portfolios.
    """
    plan_type: Union[Literal['one_time'], Literal['monthly']]
    portfolio_allocation: Dict[str, float]

    def get_total_allocation(self) -> float:
        """
        Returns the total allocation across all portfolios.

        Returns:
            float: The total allocation amount.
        """
        return sum(self.portfolio_allocation.values())

    def get_allocation_ratio(self) -> Dict[str, float]:
        """
        Returns the allocation ratios for each portfolio.

        Returns:
            Dict[str, float]: A dictionary mapping portfolio names to their allocation ratios.
        """
        total_allocation = self.get_total_allocation()
        if total_allocation == 0:
            return {portfolio: 0.0 for portfolio in self.portfolio_allocation}
        
        return {portfolio: amount / total_allocation for portfolio, amount in self.portfolio_allocation.items()}