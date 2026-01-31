import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ClimateForecaster:
    """Advanced climate forecasting system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize climate forecaster"""
        self.config = config or {}
        self.temp_model = None
        self.rain_model = None
        logger.info("ClimateForecaster initialized")
    
    def train_temperature_model(self, df: pd.DataFrame):
        """Train temperature forecasting model"""
        logger.info("Training temperature forecasting model")
        
        # Prepare data for Prophet
        temp_data = df[['date', 'temperature']].copy()
        temp_data.columns = ['ds', 'y']
        
        # Get model config
        model_config = self.config.get('temperature', {})
        
        # Initialize and train model
        self.temp_model = Prophet(
            yearly_seasonality=model_config.get('yearly_seasonality', True),
            weekly_seasonality=model_config.get('weekly_seasonality', False),
            daily_seasonality=model_config.get('daily_seasonality', False),
            changepoint_prior_scale=model_config.get('changepoint_prior_scale', 0.05)
        )
        
        self.temp_model.add_seasonality(
            name='monthly',
            period=30.5,
            fourier_order=5
        )
        
        self.temp_model.fit(temp_data)
        logger.info("Temperature model trained successfully")
    
    def train_rainfall_model(self, df: pd.DataFrame):
        """Train rainfall forecasting model"""
        logger.info("Training rainfall forecasting model")
        
        # Prepare data
        rain_data = df[['date', 'rainfall']].copy()
        rain_data.columns = ['ds', 'y']
        
        # Get model config
        model_config = self.config.get('rainfall', {})
        
        # Initialize model
        self.rain_model = Prophet(
            yearly_seasonality=model_config.get('yearly_seasonality', True),
            weekly_seasonality=model_config.get('weekly_seasonality', True),
            daily_seasonality=model_config.get('daily_seasonality', False),
            seasonality_mode=model_config.get('seasonality_mode', 'multiplicative'),
            changepoint_prior_scale=model_config.get('changepoint_prior_scale', 0.1)
        )
        
        # Add custom seasonalities for rainy seasons
        self.rain_model.add_seasonality(
            name='long_rains',
            period=365.25,
            fourier_order=3,
            condition_name='long_rains_season'
        )
        
        rain_data['long_rains_season'] = rain_data['ds'].dt.month.isin([3, 4, 5])
        
        self.rain_model.fit(rain_data)
        logger.info("Rainfall model trained successfully")
    
    def predict_temperature(self, periods: int = 30) -> pd.DataFrame:
        """Generate temperature forecast"""
        logger.info(f"Generating {periods}-day temperature forecast")
        
        if self.temp_model is None:
            raise ValueError("Temperature model not trained. Call train_temperature_model first.")
        
        future = self.temp_model.make_future_dataframe(periods=periods)
        forecast = self.temp_model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
    
    def predict_rainfall(self, periods: int = 30) -> pd.DataFrame:
        """Generate rainfall forecast"""
        logger.info(f"Generating {periods}-day rainfall forecast")
        
        if self.rain_model is None:
            raise ValueError("Rainfall model not trained. Call train_rainfall_model first.")
        
        future = self.rain_model.make_future_dataframe(periods=periods)
        future['long_rains_season'] = future['ds'].dt.month.isin([3, 4, 5])
        
        forecast = self.rain_model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
    
    def evaluate_model(self, actual_df: pd.DataFrame, 
                      forecast_df: pd.DataFrame,
                      metric: str = 'temperature') -> Dict[str, float]:
        """Evaluate forecast accuracy"""
        logger.info(f"Evaluating {metric} forecast")
        
        # Merge actual and forecast
        merged = actual_df.merge(
            forecast_df,
            left_on='date',
            right_on='ds',
            how='inner'
        )
        
        # Calculate metrics
        actual = merged['temperature'] if metric == 'temperature' else merged['rainfall']
        predicted = merged['yhat']
        
        mae = mean_absolute_error(actual, predicted)
        rmse = np.sqrt(mean_squared_error(actual, predicted))
        mape = mean_absolute_percentage_error(actual, predicted)
        
        accuracy = (1 - mape) * 100
        
        metrics = {
            'mae': round(mae, 2),
            'rmse': round(rmse, 2),
            'mape': round(mape * 100, 2),
            'accuracy': round(accuracy, 2)
        }
        
        logger.info(f"{metric.capitalize()} Forecast Accuracy: {metrics['accuracy']}%")
        return metrics