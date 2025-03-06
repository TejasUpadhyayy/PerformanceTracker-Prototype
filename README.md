# Performance Tracker Prototype





## 📋 Overview

This is a comprehensive prototype for employee performance analytics platform built with Streamlit and Google's Gemini AI. It transforms raw performance data into actionable insights, helping managers and HR professionals make data-driven decisions about their teams.

The application automatically detects relevant metrics from any CSV data structure, visualizes performance trends, and provides AI-powered recommendations for individual and team improvement.

## ✨ Key Features

### Data Analysis
- **Automatic Metric Detection**: Intelligently identifies performance metrics from any CSV structure
- **Team Dashboard**: Comprehensive overview of team performance with key statistics
- **Individual Analysis**: Deep-dive into each employee's performance metrics and trends
- **Temporal Analysis**: Track performance changes over time with trend visualization

### Visualization
- **Interactive Charts**: Explore data through dynamic charts and graphs
- **Color-Coded Tables**: Quickly identify high and low performers
- **Performance Radar**: Visual representation of an employee's strengths and weaknesses
- **Distribution Analysis**: Understand how metrics are distributed across your team

### AI-Powered Insights
- **Performance Assessment**: AI-generated summary of employee performance
- **Improvement Suggestions**: Actionable recommendations for performance enhancement
- **Custom Analysis**: Ask questions about your data and get AI-powered answers
- **Team Improvement Plans**: Structured plans with clear action items

### Export & Sharing
- **Multiple Export Formats**: Download analyses in CSV or Excel format
- **Presentation-Ready**: Generate visual reports for stakeholders

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/performx.git
   cd performx
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Gemini API key** (two options)

   **Option A:** Create a `.streamlit/secrets.toml` file:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   ```

   **Option B:** Enter your API key in the application when prompted

4. **Run the application**
   ```bash
   streamlit run app.py
   ```
   
   For version without AI features:
   ```bash
   streamlit run app_without_gemini.py
   ```

5. **Open the application**
   
   Navigate to http://localhost:8501 in your web browser

## 📊 Data Format

PerformX works with any CSV file containing employee performance data. While it automatically adapts to different formats, optimal results come from files with:

- An employee identifier column
- Performance metric columns (numeric values)
- Optional time-based columns for trend analysis

### Sample Data Structure
```
employee_id,name,department,role,performance_score,sales_target,sales_achieved,...
E001,John Smith,Sales,Senior Associate,78,100000,95000,...
E002,Emily Johnson,Marketing,Manager,85,80000,92000,...
```

## 🔧 Configuration Options

### Display Options
- **Simple Table**: Clean, straightforward data presentation
- **Highlight Top Performers**: Emphasize your team's strongest contributors
- **Color-Coded Table**: Visualize performance levels with color intensity

### Analysis Controls
- Filter data by department, role, or time period
- Select specific metrics for focused analysis
- Adjust visualization parameters for customized views

## 🔍 Use Cases

- **Performance Reviews**: Gather objective data for employee evaluations
- **Team Assessment**: Understand overall team performance and dynamics
- **Improvement Planning**: Develop targeted strategies for team enhancement
- **Resource Allocation**: Identify where training or support is most needed
- **Succession Planning**: Recognize high performers for advancement opportunities

## 📑 Project Structure

```
performx/
│
├── app.py                     # Main application with Gemini AI
├── app_without_gemini.py      # Alternative version without AI dependency
├── requirements.txt           # Package dependencies
│
├── .streamlit/                # Streamlit configuration
│   └── secrets.toml           # API keys (create this file)
│
└── data/                      # Sample data files
    └── sample_employee_data.csv  # Example data for testing
```

## 🛣️ Roadmap

Future enhancements planned for PerformX:

1. **Team & Department Comparison Views**
   - Enhanced visualizations for cross-department analysis
   - Manager effectiveness metrics

2. **Enhanced Export & Reporting**
   - PDF report generation
   - Scheduled email reports
   - Presentation-ready exports

3. **Performance Trends Analysis**
   - Predictive performance forecasting
   - Anomaly detection for unusual patterns
   - Year-over-year comparison tools

4. **Data Import Flexibility**
   - Support for multiple file formats
   - Integration with HR platforms
   - Real-time data connectors

5. **User Authentication**
   - Role-based access control
   - Secure data handling
   - Multi-tenant support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request






