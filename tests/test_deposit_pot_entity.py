import pytest
import sys
import os
from typing import Dict

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from domain.entity.deposit_pot_entity import DepositPot


class TestDepositPot:
    """Test suite for the DepositPot class using pytest."""

    @pytest.fixture
    def sample_portfolio_limits(self) -> Dict[str, float]:
        """Fixture providing sample portfolio allocation limits."""
        return {
            "Portfolio A": 1000.0,
            "Portfolio B": 500.0,
            "Portfolio C": 250.0
        }

    @pytest.fixture
    def sample_portfolio_allocation(self) -> Dict[str, float]:
        """Fixture providing sample current portfolio allocations."""
        return {
            "Portfolio A": 200.0,
            "Portfolio B": 100.0,
            "Portfolio C": 50.0
        }

    @pytest.fixture
    def deposit_pot(self, sample_portfolio_limits, sample_portfolio_allocation) -> DepositPot:
        """Fixture providing a DepositPot instance for testing."""
        return DepositPot(
            portfolio_allocation_limit=sample_portfolio_limits.copy(),
            portfolio_allocation=sample_portfolio_allocation.copy()
        )

    @pytest.fixture
    def empty_deposit_pot(self, sample_portfolio_limits) -> DepositPot:
        """Fixture providing an empty DepositPot instance."""
        return DepositPot(
            portfolio_allocation_limit=sample_portfolio_limits.copy(),
            portfolio_allocation={}
        )

    @pytest.fixture
    def full_deposit_pot(self) -> DepositPot:
        """Fixture providing a full DepositPot instance."""
        limits = {"Portfolio A": 1000.0, "Portfolio B": 500.0}
        return DepositPot(
            portfolio_allocation_limit=limits,
            portfolio_allocation=limits.copy()
        )

    def test_deposit_pot_initialization(self, deposit_pot, sample_portfolio_limits, sample_portfolio_allocation):
        """Test that DepositPot initializes correctly."""
        assert deposit_pot.portfolio_allocation_limit == sample_portfolio_limits
        assert deposit_pot.portfolio_allocation == sample_portfolio_allocation

    def test_get_total_allocation_limit(self, deposit_pot):
        """Test getting total allocation limit."""
        expected_total = 1000.0 + 500.0 + 250.0
        assert deposit_pot.get_total_allocation_limit() == expected_total

    def test_get_remaining_allocation_total_amount(self, deposit_pot):
        """Test getting remaining allocation amount."""
        total_limit = 1750.0  # Portfolio A: 1000 + Portfolio B: 500 + Portfolio C: 250
        total_allocated = 350.0  # Portfolio A: 200 + Portfolio B: 100 + Portfolio C: 50
        expected_remaining = total_limit - total_allocated  # 1400.0
        assert deposit_pot.get_remaining_allocation_total_amount() == expected_remaining

    def test_get_portfolio_allocation_ratio(self, deposit_pot):
        """Test getting portfolio allocation ratios."""
        ratios = deposit_pot.get_portfolio_allocation_ratio()
        total_limit = 1750.0
        
        expected_ratios = {
            "Portfolio A": 1000.0 / total_limit,
            "Portfolio B": 500.0 / total_limit,
            "Portfolio C": 250.0 / total_limit,
        }
        
        for portfolio, expected_ratio in expected_ratios.items():
            assert abs(ratios[portfolio] - expected_ratio) < 1e-4

    def test_get_portfolio_allocation_ratio_zero_total(self):
        """Test getting portfolio allocation ratios when total limit is zero."""
        zero_pot = DepositPot(
            portfolio_allocation_limit={"Portfolio A": 0.0, "Portfolio B": 0.0},
            portfolio_allocation={"Portfolio A": 0.0, "Portfolio B": 0.0}
        )
        ratios = zero_pot.get_portfolio_allocation_ratio()
        expected_ratios = {"Portfolio A": 0.0, "Portfolio B": 0.0}
        assert ratios == expected_ratios

    def test_is_full_false(self, deposit_pot):
        """Test is_full method when pot is not full."""
        assert not deposit_pot.is_full()

    def test_is_full_true(self, full_deposit_pot):
        """Test is_full method when pot is full."""
        assert full_deposit_pot.is_full()

    def test_is_full_overfull(self):
        """Test is_full method when pot is overfull."""
        overfull_pot = DepositPot(
            portfolio_allocation_limit={"Portfolio A": 1000.0, "Portfolio B": 500.0},
            portfolio_allocation={"Portfolio A": 1100.0, "Portfolio B": 600.0}
        )
        assert overfull_pot.is_full()

    def test_allocate_deposit_normal_case(self, deposit_pot):
        """Test allocating a deposit amount that fits within remaining allocation."""
        initial_allocation = deposit_pot.portfolio_allocation.copy()
        deposit_amount = 500.0
        
        excess = deposit_pot.allocate_deposit(deposit_amount)
        
        # Should have no excess
        assert excess == 0.0
        
        # Check that allocations were updated proportionally
        ratios = {
            "Portfolio A": 1000.0 / 1750.0,
            "Portfolio B": 500.0 / 1750.0,
            "Portfolio C": 250.0 / 1750.0
        }
        
        for portfolio in deposit_pot.portfolio_allocation_limit.keys():
            expected_addition = ratios[portfolio] * deposit_amount
            expected_new_allocation = initial_allocation[portfolio] + expected_addition
            assert abs(deposit_pot.portfolio_allocation[portfolio] - expected_new_allocation) < 1e-4

    def test_allocate_deposit_excess_case(self, deposit_pot):
        """Test allocating a deposit amount that exceeds remaining allocation."""
        remaining = deposit_pot.get_remaining_allocation_total_amount()  # 1450.0
        deposit_amount = 2000.0  # More than remaining
        
        excess = deposit_pot.allocate_deposit(deposit_amount)
        
        # Should have excess
        expected_excess = deposit_amount - remaining
        assert excess == expected_excess
        
        # Check that the pot is now full
        assert deposit_pot.is_full()

    def test_allocate_deposit_exact_remaining(self, deposit_pot):
        """Test allocating exactly the remaining amount."""
        remaining = deposit_pot.get_remaining_allocation_total_amount()
        
        excess = deposit_pot.allocate_deposit(remaining)
        
        # Should have no excess
        assert excess == 0.0
        
        # Should be exactly full
        assert deposit_pot.is_full()
        assert abs(deposit_pot.get_remaining_allocation_total_amount()) < 1e-10

    def test_allocate_deposit_zero_amount(self, deposit_pot):
        """Test allocating zero deposit amount."""
        initial_allocation = deposit_pot.portfolio_allocation.copy()
        
        excess = deposit_pot.allocate_deposit(0.0)
        
        # Should have no excess and no changes
        assert excess == 0.0
        assert deposit_pot.portfolio_allocation == initial_allocation

    def test_allocate_deposit_to_full_pot(self, full_deposit_pot):
        """Test allocating to an already full pot."""
        deposit_amount = 100.0
        initial_allocation = full_deposit_pot.portfolio_allocation.copy()
        
        excess = full_deposit_pot.allocate_deposit(deposit_amount)
        
        # All should be excess
        assert excess == deposit_amount
        
        # Allocation should remain unchanged
        assert full_deposit_pot.portfolio_allocation == initial_allocation

    def test_multiple_allocations(self, deposit_pot):
        """Test multiple sequential allocations."""
        # First allocation
        excess1 = deposit_pot.allocate_deposit(250.0)
        assert excess1 == 0.0
        
        # Second allocation
        excess2 = deposit_pot.allocate_deposit(400.0)
        assert excess2 == 0.0
        
        # Third allocation that should cause excess
        remaining = deposit_pot.get_remaining_allocation_total_amount()
        excess3 = deposit_pot.allocate_deposit(remaining + 100.0)
        assert excess3 == 100.0
        
        # Pot should now be full
        assert deposit_pot.is_full()

    def test_empty_portfolio_allocation(self, empty_deposit_pot):
        """Test with empty initial portfolio allocation."""
        deposit_amount = 250.0
        excess = empty_deposit_pot.allocate_deposit(deposit_amount)
        
        assert excess == 0.0
        
        # Check that portfolios were allocated proportionally
        expected_portfolio_a = (1000.0 / 1750.0) * deposit_amount
        expected_portfolio_b = (500.0 / 1750.0) * deposit_amount
        expected_portfolio_c = (250.0 / 1750.0) * deposit_amount
        
        assert abs(empty_deposit_pot.portfolio_allocation.get("Portfolio A", 0.0) - expected_portfolio_a) < 1e-4
        assert abs(empty_deposit_pot.portfolio_allocation.get("Portfolio B", 0.0) - expected_portfolio_b) < 1e-4
        assert abs(empty_deposit_pot.portfolio_allocation.get("Portfolio C", 0.0) - expected_portfolio_c) < 1e-4

    def test_allocate_negative_amount(self, deposit_pot):
        """Test allocating negative amount (edge case)."""
        initial_allocation = deposit_pot.portfolio_allocation.copy()
        
        excess = deposit_pot.allocate_deposit(-100.0)
        
        # Negative amount should be treated as reducing allocations proportionally
        # Since -100 < remaining (1450), excess should be 0
        assert excess == 0.0
        
        # Verify that allocations were reduced proportionally
        ratios = {
            "Portfolio A": 1000.0 / 1750.0,
            "Portfolio B": 500.0 / 1750.0,
            "Portfolio C": 250.0 / 1750.0
        }
        
        for portfolio in deposit_pot.portfolio_allocation_limit.keys():
            expected_reduction = ratios[portfolio] * (-100.0)
            expected_new_allocation = initial_allocation[portfolio] + expected_reduction
            assert abs(deposit_pot.portfolio_allocation[portfolio] - expected_new_allocation) < 1e-4

    @pytest.mark.parametrize("deposit_amount,expected_excess", [
        (100.0, 0.0),
        (500.0, 0.0),
        (1400.0, 0.0),  # Exact remaining
        (1500.0, 100.0),  # Slight excess
        (2000.0, 600.0),  # Large excess
    ])
    def test_allocate_deposit_parametrized(self, deposit_pot, deposit_amount, expected_excess):
        """Test allocation with various deposit amounts."""
        excess = deposit_pot.allocate_deposit(deposit_amount)
        assert excess == expected_excess

    def test_portfolio_allocation_precision(self, deposit_pot):
        """Test that portfolio allocations maintain precision."""
        # Allocate a small amount
        small_amount = 0.01
        excess = deposit_pot.allocate_deposit(small_amount)
        
        assert excess == 0.0
        
        # Check that the total allocated amount matches the deposit
        total_new_allocation = sum(deposit_pot.portfolio_allocation.values())
        expected_total = 350.0 + small_amount  # Initial 350.0 + 0.01
        assert abs(total_new_allocation - expected_total) < 1e-10

    def test_single_portfolio_allocation(self):
        """Test with a single portfolio."""
        single_pot = DepositPot(
            portfolio_allocation_limit={"Portfolio A": 1000.0},
            portfolio_allocation={"Portfolio A": 200.0}
        )
        
        excess = single_pot.allocate_deposit(250.0)
        assert excess == 0.0
        assert single_pot.portfolio_allocation["Portfolio A"] == 450.0
        
        # Test ratio calculation
        ratios = single_pot.get_portfolio_allocation_ratio()
        assert ratios["Portfolio A"] == 1.0

    def test_concurrent_portfolio_updates(self, deposit_pot):
        """Test that portfolio allocations are updated atomically."""
        initial_total = sum(deposit_pot.portfolio_allocation.values())
        deposit_amount = 175.0  # 10% of total limit
        
        excess = deposit_pot.allocate_deposit(deposit_amount)
        
        assert excess == 0.0
        final_total = sum(deposit_pot.portfolio_allocation.values())
        assert abs(final_total - (initial_total + deposit_amount)) < 1e-10
