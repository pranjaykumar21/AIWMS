# 🚀 ISS Cargo AI Dashboard

> An intelligent space station inventory management system with AI-powered placement optimization, 3D visualization, and comprehensive cargo tracking.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/yourusername/iss-cargo-ai)

## 🌟 Features

### 🌌 3D Warehouse Visualization
- **Interactive 3D Environment**: Immersive warehouse visualization with real-time cargo positioning
- **Zone-based Color Coding**: Visual distinction between storage zones (A, B, C)
- **Dynamic Filtering**: Filter by zone, priority, and expiry status
- **Real-time Updates**: Live cargo positioning and status updates

### 🧠 AI-Powered Optimization
- **Intelligent Placement**: AI recommends optimal storage locations based on:
  - Item priority and urgency
  - Temperature sensitivity requirements
  - Hazardous material safety protocols
  - Space utilization efficiency
- **Confidence Scoring**: AI provides confidence levels and reasoning for recommendations
- **Learning Algorithm**: Continuously improves recommendations based on usage patterns

### 📊 Advanced Analytics
- **Real-time Metrics Dashboard**: 
  - Total cargo tracking
  - Expiry monitoring
  - Capacity utilization
  - Priority distribution
- **Interactive Visualizations**:
  - Zone distribution pie charts
  - Priority histograms
  - Expiry timeline scatter plots
- **Predictive Analytics**: Forecast storage needs and expiry risks

### ♻️ Waste Management System
- **Expiry Tracking**: Automated monitoring of item expiration dates
- **Return Planning**: AI-generated waste return plans for expired items
- **Time Simulation**: Fast-forward time to test scenarios
- **Bulk Operations**: Mass retrieval and deletion capabilities

### 📋 Advanced Cargo Management
- **Interactive Data Grid**: 
  - Sortable and filterable cargo list
  - Multi-select operations
  - Real-time status updates
- **Bulk Import/Export**: 
  - CSV import functionality
  - Export arrangements to PDF
  - Template downloads
- **Search & Filter**: Advanced filtering by multiple criteria

### 🚨 Emergency Alert System
- **Critical Notifications**: Immediate alerts for items expiring within 24 hours
- **Tiered Warning System**: 
  - 🔴 Critical (≤1 day)
  - 🟡 Warning (≤3 days)
  - 🔵 Notice (≤7 days)
- **Real-time Monitoring**: Continuous background monitoring

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Internet connection for API communication

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/pranjaykumar21/AIWMS/iss-cargo-ai.git
   cd iss-cargo-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the dashboard**
   - Open your browser to `https://huggingface.co/spaces/Predator911/AIWMS`
   - The dashboard will automatically load and connect to the API

## 📦 Dependencies

```python
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.0
plotly>=5.15.0
numpy>=1.24.0
streamlit-autorefresh>=0.0.1
streamlit-aggrid>=0.3.4
```

## 🔧 Configuration

### API Configuration
The application connects to a backend API for data management. Configure the API settings in `app.py`:

```python
API_BASE_URL = "https://aiwms.onrender.com/api"
REFRESH_INTERVAL = 300  # 5 minutes
```

### Environment Variables
Create a `.env` file for sensitive configurations:

```env
API_BASE_URL=https://your-api-endpoint.com/api
REFRESH_INTERVAL=300
DEBUG_MODE=False
```

## 🎮 Usage Guide

### Adding New Cargo
1. Navigate to **🧠 AI Optimizer** page
2. Fill in cargo details (name, size, priority, etc.)
3. Click **"Get AI Recommendation"** for optimal placement
4. Review AI suggestions and confirm placement

### Monitoring Expiry
1. Go to **♻️ Waste Management** page
2. Set expiry threshold (default: 7 days)
3. View expiring items in the interactive grid
4. Generate return plans for expired cargo

### 3D Visualization
1. Access **🌌 3D Warehouse View**
2. Use filter controls to focus on specific items
3. Hover over cargo for detailed information
4. Rotate and zoom for different perspectives

### Bulk Operations
1. Visit **📋 Cargo Management** page
2. Select multiple items using checkboxes
3. Perform bulk actions (delete, retrieve, export)
4. Use advanced filters for precise selection

## 🏗️ Architecture

### Frontend (Streamlit)
- **Dashboard Interface**: Multi-page Streamlit application
- **Real-time Updates**: Auto-refresh every 5 minutes
- **Interactive Components**: AgGrid, Plotly charts, 3D visualizations
- **Responsive Design**: Mobile-friendly layout

### Backend API Integration
- **RESTful API**: Communicates with backend services
- **Error Handling**: Robust error handling and retry mechanisms
- **Caching**: Streamlit caching for improved performance
- **Health Monitoring**: API health checks and status indicators

### Data Flow
```
Frontend (Streamlit) ←→ Backend API ←→ Database
                    ←→ AI Engine ←→ Optimization Algorithms
```

## 🧪 API Endpoints

The application integrates with the following API endpoints:

### Core Operations
- `GET /api/health` - API health check
- `GET /api/get_cargo` - Retrieve all cargo items
- `POST /api/add_cargo` - Add new cargo item
- `DELETE /api/delete_cargo/{id}` - Remove cargo item

### AI Features
- `POST /api/placement` - Get AI placement recommendation
- `POST /api/waste/return-plan` - Generate return plan

### Utilities
- `POST /api/retrieve/{id}` - Retrieve specific item
- `POST /api/simulate/day` - Simulate time progression
- `GET /api/export/arrangement` - Export arrangement plan
- `POST /api/import/items` - Bulk import items

## 🎨 Customization

### Themes and Styling
Modify the CSS in `app.py` to customize the appearance:

```python
st.markdown("""
<style>
    .main-header {color:#38b6ff; font-size:46px;}
    .zone-a {color:#38b6ff;}
    .zone-b {color:#9ef8a6;}
    .zone-c {color:#ff6961;}
</style>
""", unsafe_allow_html=True)
```

### Adding New Features
1. Create new functions in `app.py`
2. Add navigation option in the sidebar
3. Implement the corresponding page render function
4. Update the main application router

## 🔍 Troubleshooting

### Common Issues

**API Connection Failed**
- Check `API_BASE_URL` configuration
- Verify internet connection
- Ensure backend API is running

**Data Not Loading**
- Clear Streamlit cache: `st.cache_data.clear()`
- Refresh the page
- Check API health status in sidebar

**3D Visualization Not Working**
- Ensure modern browser with WebGL support
- Check for JavaScript errors in browser console
- Verify Plotly installation

### Performance Optimization
- Adjust `REFRESH_INTERVAL` for your needs
- Use filtering to reduce data load
- Enable caching for better performance

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include error handling
- Write unit tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit Team** - For the amazing web framework
- **Plotly** - For powerful visualization capabilities
- **NASA** - For inspiration from real space station operations
- **Open Source Community** - For the excellent libraries and tools

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/iss-cargo-ai/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/iss-cargo-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/iss-cargo-ai/discussions)
- **Email**: support@example.com

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Production Deployment
```bash
streamlit run app.py --server.port 8501 --server.headless true
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

<div align="center">

**Made with ❤️ for space exploration and efficient inventory management**

[🌟 Star this repo](https://github.com/yourusername/iss-cargo-ai) • [🐛 Report Bug](https://github.com/yourusername/iss-cargo-ai/issues) • [💡 Request Feature](https://github.com/yourusername/iss-cargo-ai/issues)

</div>
