import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)


class WeatherDataCollector:
    """Collect and process weather data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize weather data collector"""
        self.config = config or {}
        logger.info("WeatherDataCollector initialized")
    
    def generate_historical_data(self, years: int = 10) -> pd.DataFrame:
        """Generate historical weather data for demonstration"""
        logger.info(f"Generating {years} years of historical weather data")
        
        np.random.seed(42)
        
        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*years)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        data = []
        for date in dates:
            # Temperature (Celsius) - with seasonal variation
            base_temp = self.config.get('temperature_base', 25)
            seasonal_temp = self.config.get('seasonal_variation', 5) * np.sin(2 * np.pi * date.dayofyear / 365)
            daily_variation = np.random.normal(0, 2)
            temperature = base_temp + seasonal_temp + daily_variation
            
            # Rainfall (mm) - with rainy/dry seasons
            month = date.month
            if month in [3, 4, 5, 10, 11]:  # Rainy seasons
                rainfall = max(0, np.random.exponential(15))
            else:  # Dry seasons
                rainfall = max(0, np.random.exponential(2))
            
            # Humidity (%) - correlated with rainfall
            base_humidity = self.config.get('base_humidity', 60)
            humidity = base_humidity + (rainfall / 5) + np.random.normal(0, 5)
            humidity = np.clip(humidity, 30, 95)
            
            # Wind speed (km/h)
            wind_speed = max(0, np.random.gamma(2, 5))
            
            data.append({
                'date': date,
                'temperature': round(temperature, 2),
                'rainfall': round(rainfall, 2),
                'humidity': round(humidity, 2),
                'wind_speed': round(wind_speed, 2)
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Generated {len(df)} weather records")
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate weather data"""
        logger.info("Cleaning weather data")
        
        initial_count = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['date'])
        
        # Handle missing values
        for col in ['temperature', 'rainfall', 'humidity', 'wind_speed']:
            df[col].fillna(df[col].rolling(7, min_periods=1).mean(), inplace=True)
        
        # Remove extreme outliers
        for col in ['temperature', 'humidity']:
            Q1 = df[col].quantile(0.01)
            Q3 = df[col].quantile(0.99)
            df = df[(df[col] >= Q1) & (df[col] <= Q3)]
        
        # Ensure logical constraints
        df['temperature'] = df['temperature'].clip(-10, 50)
        df['humidity'] = df['humidity'].clip(0, 100)
        df['rainfall'] = df['rainfall'].clip(0, 500)
        df['wind_speed'] = df['wind_speed'].clip(0, 150)
        
        logger.info(f"Cleaned data: {len(df)} records (removed {initial_count - len(df)})")
        return df
    
    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features"""
        df = df.copy()
        
        # Time features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['dayofyear'] = df['date'].dt.dayofyear
        df['quarter'] = df['date'].dt.quarter
        df['season'] = df['month'].apply(self._get_season)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'temp_rolling_{window}d'] = df['temperature'].rolling(window).mean()
            df[f'rain_rolling_{window}d'] = df['rainfall'].rolling(window).sum()
        
        # Weather indices
        df['heat_index'] = df['temperature'] + (0.5 * df['humidity'])
        df['drought_risk'] = (df['rainfall'] < 5).rolling(21).sum()
        
        return df
    
    def _get_season(self, month: int) -> str:
        """Determine season from month"""
        if month in [3, 4, 5]:
            return 'Long Rains'
        elif month in [10, 11]:
            return 'Short Rains'
        else:
            return 'Dry Season'