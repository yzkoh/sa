import pytest
import sys
import os
from datetime import datetime
from typing import List, Dict

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from domain.entity.deposit_plan_entity import DepositPlan
from domain.entity.deposit_entity import Deposit
from domain.usecase.make_deposit_usecase import MakeDepositUsecase


class TestMakeDepositUsecase:
    """Test suite for the MakeDepositUsecase class using pytest."""

    @pytest.fixture
    def usecase(self) -> MakeDepositUsecase:
        """Fixture providing a MakeDepositUsecase instance."""
        return MakeDepositUsecase()

    @pytest.fixture
    def sample_datetime(self) -> datetime:
        """Fixture providing a sample datetime."""
        return datetime(2025, 7, 31, 12, 0, 0)

    @pytest.mark.parametrize("deposit_plans,deposits,expected_result", [
        # Test case from example
        pytest.param(
            [
                DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 10000, "Retirement": 500}),
                DepositPlan(plan_type="monthly", portfolio_allocation={"High risk": 0, "Retirement": 100})
            ],
            [
                Deposit(id="deposit1", amount=10500.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
                Deposit(id="deposit2", amount=100.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31))
            ],
            {"High risk": 10000.0, "Retirement": 600.0},
            id="main_example"
        ),

        # Test case with mixed portfolio
        pytest.param(
            [
                DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 10000, "Retirement": 500}),
                DepositPlan(plan_type="monthly", portfolio_allocation={"Medium risk": 300, "Retirement": 100})
            ],
            [
                Deposit(id="deposit1", amount=10000.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
                Deposit(id="deposit2", amount=600.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31))
            ],
            {"High risk": 10000.0, "Medium risk": 75.0,  "Retirement": 525.0},
            id="mixed_portfolio_example"
        ),
        
        # Test case with exact allocation limits
        pytest.param(
            [
                DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 1000, "Retirement": 500}),
            ],
            [
                Deposit(id="deposit1", amount=1500.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
            ],
            {"High risk": 1000.0, "Retirement": 500.0},
            id="exact_allocation"
        ),
        
        # Test case with excess amount going to monthly plan
        pytest.param(
            [
                DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 500, "Retirement": 300}),
                DepositPlan(plan_type="monthly", portfolio_allocation={"High risk": 200, "Retirement": 100})
            ],
            [
                Deposit(id="deposit1", amount=1200.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
            ],
            {"High risk": 500.0 + (400.0 * 2/3), "Retirement": 300.0 + (400.0 * 1/3)},
            id="excess_to_monthly"
        ),
        
        # Test case with multiple deposits
        pytest.param(
            [
                DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 800, "Retirement": 200}),
            ],
            [
                Deposit(id="deposit1", amount=500.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
                Deposit(id="deposit2", amount=300.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
                Deposit(id="deposit3", amount=200.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
            ],
            {"High risk": 800.0, "Retirement": 200.0},
            id="multiple_deposits"
        ),
        
        # Test case with zero allocation plan
        pytest.param(
            [
                DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 0, "Retirement": 0}),
                DepositPlan(plan_type="monthly", portfolio_allocation={"High risk": 100, "Retirement": 50})
            ],
            [
                Deposit(id="deposit1", amount=300.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
            ],
            {"High risk": 200.0, "Retirement": 100.0},
            id="zero_allocation_plan"
        ),
        
        # Test case with only monthly plan
        pytest.param(
            [
                DepositPlan(plan_type="monthly", portfolio_allocation={"High risk": 600, "Retirement": 400})
            ],
            [
                Deposit(id="deposit1", amount=1500.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
            ],
            {"High risk": 600.0 + (500.0 * 0.6), "Retirement": 400.0 + (500.0 * 0.4)},
            id="only_monthly_plan"
        ),
        
        # # Test case with small deposit amounts
        pytest.param(
            [
                DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 100, "Retirement": 50}),
            ],
            [
                Deposit(id="deposit1", amount=75.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
            ],
            {"High risk": 50.0, "Retirement": 25.0},
            id="small_amounts"
        ),
        
        # Test case with single portfolio
        pytest.param(
            [
                DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 1000}),
            ],
            [
                Deposit(id="deposit1", amount=800.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
            ],
            {"High risk": 800.0},
            id="single_portfolio"
        ),
    ])
    def test_execute_parametrized(self, usecase, deposit_plans, deposits, expected_result):
        """Test the execute method with various parametrized scenarios."""
        result = usecase.execute(deposit_plans, deposits)
        
        # Check that all expected portfolios are present
        for portfolio, expected_amount in expected_result.items():
            assert portfolio in result
            assert abs(result[portfolio] - expected_amount) < 1e-2, f"Portfolio {portfolio}: expected {expected_amount}, got {result[portfolio]}"
        
        # Check that no unexpected portfolios are present
        for portfolio in result:
            assert portfolio in expected_result, f"Unexpected portfolio {portfolio} in result"

    def test_execute_empty_deposit_list(self, usecase):
        """Test execute with empty deposit list."""
        deposit_plans = [
            DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 1000, "Retirement": 500}),
        ]
        deposits = []
        
        result = usecase.execute(deposit_plans, deposits)
        
        # Should return empty result for empty deposits
        assert result == {}

    def test_execute_empty_deposit_plan_list(self, usecase):
        """Test execute with empty deposit plan list."""
        deposit_plans = []
        deposits = [
            Deposit(id="deposit1", amount=1000.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
        ]
        
        result = usecase.execute(deposit_plans, deposits)
        
        # Should return empty result for empty deposit plans
        assert result == {}

    def test_execute_zero_deposit_amounts(self, usecase):
        """Test execute with zero deposit amounts."""
        deposit_plans = [
            DepositPlan(plan_type="one_time", portfolio_allocation={"High risk": 1000, "Retirement": 500}),
        ]
        deposits = [
            Deposit(id="deposit1", amount=0.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
        ]
        
        result = usecase.execute(deposit_plans, deposits)
        
        # Should return empty result for zero deposits
        assert result == {
            "High risk": 0.0,
            "Retirement": 0.0
        }

    def test_precision_handling(self, usecase):
        """Test that the usecase handles decimal precision correctly."""
        deposit_plans = [
            DepositPlan(plan_type="one_time", portfolio_allocation={"A": 333.33, "B": 333.33, "C": 333.34}),
        ]
        deposits = [
            Deposit(id="deposit1", amount=1000.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
        ]
        
        result = usecase.execute(deposit_plans, deposits)
        
        # Total allocation should equal the deposit amount
        total_result = sum(result.values())
        assert abs(total_result - 1000.0) < 1e-2

    def test_large_numbers(self, usecase):
        """Test with large monetary amounts."""
        deposit_plans = [
            DepositPlan(plan_type="one_time", portfolio_allocation={"LargeCap": 1000000, "SmallCap": 500000}),
        ]
        deposits = [
            Deposit(id="deposit1", amount=2000000.0, reference_code="ref123", deposited_at=datetime(2025, 7, 31)),
        ]
        
        result = usecase.execute(deposit_plans, deposits)
        
        # Should handle large numbers correctly
        expected_large_cap = 1000000.0 + (500000.0 * 2/3)  # 1333333.33
        expected_small_cap = 500000.0 + (500000.0 * 1/3)   # 666666.67
        
        assert abs(result["LargeCap"] - expected_large_cap) < 1e-4
        assert abs(result["SmallCap"] - expected_small_cap) < 1e-4
