from datetime import datetime

from domain.entity.deposit_plan_entity import DepositPlan
from domain.entity.deposit_entity import Deposit
from domain.usecase.make_deposit_usecase import MakeDepositUsecase

def main():
    usecase = MakeDepositUsecase()

    deposit_plan_list=[
        DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 10000, "Retirement": 500}),
        DepositPlan(plan_type="monthly", portfolio_allocation={"Medium risk": 300, "Retirement": 100})
    ]
    deposit_list=[
        Deposit(id="deposit1", amount=10000.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
        Deposit(id="deposit2", amount=600.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31))
    ]
    
    portfolio_allocation = usecase.execute(deposit_plan_list, deposit_list)
    print(portfolio_allocation)

if __name__ == '__main__':
    main()
