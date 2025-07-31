from dataclasses import dataclass
from typing import Dict

@dataclass
class DepositPot:
    """
    Represents a deposit plan for a user.
    
    Attributes:
        id (str): The unique identifier of the deposit plan.
        portfolio_allocation_limit (Dict[str, float]): A dictionary representing the maximum allocation limit for each portfolio
        portfolio_allocation (Dict[str, float]): A dictionary representing the actual allocation of the deposit across different portfolios.
    """
    portfolio_allocation_limit: Dict[str, float]
    portfolio_allocation: Dict[str, float]

    def allocate_deposit(self, deposit_amount: float) -> float:
        """
        Allocates the deposit amount according to the target portfolio allocation.

        Args:
            deposit_amount (float): The amount to be allocated.

        Returns:
            float: The excess amount that could not be allocated
        """

        # Get excess amount and deposit amount
        remaining_allocation = self.get_remaining_allocation_total_amount()
        if deposit_amount > remaining_allocation:
            excess_amount = deposit_amount - remaining_allocation
            deposit_amount = remaining_allocation
        else:
            excess_amount = 0.0

        # Allocate the deposit amount to each portfolio according to the allocation ratios
        allocation_ratios = self.get_portfolio_allocation_ratio()
        for portfolio, _ in self.portfolio_allocation_limit.items():
            portfolio_allocation = allocation_ratios.get(portfolio, 0.0) * deposit_amount
            self.portfolio_allocation[portfolio] = self.portfolio_allocation.get(portfolio, 0.0) + portfolio_allocation
        
        return excess_amount

    def get_remaining_allocation_total_amount(self) -> float:
        """
        Returns the total remaining allocation amount across all portfolios.

        Returns:
            float: The total remaining allocation amount.
        """
        return sum(self.portfolio_allocation_limit.values()) - sum(self.portfolio_allocation.values())

    def get_portfolio_allocation_ratio(self) -> Dict[str, float]:
        """
        Returns the portfolio allocation ratios for the deposit plan.

        Returns:
            Dict[str, float]: A dictionary mapping portfolio names to their allocation ratios.
        """
        total_allocation = sum(self.portfolio_allocation_limit.values())
        if total_allocation == 0:
            return {key: 0.0 for key in self.portfolio_allocation_limit.keys()}
        return {key: value / total_allocation for key, value in self.portfolio_allocation_limit.items()}

    def get_total_allocation_limit(self) -> float:
        """
        Returns the total allocation limit across all portfolios.

        Returns:
            float: The total allocation limit amount.
        """
        return sum(self.portfolio_allocation_limit.values())

    def get_total_allocation_amount(self) -> float:
        """
        Returns the total allocation amount across all portfolios.

        Returns:
            float: The total allocation amount.
        """
        return sum(self.portfolio_allocation.values())

    def is_full(self) -> bool:
        """
        Checks if the deposit pot is full.

        Returns:
            bool: True if the deposit pot is full, False otherwise.
        """
        return self.get_remaining_allocation_total_amount() <= 0
