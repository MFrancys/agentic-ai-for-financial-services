# AML Investigation AI

A production-ready Anti-Money Laundering (AML) investigation system powered by AI agents using the ReACT (Reasoning and Acting) framework. This system enables automated financial crime detection and investigation through intelligent tool usage and evidence-based decision making.

## Features

🔍 **Intelligent Investigation**
- ReACT framework for systematic reasoning and action
- Real-time tool integration for data gathering
- Evidence-based decision making
- Audit trail of all investigation steps

🛠️ **Investigation Tools**
- Transaction history analysis
- Customer profile evaluation
- Regulatory threshold checking
- Risk scoring and assessment
- Pattern detection (structuring, velocity, etc.)

🚨 **Use Cases**
- Suspicious Activity Report (SAR) investigations
- Cash structuring detection
- Wire transfer monitoring
- Customer due diligence (CDD)
- Enhanced due diligence (EDD)
- Transaction monitoring alerts

## Architecture

```
aml-investigation-ai/
├── src/
│   ├── tools/              # Investigation tools (transaction, profile, regulatory)
│   ├── investigators/      # ReACT investigator agents
│   ├── models/            # Data models (cases, profiles, reports)
│   ├── api/               # FastAPI endpoints
│   ├── prompts/           # ReACT prompts and templates
│   ├── utils/             # Utilities and helpers
│   └── data/              # Mock data for testing
├── examples/              # Example investigations
├── tests/                 # Unit and integration tests
├── notebooks/            # Interactive Jupyter notebooks
└── app.py                # Main CLI application
```

## Quick Start

### Installation

```bash
cd aml-investigation-ai
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Run an Investigation

```bash
# CLI Investigation
python app.py --case-id CASE_001

# API Server
uvicorn src.api.main:app --reload

# Interactive Notebook
jupyter notebook notebooks/interactive_investigation.ipynb
```

## Example Usage

### Python API

```python
from src.investigators.react_investigator import ReACTInvestigator
from src.models.investigation_case import InvestigationCase

# Create investigator
investigator = ReACTInvestigator()

# Define case
case = InvestigationCase(
    case_id="CASE_001",
    customer_id="CUST_001",
    account_id="high_risk_account_001",
    alert_type="cash_structuring",
    description="Multiple cash deposits just under $10,000"
)

# Run investigation
result = investigator.investigate(case)

# Review findings
print(result.recommendation)
print(result.evidence)
print(result.sar_required)
```

### REST API

```bash
# Start investigation
curl -X POST http://localhost:8000/api/v1/investigations \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_001",
    "account_id": "high_risk_account_001",
    "alert_type": "cash_structuring",
    "description": "Multiple deposits under threshold"
  }'

# Get investigation status
curl http://localhost:8000/api/v1/investigations/CASE_001
```

## ReACT Framework

The system uses the **ReACT (Reasoning and Acting)** pattern:

1. **THOUGHT**: Analyze the situation and decide what information is needed
2. **ACTION**: Execute investigation tools to gather data
3. **OBSERVATION**: Process tool results and refine understanding
4. **REPEAT**: Continue until sufficient evidence is gathered
5. **CONCLUSION**: Make final recommendation with supporting evidence

## Investigation Tools

### Available Tools

1. **get_transaction_history(account_id, days)**
   - Retrieves transaction history for analysis
   - Identifies patterns and anomalies

2. **get_customer_profile(customer_id)**
   - Customer demographics and risk information
   - Historical SAR/CTR filings
   - Occupation and income verification

3. **check_regulatory_thresholds(amount, transaction_type)**
   - CTR threshold checking ($10,000+)
   - Structuring detection
   - Wire transfer reporting requirements

4. **calculate_risk_score(customer_id, transactions)**
   - ML-based risk assessment
   - Velocity analysis
   - Behavioral patterns

5. **search_negative_news(customer_name)**
   - Adverse media screening
   - PEP (Politically Exposed Person) checks
   - Sanctions screening

## Development

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src tests/

# Specific test
pytest tests/test_react_investigator.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
pylint src/

# Type checking
mypy src/
```

## Configuration

Configuration is managed through `src/config.py` and environment variables:

- `OPENAI_API_KEY`: OpenAI API key for LLM
- `MODEL_NAME`: Model to use (default: gpt-4o-mini)
- `TEMPERATURE`: Model temperature (default: 0.3)
- `MAX_ITERATIONS`: Max ReACT iterations (default: 5)
- `ENABLE_MOCK_DATA`: Use mock data for testing (default: True)

## Deployment

### Docker

```bash
# Build image
docker build -t aml-investigation-ai .

# Run container
docker run -p 8000:8000 --env-file .env aml-investigation-ai
```

### Production Considerations

- **Database**: Replace mock data with real database connections
- **Authentication**: Add OAuth2/JWT authentication for API
- **Monitoring**: Integrate with observability tools (Datadog, NewRelic)
- **Audit Logging**: All investigations are logged for compliance
- **Rate Limiting**: Implement rate limiting for API endpoints
- **Data Privacy**: Ensure PII handling complies with regulations

## Compliance & Legal

⚠️ **Important**: This system is for demonstration and educational purposes. For production use:

- Ensure compliance with local AML/KYC regulations
- Implement proper data protection (GDPR, CCPA)
- Regular model validation and bias testing
- Human review required for all SAR filings
- Maintain proper audit trails

## Examples

See `examples/` directory for:
- `scenario_cash_structuring.py`: Detecting structured deposits
- `scenario_wire_transfers.py`: International wire monitoring
- `scenario_customer_screening.py`: Enhanced due diligence
- `scenario_velocity_check.py`: Transaction velocity analysis

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Support

- Documentation: See `/docs` folder
- Issues: GitHub Issues
- Discussions: GitHub Discussions

