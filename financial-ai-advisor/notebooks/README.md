# Interactive Notebooks

## 📓 interactive_advisor.ipynb

An interactive Jupyter notebook for experimenting with the Financial AI Advisor system.

### Features

✅ **Quick Testing** - Test advisor with simple inputs  
✅ **Persona Comparison** - Compare basic, expertise, and full prompts side-by-side  
✅ **Pre-built Scenarios** - Young professional, family planning, retirement, debt  
✅ **Fast Iteration** - `quick_advice()` function for rapid experimentation  
✅ **Financial Metrics** - Calculate and visualize financial health  
✅ **Export Results** - Save advice to JSON files  

### Setup

```bash
# From project root
cd /Users/mfrancys/Documents/2026/financial-ai-advisor

# Activate virtual environment
source venv/bin/activate

# Install Jupyter (if not already installed)
pip install jupyter pandas matplotlib

# Start Jupyter
jupyter notebook notebooks/interactive_advisor.ipynb
```

### Quick Start

1. **Run Setup Cells** (cells 1-3): Load environment and imports
2. **Test Simple Scenario** (cells 4-6): Quick test with Alex's bonus scenario
3. **Compare Personas** (cells 7-8): See prompt engineering in action
4. **Fast Iteration** (cells 9-10): Use `quick_advice()` function

### Example Usage

```python
# In the notebook, just edit values and run:
result = quick_advice(
    age=30,
    income=80000,
    expenses=3000,
    debt=5000,
    savings=10000,
    question="Should I buy a house or keep renting?"
)
```

### What You'll Learn

1. **Prompt Engineering Impact** - See how prompt quality affects advice
2. **Financial Calculations** - Understand metrics like DTI, cash flow, emergency fund
3. **Persona Design** - Learn what makes a good AI persona
4. **Rapid Prototyping** - Iterate quickly without running the full API

### Tips for Iteration

- **Start Simple**: Use cell 10 (`quick_advice()`) for fastest iteration
- **Compare Personas**: Run cell 8 to see all three prompts side-by-side
- **Visualize**: Uncomment visualization cells to see financial metrics
- **Save Results**: Use the export cell to save advice for later analysis
- **Customize Prompts**: Edit `src/prompts/system_prompts.py` and reload

### Troubleshooting

**ModuleNotFoundError?**
- Make sure you're running from the `notebooks/` directory
- Check that virtual environment is activated
- Verify imports in cell 3

**No API Key?**
- Create `.env` file in project root
- Add: `OPENAI_API_KEY=sk-your-key-here`
- Restart notebook kernel

**Slow responses?**
- Using `gpt-4o-mini` (fast & cheap)
- Switch to `gpt-4` for better quality if needed
- Responses typically take 2-5 seconds

---

**Happy iterating!** 🚀💰

