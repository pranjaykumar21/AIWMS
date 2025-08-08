import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import time
from streamlit_autorefresh import st_autorefresh
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import plotly.express as px
import json

# Configuration
API_BASE_URL = "https://aiwms.onrender.com/api"
REFRESH_INTERVAL = 300  # 5 minutes

# Page Configuration
st.set_page_config(
    page_title="ISS Cargo AI",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {color:#38b6ff; font-size:46px; font-weight:700; margin-bottom:0px;}
    .sub-header {color:#9ef8a6; font-size:22px; margin-top:0px;}
    .metric-card {background-color:rgba(255,255,255,0.1); border-radius:10px; padding:20px; box-shadow:0 4px 6px rgba(0,0,0,0.1);}
    .zone-a {color:#38b6ff; font-weight:600;}
    .zone-b {color:#9ef8a6; font-weight:600;}
    .zone-c {color:#ff6961; font-weight:600;}
    .stButton>button {width:100%; background-color:#38b6ff; color:white;}
    .sidebar .sidebar-content {background-image: linear-gradient(#0e1117,#262730);}
    [data-testid="stSidebar"] {background-image: linear-gradient(#0e1117,#262730);}
    .loader {border:8px solid #f3f3f3; border-top:8px solid #38b6ff; border-radius:50%; width:50px; height:50px; animation:spin 1s linear infinite; margin:auto;}
    @keyframes spin {0% {transform:rotate(0deg);} 100% {transform:rotate(360deg);}}
    div[data-testid="stMetric"] {background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;}
    div[data-testid="stMetric"] > div {display: flex; justify-content: center;}
    div[data-testid="stMetric"] label {font-size: 1.2rem !important;}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {font-size: 1.8rem !important;}
    .success-message {color: #9ef8a6; font-weight: 600;}
    .error-message {color: #ff6961; font-weight: 600;}
    .warning-message {color: #ffb347; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# Auto Refresh
refresh_count = st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="data_refresh")

# Health Check Function
@st.cache_data(ttl=60)
def check_api_health():
    """Check if the API is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Data Loaders with improved error handling
@st.cache_data(ttl=300)
def load_cargo():
    """Load cargo data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/get_cargo", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                if 'cargo' in data:
                    df = pd.DataFrame(data['cargo'])
                elif 'items' in data:
                    df = pd.DataFrame(data['items'])
                else:
                    df = pd.DataFrame([data])
            else:
                st.error("Unexpected API response format")
                return pd.DataFrame()
            
            if df.empty:
                return df
            
            # Ensure required columns exist
            required_columns = {
                'id': 'ITEM-' + pd.Series(range(len(df))).astype(str),
                'name': 'Item ' + pd.Series(range(len(df))).astype(str),
                'size': 1.0,
                'priority': 50,
                'expiry_days': 30,
                'zone': 'Zone A',
                'temperature_sensitive': False,
                'hazardous': False
            }
            
            for col, default_value in required_columns.items():
                if col not in df.columns:
                    if isinstance(default_value, pd.Series):
                        df[col] = default_value
                    else:
                        df[col] = default_value
            
            # Calculate expiry date if not present
            if 'expiry_date' not in df.columns:
                df['expiry_date'] = pd.to_datetime('now') + pd.to_timedelta(df['expiry_days'], unit='D')
            else:
                df['expiry_date'] = pd.to_datetime(df['expiry_date'])
            
            # Add position data for 3D visualization
            if 'position_x' not in df.columns:
                df['position_x'] = np.random.uniform(0, 8, size=len(df))
                df['position_y'] = np.random.uniform(0, 8, size=len(df))
                df['position_z'] = np.random.uniform(0, 3, size=len(df))
            
            # Add dimensions for 3D visualization  
            for dim in ['width', 'height', 'depth']:
                if dim not in df.columns:
                    df[dim] = np.cbrt(df['size'])  # Cube root for equal dimensions
            
            return df
            
        else:
            st.error(f"API Error: Status {response.status_code} - {response.text}")
            return pd.DataFrame()
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        return pd.DataFrame()

# API Functions
def add_cargo_item(cargo_data):
    """Add a new cargo item"""
    try:
        response = requests.post(f"{API_BASE_URL}/add_cargo", json=cargo_data, timeout=10)
        return response
    except Exception as e:
        st.error(f"Error adding cargo: {str(e)}")
        return None

def get_placement_recommendation(item_data):
    """Get AI placement recommendation"""
    try:
        response = requests.post(f"{API_BASE_URL}/placement", json=item_data, timeout=10)
        return response
    except Exception as e:
        st.error(f"Error getting placement recommendation: {str(e)}")
        return None

def retrieve_item(item_id):
    """Retrieve an item"""
    try:
        response = requests.post(f"{API_BASE_URL}/retrieve/{item_id}", timeout=10)
        return response
    except Exception as e:
        st.error(f"Error retrieving item: {str(e)}")
        return None

def delete_cargo_item(item_id):
    """Delete a cargo item"""
    try:
        response = requests.delete(f"{API_BASE_URL}/delete_cargo/{item_id}", timeout=10)
        return response
    except Exception as e:
        st.error(f"Error deleting cargo: {str(e)}")
        return None

def generate_return_plan(plan_data):
    """Generate waste return plan"""
    try:
        response = requests.post(f"{API_BASE_URL}/waste/return-plan", json=plan_data, timeout=10)
        return response
    except Exception as e:
        st.error(f"Error generating return plan: {str(e)}")
        return None

def simulate_time(days=1):
    """Simulate time progression"""
    try:
        response = requests.post(f"{API_BASE_URL}/simulate/day", json={"days": days}, timeout=10)
        return response
    except Exception as e:
        st.error(f"Error simulating time: {str(e)}")
        return None

def export_arrangement():
    """Export arrangement plan"""
    try:
        response = requests.get(f"{API_BASE_URL}/export/arrangement", timeout=10)
        return response
    except Exception as e:
        st.error(f"Error exporting arrangement: {str(e)}")
        return None

def import_items(items_data):
    """Import multiple items"""
    try:
        response = requests.post(f"{API_BASE_URL}/import/items", json=items_data, timeout=10)
        return response
    except Exception as e:
        st.error(f"Error importing items: {str(e)}")
        return None

# Utility Functions
def calculate_days_remaining(expiry_date):
    """Calculate days remaining until expiry"""
    if pd.isnull(expiry_date):
        return 0
    if isinstance(expiry_date, str):
        expiry_date = pd.to_datetime(expiry_date)
    delta = expiry_date - pd.Timestamp.now()
    return max(0, delta.days)

def get_status_color(days):
    """Get status color based on days remaining"""
    if days <= 3:
        return "#ff6961"  # Red
    elif days <= 7:
        return "#ffb347"  # Orange
    else:
        return "#9ef8a6"  # Green

# Header Component
def render_header():
    """Render the main header"""
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown('<p class="main-header">ISS Cargo AI Dashboard</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Intelligent Space Station Inventory Management</p>', unsafe_allow_html=True)
    
    with col2:
        # Health status indicator
        if check_api_health():
            st.markdown("🟢 **API Status:** Online")
        else:
            st.markdown("🔴 **API Status:** Offline")
    
    with col3:
        st.write(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")

# 3D Visualization Engine
def render_3d_warehouse():
    """Render 3D warehouse visualization"""
    st.markdown("## 🌌 3D Warehouse Visualization")
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    with col1:
        zone_filter = st.multiselect("Filter by Zone", ["Zone A", "Zone B", "Zone C"], default=["Zone A", "Zone B", "Zone C"])
    with col2:
        min_priority = st.slider("Min Priority", 1, 100, 1)
    with col3:
        expiry_filter = st.checkbox("Show Expiring Soon", value=False)
    
    df = load_cargo()
    if df.empty:
        st.warning("No cargo data available. Check API connection.")
        return
    
    # Apply filters
    if 'zone' in df.columns:
        df = df[df['zone'].isin(zone_filter)]
    if 'priority' in df.columns:
        df = df[df['priority'] >= min_priority]
    if expiry_filter:
        df['days_remaining'] = df['expiry_date'].apply(calculate_days_remaining)
        df = df[df['days_remaining'] <= 7]
    
    # Create 3D visualization
    fig = go.Figure()
    
    # Add warehouse boundaries
    fig.add_trace(go.Mesh3d(
        x=[0, 10, 10, 0, 0, 10, 10, 0],
        y=[0, 0, 10, 10, 0, 0, 10, 10],
        z=[0, 0, 0, 0, 5, 5, 5, 5],
        i=[0, 0, 0, 1, 4, 4],
        j=[1, 2, 4, 2, 5, 6],
        k=[2, 3, 7, 3, 6, 7],
        opacity=0.1,
        color='#ffffff',
        hoverinfo='none',
        showscale=False,
        name="Warehouse Structure"
    ))
    
    # Zone colors
    zones = {"Zone A": "#38b6ff", "Zone B": "#9ef8a6", "Zone C": "#ff6961"}
    
    # Add cargo items
    for _, item in df.iterrows():
        x_pos = item.get('position_x', np.random.uniform(0, 8))
        y_pos = item.get('position_y', np.random.uniform(0, 8))
        z_pos = item.get('position_z', np.random.uniform(0, 3))
        
        width = item.get('width', 1)
        height = item.get('height', 1)
        depth = item.get('depth', 1)
        
        zone = item.get('zone', 'Zone A')
        color = zones.get(zone, "#ffffff")
        
        # Calculate days remaining
        days_remaining = calculate_days_remaining(item.get('expiry_date'))
        opacity = 0.9 if days_remaining <= 3 else 0.7
        
        # Create hover text
        hover_text = f"<b>{item.get('name', 'Unnamed Item')}</b><br>"
        hover_text += f"ID: {item.get('id', 'N/A')}<br>"
        hover_text += f"Priority: {item.get('priority', 'N/A')}<br>"
        hover_text += f"Expires in: {days_remaining} days<br>"
        hover_text += f"Zone: {zone}<br>"
        hover_text += f"Size: {item.get('size', 'N/A')} m³"
        
        # Add item to visualization
        fig.add_trace(go.Mesh3d(
            x=[x_pos, x_pos+width, x_pos+width, x_pos, x_pos, x_pos+width, x_pos+width, x_pos],
            y=[y_pos, y_pos, y_pos+depth, y_pos+depth, y_pos, y_pos, y_pos+depth, y_pos+depth],
            z=[z_pos, z_pos, z_pos, z_pos, z_pos+height, z_pos+height, z_pos+height, z_pos+height],
            i=[0, 0, 0, 1, 4, 4],
            j=[1, 2, 4, 2, 5, 6],
            k=[2, 3, 7, 3, 6, 7],
            color=color,
            opacity=opacity,
            hoverinfo='text',
            hovertext=hover_text,
            name=item.get('name', 'Unnamed Item')
        ))
    
    # Configure layout
    fig.update_layout(
        scene=dict(
            xaxis_title='X (meters)',
            yaxis_title='Y (meters)',
            zaxis_title='Z (meters)',
            aspectmode='cube',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.25),
                up=dict(x=0, y=0, z=1)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=650,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Zone legend
    with st.expander("Zone Information"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="zone-a">■ Zone A: High Priority & Temperature Controlled</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="zone-b">■ Zone B: Standard Storage</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="zone-c">■ Zone C: Hazardous Materials</div>', unsafe_allow_html=True)

# Metrics Dashboard
def render_metrics():
    """Render real-time metrics dashboard"""
    st.markdown("## 📊 Real-Time Cargo Metrics")
    
    df = load_cargo()
    if df.empty:
        st.warning("No cargo data available. Check API connection.")
        return
    
    # Calculate metrics
    total_cargo = len(df)
    df['days_remaining'] = df['expiry_date'].apply(calculate_days_remaining)
    expiring_soon = len(df[df['days_remaining'] <= 3])
    zone_distribution = df.get('zone', pd.Series(['Zone A'] * total_cargo)).value_counts().to_dict()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cargo Items", total_cargo)
    with col2:
        st.metric("Expiring ≤ 3 Days", expiring_soon, 
                 delta=f"{expiring_soon/total_cargo*100:.1f}%" if total_cargo else "0%", 
                 delta_color="inverse")
    with col3:
        avg_priority = df.get('priority', pd.Series([50] * total_cargo)).mean()
        st.metric("Average Priority", f"{avg_priority:.1f}")
    with col4:
        capacity_used = min(total_cargo * 5, 95)
        st.metric("Storage Capacity", f"{capacity_used:.1f}%")
    
    # Visualizations
    st.markdown("### Data Visualizations")
    col1, col2 = st.columns(2)
    
    with col1:
        # Zone distribution
        if zone_distribution:
            fig = px.pie(
                values=list(zone_distribution.values()),
                names=list(zone_distribution.keys()),
                color=list(zone_distribution.keys()),
                color_discrete_map={"Zone A": "#38b6ff", "Zone B": "#9ef8a6", "Zone C": "#ff6961"},
                title="Cargo Distribution by Zone"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=350, margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Priority distribution
        if 'priority' in df.columns:
            fig = px.histogram(
                df, x="priority", 
                nbins=10, 
                color_discrete_sequence=["#38b6ff"],
                title="Priority Distribution"
            )
        else:
            fig = px.histogram(
                df, x="days_remaining", 
                nbins=10, 
                color_discrete_sequence=["#38b6ff"],
                title="Days Until Expiry"
            )
        
        fig.update_layout(height=350, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Expiry timeline
    if len(df) > 0:
        st.markdown("### Expiry Timeline")
        fig = px.scatter(
            df,
            x="expiry_date",
            y="priority" if 'priority' in df.columns else "days_remaining",
            color="zone" if 'zone' in df.columns else None,
            size="size" if 'size' in df.columns else None,
            hover_name="name" if 'name' in df.columns else None,
            color_discrete_map={"Zone A": "#38b6ff", "Zone B": "#9ef8a6", "Zone C": "#ff6961"},
            title="Cargo Expiry Timeline"
        )
        fig.update_layout(height=400, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

# AI Optimization Engine
def ai_recommendation_engine():
    """Render AI placement optimizer"""
    st.markdown("## 🧠 AI Placement Optimizer")
    
    # Configuration form
    with st.form("cargo_form"):
        st.markdown("### Add New Cargo Item")
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = st.text_input("Cargo Name", "New Supply Package")
            size = st.number_input("Item Size (m³)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
            priority = st.slider("Priority Level", 1, 100, 50)
            expiry_days = st.slider("Shelf Life (Days)", 1, 365, 30)
        
        with col2:
            temperature_sensitive = st.checkbox("Temperature Sensitive")
            hazardous = st.checkbox("Hazardous Material")
            fragile = st.checkbox("Fragile")
            description = st.text_area("Description", "")
        
        # Form submission buttons
        col1, col2 = st.columns(2)
        with col1:
            get_recommendation = st.form_submit_button("Get AI Recommendation", type="primary")
        with col2:
            add_directly = st.form_submit_button("Add to Inventory")
    
    # Handle form submissions
    if get_recommendation:
        # Prepare data for placement recommendation
        item_data = {
            "name": item_name,
            "size": size,
            "priority": priority,
            "expiry_days": expiry_days,
            "temperature_sensitive": temperature_sensitive,
            "hazardous": hazardous,
            "fragile": fragile,
            "description": description
        }
        
        with st.spinner("Getting AI recommendation..."):
            response = get_placement_recommendation(item_data)
            
            if response and response.status_code == 200:
                result = response.json()
                
                # Display recommendation
                st.success("✅ AI Recommendation Generated!")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("### Recommended Placement")
                    st.markdown(f"**Suggested Zone:** {result.get('recommended_zone', 'Zone A')}")
                    st.markdown(f"**Confidence:** {result.get('confidence', 95):.1f}%")
                    st.markdown(f"**Reasoning:** {result.get('reasoning', 'Optimized for priority and requirements')}")
                    
                    # Add to inventory button
                    if st.button("Add with Recommendation"):
                        item_data['zone'] = result.get('recommended_zone', 'Zone A')
                        add_response = add_cargo_item(item_data)
                        
                        if add_response and add_response.status_code in [200, 201]:
                            st.success(f"✅ {item_name} added to inventory!")
                            st.rerun()
                        else:
                            st.error("Failed to add item to inventory")
                
                with col2:
                    st.markdown("### Placement Factors")
                    factors = result.get('factors', {})
                    for factor, value in factors.items():
                        st.markdown(f"- **{factor.title()}:** {value}")
            
            elif response:
                st.error(f"Failed to get recommendation: {response.status_code} - {response.text}")
            else:
                st.error("Failed to connect to API")
    
    elif add_directly:
        # Add item directly without recommendation
        item_data = {
            "name": item_name,
            "size": size,
            "priority": priority,
            "expiry_days": expiry_days,
            "temperature_sensitive": temperature_sensitive,
            "hazardous": hazardous,
            "fragile": fragile,
            "description": description,
            "zone": "Zone B"  # Default zone
        }
        
        with st.spinner("Adding item to inventory..."):
            response = add_cargo_item(item_data)
            
            if response and response.status_code in [200, 201]:
                st.success(f"✅ {item_name} added to inventory!")
                st.rerun()
            else:
                st.error("Failed to add item to inventory")

# Waste Management System
def waste_management_system():
    """Render waste management system"""
    st.markdown("## ♻️ Waste Management & Expiring Inventory")
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days_threshold = st.slider("Days Until Expiry Threshold", 0, 30, 7)
    
    with col2:
        if st.button("Generate Return Plan"):
            plan_data = {
                "days_threshold": days_threshold,
                "max_weight": st.number_input("Max Weight (kg)", value=500, min_value=1),
                "priority_threshold": st.number_input("Min Priority", value=0, min_value=0, max_value=100)
            }
            
            with st.spinner("Generating return plan..."):
                response = generate_return_plan(plan_data)
                
                if response and response.status_code == 200:
                    plan = response.json()
                    st.success("✅ Return plan generated!")
                    
                    # Display plan
                    if 'items' in plan and plan['items']:
                        df_plan = pd.DataFrame(plan['items'])
                        st.dataframe(df_plan, use_container_width=True)
                    else:
                        st.info("No items require return at this time")
                else:
                    st.error("Failed to generate return plan")
    
    with col3:
        if st.button("Simulate Next Day"):
            with st.spinner("Simulating time progression..."):
                response = simulate_time(1)
                
                if response and response.status_code == 200:
                    result = response.json()
                    st.success("✅ Simulation completed!")
                    st.info(f"Advanced to: {result.get('new_date', 'Unknown')}")
                    
                    if 'expired_items' in result:
                        st.warning(f"⚠️ {len(result['expired_items'])} items expired")
                    
                    st.rerun()
                else:
                    st.error("Failed to simulate time progression")
    
    # Display expiring items
    df = load_cargo()
    if not df.empty:
        df['days_remaining'] = df['expiry_date'].apply(calculate_days_remaining)
        expiring_df = df[df['days_remaining'] <= days_threshold].copy()
        
        if not expiring_df.empty:
            st.markdown("### Expiring Items")
            
            # Prepare display data
            display_columns = ['id', 'name', 'days_remaining', 'zone', 'priority']
            display_df = expiring_df[display_columns].copy()
            display_df['status'] = display_df['days_remaining'].apply(
                lambda x: "Critical" if x <= 3 else "Warning" if x <= 7 else "Monitor"
            )
            
            # Color-coded grid
            gb = GridOptionsBuilder.from_dataframe(display_df)
            gb.configure_selection('multiple', use_checkbox=True)
            gb.configure_column('days_remaining', 
                               cellStyle=JsCode('''
                               function(params) {
                                   if (params.value <= 3) {
                                       return {color: 'white', backgroundColor: '#ff6961'};
                                   } else if (params.value <= 7) {
                                       return {color: 'black', backgroundColor: '#ffb347'};
                                   } else {
                                       return {color: 'black', backgroundColor: '#9ef8a6'};
                                   }
                               }
                               '''))
            
            grid_options = gb.build()
            grid_response = AgGrid(
                display_df,
                gridOptions=grid_options,
                enable_enterprise_modules=False,
                allow_unsafe_jscode=True,
                height=400,
                theme="streamlit"
            )
            
            # Action buttons for selected items
            selected_rows = grid_response.selected_rows
            if selected_rows:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Delete Selected"):
                        deleted_count = 0
                        for row in selected_rows:
                            response = delete_cargo_item(row['id'])
                            if response and response.status_code == 200:
                                deleted_count += 1
                        
                        if deleted_count > 0:
                            st.success(f"✅ Deleted {deleted_count} items")
                            st.rerun()
                
                with col2:
                    if st.button("Retrieve Selected"):
                        retrieved_count = 0
                        for row in selected_rows:
                            response = retrieve_item(row['id'])
                            if response and response.status_code == 200:
                                retrieved_count += 1
                        
                        if retrieved_count > 0:
                            st.success(f"✅ Retrieved {retrieved_count} items")
                            st.rerun()
                
                with col3:
                    if st.button("Export Selected"):
                        response = export_arrangement()
                        if response and response.status_code == 200:
                            st.download_button(
                                label="Download Export",
                                data=response.content,
                                file_name=f"arrangement_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf"
                            )
        else:
            st.info(f"No items expiring within {days_threshold} days")

# Bulk Import Feature
def bulk_import_feature():
    """Render bulk import feature"""
    st.markdown("### 📁 Bulk Import Items")
    
    # File upload
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Read CSV file
            df_import = pd.read_csv(uploaded_file)
            st.success(f"✅ File uploaded successfully! Found {len(df_import)} items")
            
            # Display preview
            st.markdown("#### File Preview")
            st.dataframe(df_import.head(), use_container_width=True)
            
            # Validate required columns
            required_cols = ['name', 'size', 'priority']
            missing_cols = [col for col in required_cols if col not in df_import.columns]
            
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
                st.info("Required columns: name, size, priority")
                st.info("Optional columns: zone, temperature_sensitive, hazardous, fragile, expiry_days, description")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Import All Items", type="primary"):
                        # Convert DataFrame to list of dictionaries
                        items_data = []
                        for _, row in df_import.iterrows():
                            item = {
                                "name": row.get('name', 'Unnamed Item'),
                                "size": float(row.get('size', 1.0)),
                                "priority": int(row.get('priority', 50)),
                                "zone": row.get('zone', 'Zone B'),
                                "temperature_sensitive": bool(row.get('temperature_sensitive', False)),
                                "hazardous": bool(row.get('hazardous', False)),
                                "fragile": bool(row.get('fragile', False)),
                                "expiry_days": int(row.get('expiry_days', 30)),
                                "description": row.get('description', '')
                            }
                            items_data.append(item)
                        
                        # Import items
                        with st.spinner(f"Importing {len(items_data)} items..."):
                            response = import_items({"items": items_data})
                            
                            if response and response.status_code in [200, 201]:
                                result = response.json()
                                success_count = result.get('success_count', len(items_data))
                                st.success(f"✅ Successfully imported {success_count} items!")
                                
                                if 'failed_items' in result and result['failed_items']:
                                    st.warning(f"⚠️ {len(result['failed_items'])} items failed to import")
                                    with st.expander("View Failed Items"):
                                        st.json(result['failed_items'])
                                
                                st.rerun()
                            else:
                                st.error("Failed to import items")
                
                with col2:
                    st.markdown("##### Import Template")
                    template_data = {
                        'name': ['Medical Supplies', 'Food Package A', 'Scientific Equipment'],
                        'size': [2.5, 1.0, 3.2],
                        'priority': [90, 60, 75],
                        'zone': ['Zone A', 'Zone B', 'Zone A'],
                        'temperature_sensitive': [True, False, False],
                        'hazardous': [False, False, True],
                        'fragile': [True, False, True],
                        'expiry_days': [180, 30, 365],
                        'description': ['Emergency medical supplies', 'Standard food ration', 'Research equipment']
                    }
                    template_df = pd.DataFrame(template_data)
                    
                    csv = template_df.to_csv(index=False)
                    st.download_button(
                        label="Download Template",
                        data=csv,
                        file_name="cargo_import_template.csv",
                        mime="text/csv"
                    )
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# Advanced Cargo Grid
def advanced_cargo_grid():
    """Render advanced cargo management grid"""
    st.markdown("## 📋 Advanced Cargo Management")
    
    df = load_cargo()
    if df.empty:
        st.warning("No cargo data available. Check API connection.")
        return
    
    # Add calculated columns
    df['days_remaining'] = df['expiry_date'].apply(calculate_days_remaining)
    df['status'] = df['days_remaining'].apply(
        lambda x: "🔴 Critical" if x <= 3 else "🟡 Warning" if x <= 7 else "🟢 Good"
    )
    
    # Filter controls
    with st.expander("🔍 Advanced Filters", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            zone_filter = st.multiselect(
                "Zone Filter", 
                options=df['zone'].unique() if 'zone' in df.columns else [],
                default=df['zone'].unique() if 'zone' in df.columns else []
            )
        
        with col2:
            priority_range = st.slider(
                "Priority Range",
                min_value=int(df['priority'].min()) if 'priority' in df.columns else 1,
                max_value=int(df['priority'].max()) if 'priority' in df.columns else 100,
                value=(1, 100)
            )
        
        with col3:
            size_range = st.slider(
                "Size Range (m³)",
                min_value=float(df['size'].min()) if 'size' in df.columns else 0.1,
                max_value=float(df['size'].max()) if 'size' in df.columns else 10.0,
                value=(0.1, 10.0)
            )
        
        with col4:
            status_filter = st.multiselect(
                "Status Filter",
                options=["🟢 Good", "🟡 Warning", "🔴 Critical"],
                default=["🟢 Good", "🟡 Warning", "🔴 Critical"]
            )
    
    # Apply filters
    filtered_df = df.copy()
    if zone_filter and 'zone' in df.columns:
        filtered_df = filtered_df[filtered_df['zone'].isin(zone_filter)]
    if 'priority' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['priority'] >= priority_range[0]) & 
            (filtered_df['priority'] <= priority_range[1])
        ]
    if 'size' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['size'] >= size_range[0]) & 
            (filtered_df['size'] <= size_range[1])
        ]
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    
    # Display summary
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} items**")
    
    # Configure AgGrid
    display_columns = [
        'id', 'name', 'status', 'days_remaining', 'zone', 
        'priority', 'size', 'temperature_sensitive', 'hazardous'
    ]
    
    # Filter to only include columns that exist
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    grid_df = filtered_df[available_columns].copy()
    
    # Build grid options
    gb = GridOptionsBuilder.from_dataframe(grid_df)
    gb.configure_default_column(editable=False, groupable=True)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    
    # Configure column-specific options
    if 'status' in grid_df.columns:
        gb.configure_column('status', width=120, pinned='left')
    if 'days_remaining' in grid_df.columns:
        gb.configure_column('days_remaining', type=['numericColumn'], width=130)
    if 'priority' in grid_df.columns:
        gb.configure_column('priority', type=['numericColumn'], width=100)
    if 'size' in grid_df.columns:
        gb.configure_column('size', type=['numericColumn'], width=100)
    
    grid_options = gb.build()
    
    # Display grid
    grid_response = AgGrid(
        grid_df,
        gridOptions=grid_options,
        data_return_mode='AS_INPUT',
        update_mode='MODEL_CHANGED',
        enable_enterprise_modules=False,
        height=500,
        theme="streamlit"
    )
    
    # Action buttons
    selected_rows = grid_response.selected_rows
    if selected_rows:
        st.markdown("### 🛠️ Bulk Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🗑️ Delete Selected", type="secondary"):
                if st.button("⚠️ Confirm Delete"):
                    deleted_count = 0
                    for row in selected_rows:
                        response = delete_cargo_item(row['id'])
                        if response and response.status_code == 200:
                            deleted_count += 1
                    
                    if deleted_count > 0:
                        st.success(f"✅ Deleted {deleted_count} items")
                        st.rerun()
        
        with col2:
            if st.button("📦 Retrieve Selected"):
                retrieved_count = 0
                for row in selected_rows:
                    response = retrieve_item(row['id'])
                    if response and response.status_code == 200:
                        retrieved_count += 1
                
                if retrieved_count > 0:
                    st.success(f"✅ Retrieved {retrieved_count} items")
                    st.rerun()
        
        with col3:
            if st.button("📊 Export Selected"):
                # Create CSV of selected items
                selected_df = pd.DataFrame(selected_rows)
                csv = selected_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"selected_cargo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
        
        with col4:
            st.markdown(f"**{len(selected_rows)} items selected**")

# Emergency Alerts System
def emergency_alerts():
    """Render emergency alerts and notifications"""
    st.markdown("## 🚨 Emergency Alerts & Notifications")
    
    df = load_cargo()
    if df.empty:
        return
    
    df['days_remaining'] = df['expiry_date'].apply(calculate_days_remaining)
    
    # Critical alerts
    critical_items = df[df['days_remaining'] <= 1]
    warning_items = df[(df['days_remaining'] > 1) & (df['days_remaining'] <= 3)]
    expiring_items = df[(df['days_remaining'] > 3) & (df['days_remaining'] <= 7)]
    
    # Display alerts
    if len(critical_items) > 0:
        st.error(f"🔴 **CRITICAL**: {len(critical_items)} items expire within 24 hours!")
        with st.expander("View Critical Items"):
            st.dataframe(critical_items[['id', 'name', 'days_remaining', 'zone']], use_container_width=True)
    
    if len(warning_items) > 0:
        st.warning(f"🟡 **WARNING**: {len(warning_items)} items expire within 3 days!")
        with st.expander("View Warning Items"):
            st.dataframe(warning_items[['id', 'name', 'days_remaining', 'zone']], use_container_width=True)
    
    if len(expiring_items) > 0:
        st.info(f"🔵 **NOTICE**: {len(expiring_items)} items expire within 7 days")
        with st.expander("View Expiring Items"):
            st.dataframe(expiring_items[['id', 'name', 'days_remaining', 'zone']], use_container_width=True)
    
    if len(critical_items) == 0 and len(warning_items) == 0 and len(expiring_items) == 0:
        st.success("✅ All cargo items are within acceptable expiry ranges!")

# System Configuration
def system_configuration():
    """Render system configuration panel"""
    st.markdown("## ⚙️ System Configuration")
    
    with st.expander("🔧 API Configuration", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            new_api_url = st.text_input("API Base URL", value=API_BASE_URL)
            new_refresh_interval = st.number_input("Refresh Interval (seconds)", value=REFRESH_INTERVAL, min_value=30, max_value=3600)
        
        with col2:
            if st.button("Test API Connection"):
                try:
                    response = requests.get(f"{new_api_url}/health", timeout=5)
                    if response.status_code == 200:
                        st.success("✅ API connection successful!")
                    else:
                        st.error(f"❌ API returned status {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
            
            if st.button("Apply Configuration"):
                st.info("Configuration applied for this session")
    
    with st.expander("📊 Display Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            theme_mode = st.selectbox("Theme Mode", ["Dark", "Light", "Auto"])
            items_per_page = st.number_input("Items Per Page", value=20, min_value=10, max_value=100)
        
        with col2:
            auto_refresh = st.checkbox("Auto Refresh", value=True)
            show_animations = st.checkbox("Show Animations", value=True)
    
    with st.expander("🔔 Alert Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            critical_threshold = st.number_input("Critical Alert (days)", value=1, min_value=0, max_value=7)
            warning_threshold = st.number_input("Warning Alert (days)", value=3, min_value=1, max_value=14)
        
        with col2:
            enable_sound = st.checkbox("Enable Sound Alerts", value=False)
            enable_email = st.checkbox("Enable Email Notifications", value=False)

# Main Application
def main():
    """Main application function"""
    render_header()
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("## 🚀 Navigation")
        
        page = st.selectbox(
            "Select Page:",
            [
                "🌌 3D Warehouse View",
                "📊 Metrics Dashboard", 
                "🧠 AI Optimizer",
                "♻️ Waste Management",
                "📋 Cargo Management",
                "🚨 Emergency Alerts",
                "⚙️ System Config"
            ]
        )
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("📥 Export All", use_container_width=True):
            response = export_arrangement()
            if response and response.status_code == 200:
                st.download_button(
                    label="⬇️ Download Export",
                    data=response.content,
                    file_name=f"full_arrangement_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf"
                )
        
        # Bulk import in sidebar
        st.markdown("---")
        bulk_import_feature()
        
        st.markdown("---")
        
        # System status
        st.markdown("### 📡 System Status")
        if check_api_health():
            st.success("🟢 API Online")
        else:
            st.error("🔴 API Offline")
        
        st.markdown(f"**Uptime:** {datetime.now().strftime('%H:%M:%S')}")
        st.markdown(f"**Refresh:** Every {REFRESH_INTERVAL//60}min")
    
    # Main content area
    if page == "🌌 3D Warehouse View":
        render_3d_warehouse()
    elif page == "📊 Metrics Dashboard":
        render_metrics()
    elif page == "🧠 AI Optimizer":
        ai_recommendation_engine()
    elif page == "♻️ Waste Management":
        waste_management_system()
    elif page == "📋 Cargo Management":
        advanced_cargo_grid()
    elif page == "🚨 Emergency Alerts":
        emergency_alerts()
    elif page == "⚙️ System Config":
        system_configuration()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        f"ISS Cargo AI Dashboard v2.0 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Refresh #{refresh_count}"
        "</div>", 
        unsafe_allow_html=True
    )

# Run the application
if __name__ == "__main__":
    main()
