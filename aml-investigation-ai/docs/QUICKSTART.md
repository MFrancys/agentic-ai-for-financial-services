# Quick Start Guide

Get started with AML Investigation AI in 5 minutes.

## Prerequisites

- Python 3.10+
- OpenAI API key
- pip or conda

## Installation

1. **Clone or navigate to the project:**
   ```bash
   cd aml-investigation-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Quick Test

### Option 1: Command Line Interface

Run the demo with 3 predefined cases:

```bash
python app.py --demo
```

Run a specific case:

```bash
python app.py --case-id CASE_001
```

### Option 2: Python API

```python
from src.models.investigation_case import InvestigationCase, AlertType
from src.investigators.react_investigator import ReACTInvestigator

# Create a case
case = InvestigationCase(
    case_id="DEMO_001",
    customer_id="CUST_001",
    account_id="high_risk_account_001",
    alert_type=AlertType.CASH_STRUCTURING,
    description="Multiple cash deposits under $10,000",
    time_period_days=14,
)

# Run investigation
investigator = ReACTInvestigator()
result = investigator.investigate(case, verbose=True)

# Check results
print(f"Risk Score: {result.final_risk_score}/10")
print(f"SAR Required: {result.sar_required}")
print(f"Recommendation: {result.recommendation}")
```

### Option 3: REST API

Start the API server:

```bash
uvicorn src.api.main:app --reload
```

Then visit http://localhost:8000/api/v1/docs for interactive API documentation.

Test with curl:

```bash
curl -X POST http://localhost:8000/api/v1/investigations \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_001",
    "account_id": "high_risk_account_001",
    "alert_type": "cash_structuring",
    "description": "Multiple deposits under threshold",
    "priority": "high"
  }'
```

### Option 4: Jupyter Notebook

```bash
jupyter notebook notebooks/interactive_investigation.ipynb
```

Then follow the interactive examples in the notebook.

## What's Next?

- Read the full [README.md](../README.md) for detailed documentation
- Explore [examples/](../examples/) for more scenarios
- Check [tests/](../tests/) to understand the testing approach
- Customize the system for your needs

## Troubleshooting

**Issue: "OPENAI_API_KEY is required"**
- Make sure you've created a `.env` file with your API key
- Verify the key is valid and has credits

**Issue: "Module not found"**
- Make sure you're running from the project root directory
- Install all requirements: `pip install -r requirements.txt`

**Issue: "No transactions found"**
- This is expected for unknown account IDs when using mock data
- Try the predefined account IDs: `high_risk_account_001`, `business_account_002`, `normal_account`

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review example scenarios in `examples/`
- Run tests: `pytest tests/`

