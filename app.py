import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import google.generativeai as genai
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Performance Tracker Prototype",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        font-weight: 500;
    }
    .metric-card {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .employee-section {
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        gap: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Gemini API
def initialize_gemini():
    # Default API key - you provided this for the application
    default_api_key = "AIzaSyDhk5do6PMKbBGmme7o6bJB3IMxKZMd_mo"
    
    # First try to get API key from session state
    api_key = st.session_state.get("api_key", "")
    
    # If not in session state, try to get from secrets
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", default_api_key)
        except:
            # If secrets file doesn't exist, use the default API key
            api_key = default_api_key
    
    # Configure Gemini with the API key
    try:
        genai.configure(api_key=api_key)
        st.session_state.api_key = api_key
        return True
    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}")
        st.info("You can enter a different API key below if needed:")
        new_api_key = st.text_input("Enter your Gemini API Key:", type="password")
        if st.button("Save API Key"):
            st.session_state.api_key = new_api_key
            genai.configure(api_key=new_api_key)
            st.success("API Key saved successfully!")
            return True
        return False

# Function to get AI insights
def get_ai_insights(employee_data, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error getting AI insights: {e}")
        return "Unable to generate insights at this time."

# Function to extract performance metrics
def extract_performance_metrics(df):
    """
    Dynamically extract key performance metrics from the dataframe
    """
    metrics = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Try to identify key metrics based on column names
    possible_metrics = {
        'performance': ['performance', 'score', 'rating', 'evaluation', 'assessment', 'review'],
        'targets': ['target', 'goal', 'objective', 'quota'],
        'sales': ['sales', 'revenue', 'deals', 'conversion'],
        'attendance': ['attendance', 'presence', 'absence', 'leave'],
        'productivity': ['productivity', 'output', 'efficiency', 'tasks', 'completed'],
        'quality': ['quality', 'errors', 'accuracy', 'defects', 'precision']
    }
    
    for metric_type, keywords in possible_metrics.items():
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in keywords) and col in numeric_cols:
                metrics[metric_type] = col
                break
    
    # If no specific metrics found, use available numeric columns
    if not metrics and numeric_cols:
        for i, col in enumerate(numeric_cols[:min(6, len(numeric_cols))]):
            metric_types = list(possible_metrics.keys())
            if i < len(metric_types):
                metrics[metric_types[i]] = col
            else:
                metrics[f'metric_{i+1}'] = col
    
    return metrics

# Function to analyze employee data
def analyze_employee_data(df, employee_id, metrics):
    """
    Analyze individual employee data and generate insights
    """
    employee_data = df[df['employee_id'] == employee_id].to_dict('records')[0]
    
    # Prepare data for AI analysis
    metric_details = []
    for metric_type, col_name in metrics.items():
        if col_name in employee_data:
            metric_details.append(f"{metric_type.capitalize()}: {employee_data[col_name]}")
    
    # Create a prompt for Gemini
    prompt = f"""
    Analyze this employee's performance data and provide concise, actionable insights and improvement suggestions:
    
    Employee ID: {employee_id}
    {', '.join([f"{k}: {employee_data.get(k, 'N/A')}" for k in employee_data if k != 'employee_id'])}
    
    Key metrics:
    {', '.join(metric_details)}
    
    Please provide:
    1. A brief assessment of their performance (2-3 sentences)
    2. 3 specific strengths based on the data
    3. 2-3 improvement areas with actionable suggestions
    4. A performance rating on a scale of 1-10
    """
    
    analysis = get_ai_insights(employee_data, prompt)
    return analysis

# Main app function
def main():
    st.markdown('<p class="main-header">Performance Tracker Prototype</p>', unsafe_allow_html=True)
    
    # Initialize Gemini API
    api_initialized = initialize_gemini()
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your employee performance data (CSV)", type="csv")
    
    if uploaded_file is not None:
        # Load and display data
        df = pd.read_csv(uploaded_file)
        
        # Save original dataframe
        if 'original_df' not in st.session_state:
            st.session_state.original_df = df.copy()
        
        # Basic data cleaning
        # Convert column names to lowercase and replace spaces with underscores
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # Try to identify employee ID column
        employee_id_col = None
        for col in df.columns:
            if 'id' in col.lower() or 'employee' in col.lower():
                employee_id_col = col
                break
        
        if not employee_id_col and len(df.columns) > 0:
            employee_id_col = df.columns[0]  # Use first column as fallback
        
        if employee_id_col:
            df.rename(columns={employee_id_col: 'employee_id'}, inplace=True)
            employee_id_col = 'employee_id'
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "👤 Individual Analysis", "🔍 AI Insights"])
        
        with tab1:
            st.markdown('<p class="sub-header">Team Performance Overview</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            # Extract metrics
            metrics = extract_performance_metrics(df)
            
            with col1:
                # Summary statistics
                st.markdown("### Key Metrics")
                metrics_df = pd.DataFrame()
                
                for metric_type, col_name in metrics.items():
                    if col_name in df.columns:
                        metrics_df[metric_type.capitalize()] = [
                            f"Avg: {df[col_name].mean():.2f}",
                            f"Min: {df[col_name].min():.2f}",
                            f"Max: {df[col_name].max():.2f}"
                        ]
                
                st.dataframe(metrics_df.T)
            
            with col2:
                # Distribution plot for a key metric
                st.markdown("### Performance Distribution")
                if metrics:
                    main_metric = next(iter(metrics.values()))
                    if main_metric in df.columns:
                        fig = px.histogram(df, x=main_metric, nbins=10, 
                                           title=f"Distribution of {main_metric.replace('_', ' ').title()}")
                        st.plotly_chart(fig, use_container_width=True)
            
            # Team performance table
            st.markdown("### Team Performance Table")
            
            # Get metric columns that exist in the dataframe
            valid_metric_cols = [col for col in metrics.values() if col in df.columns]
            
            # Add display options
            display_option = st.radio(
                "Choose display style:",
                ["Simple Table", "Highlight Top Performers", "Color-Coded Table"],
                horizontal=True
            )
            
            if display_option == "Simple Table":
                # Simple display without styling
                st.dataframe(df, use_container_width=True)
                
            elif display_option == "Highlight Top Performers":
                # Let user select which metric to highlight
                if valid_metric_cols:
                    metric_to_highlight = st.selectbox(
                        "Select metric to highlight top performers:",
                        valid_metric_cols
                    )
                    
                    # Number of top performers to show
                    top_n = st.slider("Number of top performers to highlight:", 1, 10, 5)
                    
                    # Display top performers
                    top_performers = df.sort_values(by=metric_to_highlight, ascending=False).head(top_n)
                    st.subheader(f"Top {top_n} Performers by {metric_to_highlight}")
                    st.dataframe(top_performers, use_container_width=True)
                    
                    # Display all data
                    st.subheader("All Team Data")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("No valid metric columns found for highlighting top performers.")
                    st.dataframe(df, use_container_width=True)
                
            elif display_option == "Color-Coded Table":
                # Create a custom colored table using HTML
                if valid_metric_cols:
                    # Function to create custom HTML table with color coding
                    def create_colored_table(dataframe, metrics_cols):
                        # Start HTML table
                        html = "<table style='width:100%; border-collapse: collapse;'>"
                        
                        # Header row
                        html += "<tr>"
                        for col in dataframe.columns:
                            html += f"<th style='text-align: left; padding: 8px; background-color: #f1f1f1; border: 1px solid #ddd;'>{col}</th>"
                        html += "</tr>"
                        
                        # Data rows
                        for idx, row in dataframe.iterrows():
                            html += "<tr>"
                            for col in dataframe.columns:
                                cell_value = row[col]
                                cell_style = "border: 1px solid #ddd; padding: 8px;"
                                
                                # Apply color styling to metric columns
                                if col in metrics_cols and pd.api.types.is_numeric_dtype(dataframe[col]):
                                    min_val = dataframe[col].min()
                                    max_val = dataframe[col].max()
                                    
                                    # Avoid division by zero
                                    if max_val > min_val:
                                        try:
                                            ratio = (cell_value - min_val) / (max_val - min_val)
                                            
                                            # Generate color (green for high values)
                                            intensity = int(255 * ratio)
                                            cell_style += f"background-color: rgba(0, {intensity}, 0, 0.2);"
                                            
                                            # Make high values bold
                                            if ratio > 0.8:
                                                cell_style += "font-weight: bold;"
                                        except:
                                            # Handle any calculation errors
                                            pass
                                
                                html += f"<td style='{cell_style}'>{cell_value}</td>"
                            html += "</tr>"
                        
                        html += "</table>"
                        return html
                    
                    # Create and display the colored table
                    colored_table = create_colored_table(df, valid_metric_cols)
                    st.markdown(colored_table, unsafe_allow_html=True)
                    
                    # Show which metrics are color-coded
                    st.caption(f"Color intensity indicates relative performance across: {', '.join(valid_metric_cols)}")
                else:
                    st.error("No valid metric columns found for color coding.")
                    st.dataframe(df, use_container_width=True)
            
            # Generate team insights using AI if API is initialized
            if api_initialized:
                with st.expander("🧠 Team Performance Insights"):
                    team_prompt = f"""
                    Analyze this team's performance data and provide concise, actionable insights:
                    
                    Team size: {len(df)}
                    Key metrics: {', '.join([f"{k.capitalize()}: Avg={df[v].mean():.2f}, Min={df[v].min():.2f}, Max={df[v].max():.2f}" for k, v in metrics.items() if v in df.columns])}
                    
                    Please provide:
                    1. A brief assessment of team performance (3-4 sentences)
                    2. Top performance trends 
                    3. 2-3 team improvement suggestions
                    """
                    
                    with st.spinner("Generating team insights..."):
                        team_insights = get_ai_insights(df, team_prompt)
                        st.markdown(team_insights)
        
        with tab2:
            st.markdown('<p class="sub-header">Individual Employee Analysis</p>', unsafe_allow_html=True)
            
            # Employee selector
            if employee_id_col and employee_id_col in df.columns:
                employee_ids = df[employee_id_col].unique().tolist()
                selected_employee = st.selectbox("Select Employee", employee_ids)
                
                if selected_employee:
                    employee_data = df[df[employee_id_col] == selected_employee]
                    
                    # Display employee information
                    col1, col2 = st.columns([2, 3])
                    
                    with col1:
                        st.markdown("### Employee Details")
                        details_to_show = {}
                        non_metric_cols = [col for col in df.columns if col not in metrics.values() and col != employee_id_col]
                        for col in non_metric_cols[:5]:  # Show first 5 non-metric columns
                            details_to_show[col.replace('_', ' ').title()] = employee_data[col].iloc[0]
                        
                        for k, v in details_to_show.items():
                            st.markdown(f"**{k}:** {v}")
                    
                    with col2:
                        st.markdown("### Performance Metrics")
                        
                        # Create radar chart for performance metrics
                        performance_metrics = {}
                        for metric_type, col_name in metrics.items():
                            if col_name in employee_data.columns:
                                performance_metrics[metric_type.capitalize()] = float(employee_data[col_name].iloc[0])
                        
                        if performance_metrics:
                            categories = list(performance_metrics.keys())
                            values = list(performance_metrics.values())
                            
                            # Normalize values for radar chart
                            max_values = {metric: df[col].max() for metric, col in metrics.items()}
                            normalized_values = [values[i] / max_values[categories[i].lower()] for i in range(len(values))]
                            
                            # Add the first value at the end to close the radar chart
                            categories.append(categories[0])
                            normalized_values.append(normalized_values[0])
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatterpolar(
                                r=normalized_values,
                                theta=categories,
                                fill='toself',
                                name='Performance'
                            ))
                            
                            fig.update_layout(
                                polar=dict(
                                    radialaxis=dict(
                                        visible=True,
                                        range=[0, 1]
                                    )
                                ),
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # AI-generated insights for the employee
                    if api_initialized:
                        st.markdown("### AI-Powered Performance Analysis")
                        with st.spinner("Analyzing employee data..."):
                            analysis = analyze_employee_data(df, selected_employee, metrics)
                            st.markdown(analysis)
                
                # Historical comparison if available
                if 'date' in df.columns or 'period' in df.columns or 'month' in df.columns or 'quarter' in df.columns:
                    time_col = next((col for col in df.columns if col in ['date', 'period', 'month', 'quarter']), None)
                    if time_col:
                        st.markdown("### Historical Performance")
                        for metric_type, col_name in metrics.items():
                            if col_name in df.columns:
                                fig = px.line(df, x=time_col, y=col_name, title=f"{metric_type.capitalize()} Trend")
                                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown('<p class="sub-header">AI-Powered Team Insights</p>', unsafe_allow_html=True)
            
            if api_initialized:
                # Custom analysis
                st.markdown("### Ask AI about your team data")
                user_prompt = st.text_area("Enter your question about the data:", 
                                        "What are the top 3 performance issues in the team and how can we address them?")
                
                if st.button("Generate Insights"):
                    with st.spinner("Analyzing..."):
                        # Create a comprehensive prompt with data summary
                        ai_prompt = f"""
                        Based on this employee performance data, answer the following question:
                        
                        "{user_prompt}"
                        
                        Data summary:
                        - Total employees: {len(df)}
                        - Columns available: {', '.join(df.columns.tolist())}
                        - Key metrics: {', '.join([f"{k.capitalize()}: Avg={df[v].mean():.2f}, Min={df[v].min():.2f}, Max={df[v].max():.2f}" for k, v in metrics.items() if v in df.columns])}
                        
                        Please provide concrete, data-backed insights and actionable recommendations.
                        """
                        
                        insights = get_ai_insights(df, ai_prompt)
                        st.markdown(insights)
                
                # Performance improvement recommendations
                st.markdown("### Team Performance Improvement Plan")
                with st.spinner("Generating improvement plan..."):
                    improvement_prompt = f"""
                    Based on this team's performance data, create a structured improvement plan:
                    
                    Team data summary:
                    - Total employees: {len(df)}
                    - Key metrics: {', '.join([f"{k.capitalize()}: Avg={df[v].mean():.2f}, Min={df[v].min():.2f}, Max={df[v].max():.2f}" for k, v in metrics.items() if v in df.columns])}
                    
                    Please provide:
                    1. Top 3 team strengths to leverage
                    2. Top 3 improvement areas with specific action items
                    3. Key performance indicators to track progress
                    4. A 30-60-90 day implementation timeline
                    
                    Format as a clear, actionable plan.
                    """
                    
                    improvement_plan = get_ai_insights(df, improvement_prompt)
                    st.markdown(improvement_plan)
            else:
                st.warning("Please enter your Gemini API key to unlock AI-powered insights.")
            
            # Export options
            st.markdown("### Export Options")
            export_format = st.selectbox("Select export format:", ["CSV", "Excel"])
            
            if st.button("Export Data and Insights"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if export_format == "CSV":
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"performx_analysis_{timestamp}.csv",
                        mime="text/csv"
                    )
                else:
                    # Create a buffer to store Excel file
                    buffer = StringIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, sheet_name='Performance Data', index=False)
                    
                    st.download_button(
                        label="Download Excel",
                        data=buffer.getvalue(),
                        file_name=f"performx_analysis_{timestamp}.xlsx",
                        mime="application/vnd.ms-excel"
                    )

# Run the app
if __name__ == "__main__":
    main()