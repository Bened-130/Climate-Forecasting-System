"""
Configuration settings for the Climate Forecasting System
"""

# Data generation settings
DATA_SETTINGS = {
    'historical_years': 10,
    'temperature_base': 25,
    'seasonal_variation': 5,
    'base_humidity': 60
}

# Model settings
MODEL_SETTINGS = {
    'temperature': {
        'changepoint_prior_scale': 0.05,
        'yearly_seasonality': True,
        'weekly_seasonality': False,
        'daily_seasonality': False
    },
    'rainfall': {
        'changepoint_prior_scale': 0.1,
        'yearly_seasonality': True,
        'weekly_seasonality': True,
        'daily_seasonality': False,
        'seasonality_mode': 'multiplicative'
    }
}

"""
Configuration settings for the Climate Forecasting System
"""

# Data generation settings
DATA_SETTINGS = {
    'historical_years': 10,
    'temperature_base': 25,
    'seasonal_variation': 5,
    'base_humidity': 60
}

# Model settings
MODEL_SETTINGS = {
    'temperature': {
        'changepoint_prior_scale': 0.05,
        'yearly_seasonality': True,
        'weekly_seasonality': False,
        'daily_seasonality': False
    },
    'rainfall': {
        'changepoint_prior_scale': 0.1,
        'yearly_seasonality': True,
        'weekly_seasonality': True,
        'daily_seasonality': False,
        'seasonality_mode': 'multiplicative'
    }
}

# Risk thresholds
RISK_THRESHOLDS = {
    'drought': {
        'high': 50,    # mm in 21 days
        'medium': 150  # mm in 21 days
    },
    'flood': {
        'low': 100,    # mm in 7 days
        'medium': 200  # mm in 7 days
    },
    'extreme_heat': {
        'medium': 30,  # °C
        'high': 35     # °C
    }
}

# Financial impact values (per day)
FINANCIAL_IMPACT = {
    'High': 50000,
    'Medium': 15000,
    'Low': 1000
}

# Alert settings
ALERT_THRESHOLDS = {
    'extreme_heat': 35,    # °C
    'heavy_rainfall': 50   # mm
}

# Forecast settings
FORECAST_DAYS = 30
TRAIN_TEST_SPLIT = 0.9