# Kenya-Agor Agricultural System

## Overview

Kenya-Agor is a comprehensive agricultural data visualization and management system designed specifically for Kenyan farmers. The platform integrates machine learning, AI chatbot assistance, and real-time agricultural data to provide actionable insights for farming decisions. It serves as a centralized hub for agricultural data from official Kenyan sources like KilimoSTAT and KNBS, offering personalized dashboards, automated reporting, and intelligent crop recommendations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask-based web application with modular service architecture
- **Database**: SQLAlchemy ORM with PostgreSQL for production data storage
- **Authentication**: Flask-Login for user session management with farmer-specific profiles
- **Service Layer**: Separated concerns with dedicated services for ML, data processing, and chatbot functionality

### Data Processing Pipeline
- **Data Sources**: Integration with KilimoSTAT and KNBS APIs for official agricultural statistics
- **ML Service**: Scikit-learn based machine learning for crop recommendations, price predictions, and data analysis
- **Data Cleaning**: Automated preprocessing pipeline for handling missing values, outliers, and standardization
- **Storage Model**: Structured agricultural data model supporting crops, seasons, counties, and market information

### AI Integration
- **Chatbot Service**: OpenAI GPT-4o integration for agricultural advisory services
- **Context Awareness**: User-specific context including location, farm size, crops, and experience level
- **Advisory System**: Specialized prompts for Kenyan agricultural conditions and practices

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive design
- **UI Components**: Agricultural-themed interface with green color palette and farming iconography
- **Interactive Elements**: Chart.js for data visualization, real-time chatbot interface
- **User Experience**: Role-based dashboards tailored for Kenyan farmers

### Security & Configuration
- **Environment Variables**: Secure handling of API keys, database URLs, and session secrets
- **Proxy Configuration**: ProxyFix middleware for HTTPS URL generation
- **Password Security**: Werkzeug password hashing with 256-character hash storage

## External Dependencies

### APIs & Data Sources
- **OpenAI API**: GPT-4o model for agricultural chatbot assistance
- **KilimoSTAT API**: Official Kenyan agricultural statistics portal
- **KNBS API**: Kenya National Bureau of Statistics for agricultural data

### Third-Party Libraries
- **Flask Ecosystem**: Flask, Flask-SQLAlchemy, Flask-Login for web framework
- **Machine Learning**: Scikit-learn for ML models, Pandas/NumPy for data processing
- **Frontend**: Bootstrap 5, Font Awesome icons, Chart.js for visualization
- **Database**: PostgreSQL with SQLAlchemy ORM abstraction

### Development Tools
- **Logging**: Python logging for debugging and error tracking
- **Data Processing**: JSON handling for API responses and agricultural data storage
- **HTTP Requests**: Requests library for external API integration