# Deposit Plan System

A Python-based deposit allocation system that manages user deposits across different investment portfolios using a sophisticated three-tier priority allocation strategy.

## Overview

The Deposit Plan System is designed to automatically allocate user deposits across various investment portfolios based on predefined allocation plans. The system supports two types of deposit plans:

- **One-Time Plans**: Single-use allocation instructions with highest priority
- **Monthly Plans**: Recurring allocation patterns that serve as the default investment strategy

## Key Features

- **Priority-Based Allocation**: Three-tier allocation system ensuring optimal fund distribution
- **Flexible Portfolio Management**: Support for multiple investment portfolios with customizable allocations
- **Proportional Distribution**: Intelligent handling of partial fulfillments and excess funds
- **Type Safety**: Built with Python dataclasses and type hints for robust data handling
- **Comprehensive Testing**: Full test suite with pytest integration

## Architecture

The system follows Clean Architecture principles with clear separation of concerns:

```
src/
├── main.py                          # Application entry point
├── constants/                       # System constants and configuration
├── domain/
│   ├── entity/                      # Business entities
│   │   ├── deposit_entity.py        # Deposit data model
│   │   ├── deposit_plan_entity.py   # Deposit plan data model
│   │   └── deposit_pot_entity.py    # Allocation container model
│   └── usecase/                     # Business logic
│       └── make_deposit_usecase.py  # Core allocation logic
```

### Core Entities

1. **Deposit**: Represents a user deposit with amount, reference, and timestamp
2. **DepositPlan**: Defines allocation rules for one-time or monthly plans
3. **DepositPot**: Virtual container that manages allocation limits and distributions

## Allocation Logic

The system implements a sophisticated three-step priority allocation strategy:

### 1. Fulfill the One-Time Plan (Highest Priority)
- The system prioritizes the one-time deposit plan above all others
- Funds are allocated to fully satisfy the one-time plan's portfolio allocation
- Once fulfilled, the one-time plan is marked as complete and won't be considered in future deposits
- This ensures urgent or special investment instructions are handled first

### 2. Fulfill the Monthly Plan (Secondary Priority)
- After the one-time plan is satisfied, remaining funds are used for the monthly plan
- The monthly plan represents the user's regular investment strategy
- This plan remains active for future deposits and represents ongoing investment goals

### 3. Distribute Excess Funds (Overflow Handling)
- Any funds remaining after both plans are fulfilled are distributed proportionally
- The distribution follows the monthly plan's allocation percentages
- This reinforces the user's long-term investment strategy as the default choice
- Ensures no funds remain unallocated

### Partial Fulfillment Strategy

When deposits are insufficient to fully satisfy a plan:
- Funds are allocated proportionally according to the plan's allocation rules
- This maintains the user's desired asset mix even with smaller deposits
- Each portfolio receives funds based on its percentage within the plan
- No portfolio is completely neglected in partial fulfillment scenarios

### Example Allocation Scenario

Consider the following setup:
- **One-Time Plan**: $10,000 to High Risk, $500 to Retirement
- **Monthly Plan**: $300 to Medium Risk, $100 to Retirement
- **Total Deposit**: $10,600

**Step 1**: Allocate $10,500 to fulfill one-time plan completely
- High Risk: $10,000
- Retirement: $500

**Step 2**: Remaining $100 goes to monthly plan proportionally
- Medium Risk: $75 (75% of monthly plan)
- Retirement: $25 (25% of monthly plan)

**Final Allocation**:
- High Risk: $10,000
- Medium Risk: $75
- Retirement: $525

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Running the Application

Execute the main application to see the allocation system in action:

```bash
python3 ./src/main.py
```

This will run the demo scenario with predefined deposit plans and deposits, showing how the allocation logic works in practice.

### Setting Up the Development Environment

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment**:
   ```bash
   source ./venv/bin/activate
   ```

3. **Install test dependencies**:
   ```bash
   pip install -r requirements-test.txt
   ```

### Running the Test Suite

Execute the comprehensive test suite to verify system functionality:

```bash
python -m pytest
```

#### Advanced Testing Options

**Run tests with coverage report**:
```bash
python -m pytest --cov=src --cov-report=html
```

**Run specific test files**:
```bash
python -m pytest tests/test_deposit_pot_entity.py
python -m pytest tests/test_make_deposit_usecase.py
```

**Run tests in verbose mode**:
```bash
python -m pytest -v
```

## Usage Examples

### Basic Usage

```python
from datetime import datetime
from domain.entity.deposit_plan_entity import DepositPlan
from domain.entity.deposit_entity import Deposit
from domain.usecase.make_deposit_usecase import MakeDepositUsecase

# Create deposit plans
one_time_plan = DepositPlan(
    plan_type="one_time", 
    portfolio_allocation={"High Risk": 10000, "Retirement": 500}
)

monthly_plan = DepositPlan(
    plan_type="monthly", 
    portfolio_allocation={"Medium Risk": 300, "Retirement": 100}
)

# Create deposits
deposit = Deposit(
    id="deposit1", 
    amount=10600.0, 
    reference_code="ref123", 
    deposited_at=datetime(2025, 7, 31)
)

# Execute allocation
usecase = MakeDepositUsecase()
result = usecase.execute([one_time_plan, monthly_plan], [deposit])
print(result)  # {'High Risk': 10000.0, 'Retirement': 525.0, 'Medium Risk': 75.0}
```

### Custom Portfolio Allocation

```python
# Create a custom allocation strategy
custom_plan = DepositPlan(
    plan_type="monthly",
    portfolio_allocation={
        "Conservative": 500,
        "Balanced": 300,
        "Aggressive": 200
    }
)

# Handle multiple deposits
deposits = [
    Deposit("d1", 600.0, "ref1", datetime.now()),
    Deposit("d2", 400.0, "ref2", datetime.now())
]

result = usecase.execute([custom_plan], deposits)
# Total $1000 allocated proportionally: Conservative: $500, Balanced: $300, Aggressive: $200
```

## Testing Strategy

The system includes comprehensive tests covering:

- **Entity Tests**: Validation of data models and their methods
- **Use Case Tests**: Core business logic verification
- **Integration Tests**: End-to-end allocation scenarios
- **Edge Cases**: Boundary conditions and error handling

### Test Coverage

The test suite maintains high coverage across all components:
- Entity validation and calculations
- Allocation logic accuracy
- Partial fulfillment scenarios
- Excess fund distribution
- Error handling and edge cases

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints throughout the codebase
- Maintain clear docstrings for all public methods
- Implement dataclasses for data models

### Adding New Features
1. Create corresponding tests first (TDD approach)
2. Implement the feature following existing patterns
3. Ensure all tests pass
4. Update documentation as needed

### Error Handling
The system gracefully handles various scenarios:
- Empty deposit lists
- Zero-amount deposits
- Invalid plan configurations
- Rounding precision issues
