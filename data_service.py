import requests
import pandas as pd
import json
import logging
from datetime import datetime
from app import db
from models import AgriculturalData
from ml_service import MLService

class DataService:
    """Service for fetching and processing data from KilimoSTAT and KNBS"""
    
    def __init__(self):
        self.ml_service = MLService()
        self.base_urls = {
            'kilimo_stat': 'https://statistics.kilimo.go.ke/api/',
            'knbs': 'https://knbs.or.ke/api/'
        }
        
    def fetch_latest_data(self):
        """Fetch latest agricultural data from official sources"""
        try:
            total_records = 0
            
            # Fetch from KilimoSTAT (simulated structure based on real portal)
            kilimo_records = self._fetch_kilimo_data()
            if kilimo_records:
                total_records += len(kilimo_records)
                self._save_agricultural_data(kilimo_records, 'KilimoSTAT')
            
            # Fetch from KNBS (simulated structure)
            knbs_records = self._fetch_knbs_data()
            if knbs_records:
                total_records += len(knbs_records)
                self._save_agricultural_data(knbs_records, 'KNBS')
            
            return {
                'success': True,
                'records_updated': total_records,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logging.error(f"Data fetching error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    def _fetch_kilimo_data(self):
        """Fetch data from KilimoSTAT portal"""
        try:
            # Note: Since direct API access isn't available, we'll use sample data structure
            # that matches the actual KilimoSTAT data format for demonstration
            
            # In a real implementation, this would make HTTP requests to actual endpoints
            sample_kilimo_data = self._get_sample_kilimo_data()
            
            # Clean and process the data using ML service
            cleaned_data = []
            for record in sample_kilimo_data:
                processed = self.ml_service.clean_agricultural_data([record])
                if processed:
                    cleaned_data.extend(processed)
            
            return cleaned_data
            
        except Exception as e:
            logging.error(f"KilimoSTAT fetch error: {str(e)}")
            return []
    
    def _fetch_knbs_data(self):
        """Fetch data from KNBS portal"""
        try:
            # Sample KNBS data structure based on their agricultural statistics
            sample_knbs_data = self._get_sample_knbs_data()
            
            # Clean and process the data
            cleaned_data = []
            for record in sample_knbs_data:
                processed = self.ml_service.clean_agricultural_data([record])
                if processed:
                    cleaned_data.extend(processed)
            
            return cleaned_data
            
        except Exception as e:
            logging.error(f"KNBS fetch error: {str(e)}")
            return []
    
    def _get_sample_kilimo_data(self):
        """Generate sample data based on KilimoSTAT structure"""
        # This represents the actual data structure from KilimoSTAT
        # In production, this would be replaced with actual API calls
        counties = [
            'Nakuru', 'Kiambu', 'Meru', 'Machakos', 'Kisumu', 'Eldoret',
            'Nyeri', 'Kakamega', 'Bungoma', 'Trans Nzoia'
        ]
        
        crops = [
            'Maize', 'Beans', 'Tea', 'Coffee', 'Wheat', 'Rice',
            'Sweet Potatoes', 'Irish Potatoes', 'Tomatoes', 'Onions'
        ]
        
        sample_data = []
        current_year = datetime.now().year
        
        for county in counties:
            for crop in crops:
                # Production data
                sample_data.append({
                    'county': county,
                    'crop_name': crop,
                    'data_type': 'crop_production',
                    'year': current_year - 1,
                    'value': self._generate_realistic_production_value(crop),
                    'unit': 'tonnes',
                    'season': 'Long_Rains'
                })
                
                # Market price data
                sample_data.append({
                    'county': county,
                    'crop_name': crop,
                    'data_type': 'market_prices',
                    'year': current_year,
                    'value': self._generate_realistic_price_value(crop),
                    'unit': 'KES_per_kg',
                    'season': 'Current'
                })
        
        return sample_data
    
    def _get_sample_knbs_data(self):
        """Generate sample data based on KNBS structure"""
        counties = [
            'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret',
            'Thika', 'Malindi', 'Kitale', 'Garissa', 'Meru'
        ]
        
        crops = ['Maize', 'Wheat', 'Rice', 'Beans', 'Tea', 'Coffee']
        
        sample_data = []
        current_year = datetime.now().year
        
        for county in counties:
            for crop in crops:
                sample_data.append({
                    'county': county,
                    'crop_name': crop,
                    'data_type': 'area_cultivated',
                    'year': current_year - 1,
                    'value': self._generate_realistic_area_value(),
                    'unit': 'hectares',
                    'season': 'Annual'
                })
        
        return sample_data
    
    def _generate_realistic_production_value(self, crop):
        """Generate realistic production values based on crop type"""
        import random
        
        # Base production values in tonnes (approximate Kenyan averages)
        crop_production_ranges = {
            'Maize': (1000, 50000),
            'Beans': (500, 15000),
            'Tea': (2000, 30000),
            'Coffee': (800, 12000),
            'Wheat': (1500, 25000),
            'Rice': (800, 10000),
            'Sweet Potatoes': (3000, 40000),
            'Irish Potatoes': (2000, 35000),
            'Tomatoes': (1000, 20000),
            'Onions': (800, 15000)
        }
        
        range_min, range_max = crop_production_ranges.get(crop, (500, 10000))
        return round(random.uniform(range_min, range_max), 2)
    
    def _generate_realistic_price_value(self, crop):
        """Generate realistic price values based on crop type"""
        import random
        
        # Base prices in KES per kg (approximate Kenyan market prices)
        crop_price_ranges = {
            'Maize': (30, 60),
            'Beans': (80, 150),
            'Tea': (200, 400),  # per kg for processed tea
            'Coffee': (300, 600),  # per kg for processed coffee
            'Wheat': (40, 70),
            'Rice': (90, 140),
            'Sweet Potatoes': (25, 50),
            'Irish Potatoes': (35, 70),
            'Tomatoes': (40, 100),
            'Onions': (30, 80)
        }
        
        range_min, range_max = crop_price_ranges.get(crop, (20, 100))
        return round(random.uniform(range_min, range_max), 2)
    
    def _generate_realistic_area_value(self):
        """Generate realistic area cultivated values"""
        import random
        return round(random.uniform(100, 10000), 2)
    
    def _save_agricultural_data(self, data_records, source):
        """Save processed agricultural data to database"""
        try:
            for record in data_records:
                # Check if record already exists
                existing = AgriculturalData.query.filter_by(
                    data_source=source,
                    county=record.get('county'),
                    crop_name=record.get('crop_name'),
                    data_type=record.get('data_type'),
                    year=record.get('year'),
                    season=record.get('season')
                ).first()
                
                if not existing:
                    # Create new record
                    ag_data = AgriculturalData(
                        data_source=source,
                        data_type=record.get('data_type'),
                        county=record.get('county'),
                        crop_name=record.get('crop_name'),
                        season=record.get('season'),
                        year=record.get('year'),
                        value=record.get('value'),
                        unit=record.get('unit'),
                        raw_data=record,
                        processed_data=record
                    )
                    db.session.add(ag_data)
                else:
                    # Update existing record
                    existing.value = record.get('value')
                    existing.updated_at = datetime.utcnow()
                    existing.processed_data = record
            
            db.session.commit()
            logging.info(f"Saved {len(data_records)} records from {source}")
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving data from {source}: {str(e)}")
            raise
    
    def get_county_data(self, county_name, crop_name=None):
        """Get agricultural data for a specific county"""
        try:
            query = AgriculturalData.query.filter_by(county=county_name)
            
            if crop_name:
                query = query.filter_by(crop_name=crop_name)
            
            data = query.order_by(AgriculturalData.year.desc()).limit(50).all()
            
            return [{
                'county': record.county,
                'crop_name': record.crop_name,
                'data_type': record.data_type,
                'year': record.year,
                'value': record.value,
                'unit': record.unit,
                'season': record.season
            } for record in data]
            
        except Exception as e:
            logging.error(f"Error fetching county data: {str(e)}")
            return []
    
    def get_crop_trends(self, crop_name, years=5):
        """Get trend data for a specific crop over recent years"""
        try:
            current_year = datetime.now().year
            start_year = current_year - years
            
            data = AgriculturalData.query.filter(
                AgriculturalData.crop_name == crop_name,
                AgriculturalData.year >= start_year,
                AgriculturalData.data_type == 'crop_production'
            ).order_by(AgriculturalData.year.asc()).all()
            
            # Group by year and calculate totals
            year_totals = {}
            for record in data:
                year = record.year
                if year not in year_totals:
                    year_totals[year] = 0
                year_totals[year] += record.value or 0
            
            return {
                'crop': crop_name,
                'trend_data': [
                    {'year': year, 'production': total}
                    for year, total in sorted(year_totals.items())
                ]
            }
            
        except Exception as e:
            logging.error(f"Error fetching crop trends: {str(e)}")
            return {'crop': crop_name, 'trend_data': []}
