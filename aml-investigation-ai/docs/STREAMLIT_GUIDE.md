# Streamlit Web App Guide

An interactive web interface for the AML Investigation AI system.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser:**
   The app will automatically open at `http://localhost:8501`

## 📱 Features

### 1. Quick Investigation
- **Predefined Cases:** Choose from 3 ready-to-run investigation scenarios
  - Cash Structuring (Restaurant Owner)
  - Wire Transfers (Import/Export Business)
  - Normal Activity (Control Case)
- **One-Click Investigation:** Start investigations with a single button
- **Real-Time Progress:** Watch the AI investigator work
- **Beautiful Results:** Interactive visualizations and reports

### 2. Custom Investigation
- **Full Control:** Create your own investigation cases
- **Flexible Inputs:** Customize all case parameters
  - Customer ID
  - Account ID
  - Alert Type
  - Priority Level
  - Time Period
  - Description
  - Customer Explanation
- **Instant Results:** Run and view results immediately

### 3. Data Explorer
- **Customer Profiles:** View detailed customer information
- **Transaction History:** Analyze account transactions
- **Risk Analysis:** Examine pattern detection results
- **Interactive Charts:** Visualize transaction timelines

### 4. Investigation History
- **Track All Cases:** Keep history of all investigations
- **Statistics Dashboard:** View summary metrics
- **Detailed Review:** Revisit any previous investigation
- **Export Capability:** Download reports in JSON format

## 🎨 User Interface

### Main Components

#### Dashboard
- System status indicators
- API connection status
- Model information
- Quick access navigation

#### Investigation Results Display
- **Risk Gauge:** Visual risk score (0-10 scale)
- **Key Metrics:** SAR status, evidence count, duration
- **Findings:** Organized key findings and evidence
- **Recommendations:** Clear next steps and actions
- **Tool Execution Log:** Transparency into investigation process
- **Reasoning Trace:** Complete AI reasoning for audit

#### Data Visualizations
- Risk score gauge chart
- Evidence severity pie chart
- Transaction timeline bar chart
- Pattern analysis displays

## 🔍 How to Use

### Running a Quick Investigation

1. Select **"Quick Investigation"** from the sidebar
2. Choose a predefined case from the dropdown
3. Review the case details displayed
4. Click **"🔍 Start Investigation"**
5. Watch the progress indicators
6. Review the comprehensive results

### Creating a Custom Investigation

1. Select **"Custom Investigation"** from the sidebar
2. Fill in all case details:
   - Case ID (auto-generated or custom)
   - Customer ID (select or enter)
   - Account ID (select or enter)
   - Alert Type (cash_structuring, wire_transfer, etc.)
   - Priority (low, medium, high, critical)
   - Time period in days
   - Optional amount
   - Alert source
3. Provide a detailed description
4. Add customer explanation (if available)
5. Click **"🚀 Run Custom Investigation"**
6. View results instantly

### Exploring Data

1. Select **"View Data"** from the sidebar
2. Choose data type:
   - **Customer Profiles:** View risk scores, demographics
   - **Transaction History:** See all transactions
   - **Risk Analysis:** Review pattern detection
3. Select specific customer/account
4. Click **"Load"** or **"Analyze"**
5. Explore interactive visualizations

### Reviewing History

1. Select **"Investigation History"** from the sidebar
2. View summary statistics
3. Browse the history table
4. Select a case to view details
5. Download reports as needed

## 📊 Understanding Results

### Risk Scores
- **0-4 (Green):** Low risk - standard monitoring
- **4-6 (Yellow):** Medium risk - enhanced monitoring
- **6-8 (Orange):** High risk - potential SAR filing
- **8-10 (Red):** Critical risk - SAR filing recommended

### Evidence Severity
- **Critical:** Immediate action required
- **High:** Strong indicator of suspicious activity
- **Medium:** Notable concern requiring review
- **Low:** Minor indicator for awareness

### SAR Decision
- **YES:** Suspicious Activity Report filing recommended
- **NO:** No SAR required at this time

## 💡 Tips & Best Practices

### For Best Results:
1. **Provide Detailed Descriptions:** More context = better analysis
2. **Use Appropriate Time Periods:** 14-30 days for patterns
3. **Check Data First:** Use Data Explorer before investigating
4. **Review Tool Executions:** Understand what evidence was gathered
5. **Read Reasoning Trace:** See how the AI reached conclusions

### Performance Optimization:
- The first investigation may take longer (model initialization)
- Subsequent investigations will be faster
- Use the history feature to compare cases
- Export reports for external review

## 🔒 Security & Compliance

### Important Notes:
- ⚠️ **Demo System:** Not for production SAR filing
- 🔐 **API Key:** Keep your OpenAI API key secure
- 📋 **Audit Trail:** All reasoning is logged
- 👤 **Human Review:** Always required for SAR decisions
- 💾 **Data Privacy:** Session state not persisted

### Best Practices:
- Use in secure environment
- Don't share investigation results publicly
- Follow your organization's compliance procedures
- Maintain proper documentation
- Review all AI recommendations

## 🎯 Use Cases

### Training & Education
- Demonstrate AML investigation process
- Train compliance staff
- Educate about suspicious patterns
- Show ReACT framework in action

### Analysis & Testing
- Test detection algorithms
- Compare different scenarios
- Evaluate risk scoring
- Validate investigation approaches

### Rapid Prototyping
- Quickly test case variations
- Experiment with different parameters
- Iterate on investigation logic
- Demo to stakeholders

## 🐛 Troubleshooting

### App Won't Start
```bash
# Check if streamlit is installed
pip install streamlit

# Verify dependencies
pip install -r requirements.txt

# Run with verbose output
streamlit run streamlit_app.py --logger.level=debug
```

### API Key Error
- Ensure `.env` file exists
- Verify `OPENAI_API_KEY` is set correctly
- Check API key has available credits
- Restart the app after updating `.env`

### No Results Displayed
- Check browser console for errors
- Verify data files are present
- Ensure mock_data.py is working
- Try reloading the page

### Slow Performance
- First run initializes models (slower)
- Check internet connection
- Reduce time period for analysis
- Use smaller investigation scope

## 🎨 Customization

### Modify Cases
Edit `streamlit_app.py` and update the `predefined_cases` dictionary:

```python
predefined_cases = {
    "Your Custom Case": {
        "case_id": "CUSTOM_001",
        "customer_id": "YOUR_CUST",
        # ... other parameters
    }
}
```

### Change Styling
Modify the CSS in the `st.markdown()` section:

```python
st.markdown("""
<style>
    /* Your custom CSS here */
</style>
""", unsafe_allow_html=True)
```

### Add New Views
Add new modes in the sidebar radio button and create corresponding sections.

## 📱 Mobile Access

The app is responsive and works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Tablets
- Mobile devices (with some layout adjustments)

For best experience, use desktop with screen width ≥ 1024px.

## 🚀 Deployment

### Local Network Access
```bash
streamlit run streamlit_app.py --server.address=0.0.0.0
```

### Streamlit Cloud (Free)
1. Push code to GitHub
2. Visit share.streamlit.io
3. Connect repository
4. Add secrets (API key)
5. Deploy

### Docker
```bash
docker build -t aml-investigation-app .
docker run -p 8501:8501 aml-investigation-app
```

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Main README](../README.md)
- [Quick Start Guide](QUICKSTART.md)
- [API Documentation](http://localhost:8000/api/v1/docs)

## 🆘 Support

For issues or questions:
- Check this guide first
- Review the main README
- Test with demo cases
- Verify environment setup
- Check GitHub issues

---

**Enjoy your interactive AML Investigation experience! 🎉**

