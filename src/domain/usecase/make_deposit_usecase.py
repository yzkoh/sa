from abc import ABC
from typing import List, Dict

from domain.entity.deposit_plan_entity import DepositPlan
from domain.entity.deposit_entity import Deposit
from domain.entity.deposit_pot_entity import DepositPot

class MakeDepositUsecase(ABC):
    """
    Abstract base class for making deposits.
    This class defines the interface for deposit operations.
    """
    def execute(self, deposit_plan_list: List[DepositPlan], deposit_list: List[Deposit]) -> Dict[str, float]:
        """
        Gets a user by their reference code.

        Args:
            reference_code (str): The unique reference code of the user.

        Returns:
            Dict[str, float]: A dictionary mapping portfolio name to the total deposit amounts.
        """

        if not deposit_plan_list or not deposit_list:
            return {}
        
        portfolio_allocation: Dict[str, float] = {}
        total_deposit_amount = sum(deposit.amount for deposit in deposit_list)
        
        # Sort deposit plan by type, one_time first, then monthly. This tells the priority
        # of allocation, one_time plans are allocated first. The following action
        # fills the "virtual pot" (deposit plan) in the order of priority.
        deposit_plan_list.sort(key=lambda plan: plan.plan_type == 'monthly')
        
        remaining_deposit_amount = total_deposit_amount
        for deposit_plan in deposit_plan_list:
            pot = DepositPot(
                portfolio_allocation_limit=deposit_plan.portfolio_allocation.copy(),
                portfolio_allocation={}
            )
            pot.allocate_deposit(remaining_deposit_amount)
            remaining_deposit_amount -= pot.get_total_allocation_amount()
            
            # add the portfolio allocation to the total portfolio allocation
            for portfolio, amount in pot.portfolio_allocation.items():
                portfolio_allocation[portfolio] = portfolio_allocation.get(portfolio, 0.0) + amount

            run_out_of_deposit = remaining_deposit_amount <= 0
            if run_out_of_deposit:
                break            

        if remaining_deposit_amount > 0:
            # use "monthly" allocation ratio, if not use "one_time" (hence referring to last item in the sorted deposit plan list)
            remaining_allocation_ratio = deposit_plan_list[-1].get_allocation_ratio()
            self._add_remaining_allocation(portfolio_allocation, remaining_allocation_ratio, remaining_deposit_amount)
        
        return portfolio_allocation

    def _add_remaining_allocation(self, portfolio_allocation: Dict[str, float], allocation_ratio: Dict[str, float], remaining_amount: float) -> Dict[str, float]:
        """
        Calculates the remaining allocation for each portfolio based on the allocation ratio and remaining amount.

        Args:
            portfolio_allocation (Dict[str, float]): The current portfolio allocation.
            allocation_ratio (Dict[str, float]): The allocation ratio for each portfolio.
            remaining_amount (float): The remaining amount to be allocated.

        Returns:
            Dict[str, float]: The updated portfolio allocation.
        """
        for portfolio, ratio in allocation_ratio.items():
            portfolio_allocation[portfolio] = portfolio_allocation.get(portfolio, 0.0) + ratio * remaining_amount

        return portfolio_allocation
