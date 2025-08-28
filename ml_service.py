import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import json
import logging
from datetime import datetime, timedelta
from models import AgriculturalData, User

class MLService:
    """Machine Learning service for agricultural data analysis and insights"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.crop_model = None
        self.price_model = None
        
    def clean_agricultural_data(self, raw_data):
        """Clean and preprocess raw agricultural data"""
        try:
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data)
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(raw_data if isinstance(raw_data, list) else [raw_data])
            
            # Handle missing values
            df = self._handle_missing_values(df)
            
            # Standardize column names
            df = self._standardize_columns(df)
            
            # Remove outliers
            df = self._remove_outliers(df)
            
            # Data validation
            df = self._validate_data(df)
            
            return df.to_dict('records')
            
        except Exception as e:
            logging.error(f"Data cleaning error: {str(e)}")
            return []
    
    def _handle_missing_values(self, df):
        """Handle missing values in agricultural data"""
        # Fill numeric columns with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())
        
        # Fill categorical columns with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if not df[col].empty:
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val[0])
        
        return df
    
    def _standardize_columns(self, df):
        """Standardize column names for consistency"""
        column_mapping = {
            'County': 'county',
            'COUNTY': 'county',
            'Crop': 'crop_name',
            'CROP': 'crop_name',
            'Production': 'production_tonnes',
            'PRODUCTION': 'production_tonnes',
            'Area': 'area_hectares',
            'AREA': 'area_hectares',
            'Year': 'year',
            'YEAR': 'year',
            'Price': 'price_kes',
            'PRICE': 'price_kes',
            'Season': 'season',
            'SEASON': 'season'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df
    
    def _remove_outliers(self, df):
        """Remove outliers using IQR method"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col in df.columns and not df[col].empty:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Remove outliers
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        
        return df
    
    def _validate_data(self, df):
        """Validate data for consistency and accuracy"""
        # Remove rows with invalid years
        current_year = datetime.now().year
        if 'year' in df.columns:
            df = df[(df['year'] >= 1960) & (df['year'] <= current_year)]
        
        # Remove rows with negative production or area values
        if 'production_tonnes' in df.columns:
            df = df[df['production_tonnes'] >= 0]
        
        if 'area_hectares' in df.columns:
            df = df[df['area_hectares'] >= 0]
        
        return df
    
    def generate_farmer_insights(self, user):
        """Generate personalized insights for a farmer"""
        try:
            insights = {
                'crop_recommendations': [],
                'market_trends': {},
                'weather_insights': {},
                'productivity_tips': []
            }
            
            user_county = user.county
            user_crops = json.loads(user.primary_crops) if user.primary_crops else []
            
            # Get county-specific data
            county_data = AgriculturalData.query.filter_by(county=user_county).all()
            
            if county_data:
                # Analyze crop performance in the county
                insights['crop_recommendations'] = self._analyze_crop_performance(
                    county_data, user_crops, user_county
                )
                
                # Generate market trends
                insights['market_trends'] = self._analyze_market_trends(county_data)
            
            # Generate productivity tips based on user profile
            insights['productivity_tips'] = self._generate_productivity_tips(user)
            
            return insights
            
        except Exception as e:
            logging.error(f"Insights generation error: {str(e)}")
            return {
                'crop_recommendations': [],
                'market_trends': {},
                'weather_insights': {},
                'productivity_tips': []
            }
    
    def _analyze_crop_performance(self, county_data, user_crops, county):
        """Analyze crop performance and generate recommendations"""
        recommendations = []
        
        try:
            # Create DataFrame from county data
            data_list = []
            for record in county_data:
                if record.crop_name and record.value:
                    data_list.append({
                        'crop_name': record.crop_name,
                        'value': record.value,
                        'year': record.year,
                        'data_type': record.data_type
                    })
            
            if not data_list:
                return [
                    {
                        'crop': 'Maize',
                        'reason': 'Staple crop suitable for most Kenyan counties',
                        'potential_yield': 'Medium to High'
                    }
                ]
            
            df = pd.DataFrame(data_list)
            
            # Group by crop and calculate average performance
            crop_performance = df.groupby('crop_name')['value'].agg(['mean', 'std']).reset_index()
            crop_performance = crop_performance.sort_values('mean', ascending=False)
            
            # Generate top 3 recommendations
            top_crops = crop_performance.head(3)
            
            for _, crop in top_crops.iterrows():
                recommendations.append({
                    'crop': crop['crop_name'],
                    'reason': f'High average performance in {county} county',
                    'potential_yield': 'High' if crop['mean'] > crop_performance['mean'].median() else 'Medium',
                    'avg_value': round(crop['mean'], 2)
                })
            
            return recommendations
            
        except Exception as e:
            logging.error(f"Crop analysis error: {str(e)}")
            return [
                {
                    'crop': 'Maize',
                    'reason': 'Staple crop suitable for most Kenyan counties',
                    'potential_yield': 'Medium'
                }
            ]
    
    def _analyze_market_trends(self, county_data):
        """Analyze market trends from agricultural data"""
        trends = {
            'price_trends': {},
            'production_trends': {},
            'seasonal_patterns': {}
        }
        
        try:
            # Filter price data
            price_data = [d for d in county_data if d.data_type == 'market_prices']
            
            if price_data:
                # Analyze price trends by crop
                price_df = pd.DataFrame([
                    {
                        'crop': record.crop_name,
                        'price': record.value,
                        'year': record.year
                    }
                    for record in price_data if record.crop_name and record.value
                ])
                
                if not price_df.empty:
                    latest_prices = price_df.groupby('crop')['price'].last().to_dict()
                    trends['price_trends'] = {
                        crop: {
                            'current_price': price,
                            'trend': 'stable'  # Simplified trend analysis
                        }
                        for crop, price in latest_prices.items()
                    }
            
            return trends
            
        except Exception as e:
            logging.error(f"Market trends analysis error: {str(e)}")
            return trends
    
    def _generate_productivity_tips(self, user):
        """Generate personalized productivity tips"""
        tips = []
        
        # Tips based on farm size
        if user.farm_size and user.farm_size < 5:
            tips.extend([
                "Consider intensive farming methods to maximize small farm productivity",
                "Explore high-value crops like vegetables and herbs for better returns",
                "Implement crop rotation to maintain soil fertility"
            ])
        elif user.farm_size and user.farm_size >= 5:
            tips.extend([
                "Consider mechanization to improve efficiency on larger farms",
                "Diversify crops to reduce risk and increase income streams",
                "Explore contract farming opportunities with agribusiness companies"
            ])
        
        # Tips based on experience
        if user.farming_experience and user.farming_experience < 5:
            tips.extend([
                "Join local farmer groups to learn from experienced farmers",
                "Attend agricultural extension services and training programs",
                "Start with proven crops before experimenting with new varieties"
            ])
        
        # County-specific tips (simplified examples)
        county_tips = {
            'Nakuru': 'Consider dairy farming alongside crop production in this favorable climate',
            'Kiambu': 'Coffee and tea are well-suited for this highland region',
            'Meru': 'Miraa and coffee are traditional crops with good market potential',
            'Machakos': 'Drought-resistant crops like sorghum and millet work well here'
        }
        
        if user.county in county_tips:
            tips.append(county_tips[user.county])
        
        return tips[:5]  # Return top 5 tips
    
    def generate_agricultural_report(self, user):
        """Generate comprehensive agricultural report for a farmer"""
        try:
            insights = self.generate_farmer_insights(user)
            user_crops = json.loads(user.primary_crops) if user.primary_crops else []
            
            report_content = f"""
            Agricultural Analysis Report for {user.full_name}
            
            Farm Profile:
            - Location: {user.county} County
            - Farm Size: {user.farm_size} acres
            - Primary Crops: {', '.join(user_crops)}
            - Farming Experience: {user.farming_experience} years
            
            Crop Recommendations:
            """
            
            for i, rec in enumerate(insights['crop_recommendations'], 1):
                report_content += f"\n{i}. {rec['crop']} - {rec['reason']}"
            
            report_content += "\n\nProductivity Tips:\n"
            for i, tip in enumerate(insights['productivity_tips'], 1):
                report_content += f"{i}. {tip}\n"
            
            return {
                'title': f'Agricultural Analysis Report - {user.county} County',
                'type': 'comprehensive_analysis',
                'content': report_content,
                'insights': insights
            }
            
        except Exception as e:
            logging.error(f"Report generation error: {str(e)}")
            return None
    
    def predict_crop_yield(self, crop_data):
        """Predict crop yield using machine learning model"""
        try:
            if not crop_data:
                return None
            
            # Prepare data for prediction
            df = pd.DataFrame(crop_data)
            
            # Feature engineering
            features = ['area_hectares', 'year']
            if all(col in df.columns for col in features):
                X = df[features]
                y = df['production_tonnes'] if 'production_tonnes' in df.columns else None
                
                if y is not None and len(X) > 10:
                    # Train simple linear regression model
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.2, random_state=42
                    )
                    
                    model = LinearRegression()
                    model.fit(X_train, y_train)
                    
                    predictions = model.predict(X_test)
                    r2 = r2_score(y_test, predictions)
                    
                    return {
                        'model_accuracy': r2,
                        'predictions': predictions.tolist(),
                        'feature_importance': dict(zip(features, model.coef_))
                    }
            
            return None
            
        except Exception as e:
            logging.error(f"Crop yield prediction error: {str(e)}")
            return None
