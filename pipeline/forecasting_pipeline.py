from typing import Dict, Any
from data_collection.weather_collector import WeatherDataCollector
from forecasting.climate_forecaster import ClimateForecaster
from risk_assessment.risk_assessor import RiskAssessor
from alerts.alert_system import AlertSystem
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ClimateForecastingPipeline:
    """Complete climate forecasting pipeline"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize forecasting pipeline"""
        self.config = config or {}
        self.collector = WeatherDataCollector(self.config.get('data_settings', {}))
        self.forecaster = ClimateForecaster(self.config.get('model_settings', {}))
        self.risk_assessor = RiskAssessor({
            'drought': self.config.get('risk_thresholds', {}).get('drought', {}),
            'flood': self.config.get('risk_thresholds', {}).get('flood', {}),
            'extreme_heat': self.config.get('risk_thresholds', {}).get('extreme_heat', {}),
            'financial_impact': self.config.get('financial_impact', {})
        })
        self.alert_system = AlertSystem({
            'alert_thresholds': self.config.get('alert_thresholds', {})
        })
        logger.info("ClimateForecastingPipeline initialized")
    
    def run_complete_forecast(self, forecast_days: int = None) -> Dict[str, Any]:
        """Run complete forecasting pipeline"""
        forecast_days = forecast_days or self.config.get('forecast_days', 30)
        
        logger.info("=" * 60)
        logger.info("STARTING CLIMATE FORECASTING PIPELINE")
        logger.info("=" * 60)
        
        # Step 1: Data Collection
        logger.info("\n--- STEP 1: Data Collection ---")
        historical_data = self.collector.generate_historical_data(
            years=self.config.get('data_settings', {}).get('historical_years', 10)
        )
        clean_data = self.collector.clean_data(historical_data)
        featured_data = self.collector.add_features(clean_data)
        
        # Step 2: Train Models
        logger.info("\n--- STEP 2: Model Training ---")
        
        # Split data for validation
        split_ratio = self.config.get('train_test_split', 0.9)
        split_point = int(len(clean_data) * split_ratio)
        train_data = clean_data[:split_point]
        test_data = clean_data[split_point:]
        
        self.forecaster.train_temperature_model(train_data)
        self.forecaster.train_rainfall_model(train_data)
        
        # Step 3: Generate Forecasts
        logger.info("\n--- STEP 3: Generating Forecasts ---")
        temp_forecast = self.forecaster.predict_temperature(forecast_days)
        rain_forecast = self.forecaster.predict_rainfall(forecast_days)
        
        # Step 4: Evaluate Accuracy
        logger.info("\n--- STEP 4: Model Evaluation ---")
        
        # Predict on test set
        test_temp_forecast = self.forecaster.predict_temperature(len(test_data))
        test_rain_forecast = self.forecaster.predict_rainfall(len(test_data))
        
        temp_metrics = self.forecaster.evaluate_model(
            test_data, test_temp_forecast, 'temperature'
        )
        rain_metrics = self.forecaster.evaluate_model(
            test_data, test_rain_forecast, 'rainfall'
        )
        
        # Step 5: Risk Assessment
        logger.info("\n--- STEP 5: Risk Assessment ---")
        drought_risk = self.risk_assessor.assess_drought_risk(rain_forecast)
        flood_risk = self.risk_assessor.assess_flood_risk(rain_forecast)
        heat_risk = self.risk_assessor.assess_extreme_heat(temp_forecast)
        
        # Calculate financial impacts
        drought_impact = self.risk_assessor.calculate_financial_impact(
            drought_risk, 'drought'
        )
        
        # Step 6: Generate Alerts
        logger.info("\n--- STEP 6: Alert Generation ---")
        alerts = self.alert_system.check_thresholds(
            temp_forecast.merge(rain_forecast, on='ds', suffixes=('_temp', '_rain')),
            drought_risk
        )
        
        # Step 7: Results Summary
        logger.info("\n" + "=" * 60)
        logger.info("FORECASTING PIPELINE RESULTS")
        logger.info("=" * 60)
        
        print(f"\nModel Performance:")
        print(f"  Temperature Forecast Accuracy: {temp_metrics['accuracy']}%")
        print(f"  Rainfall Forecast Accuracy: {rain_metrics['accuracy']}%")
        print(f"  Average Accuracy: {(temp_metrics['accuracy'] + rain_metrics['accuracy']) / 2:.2f}%")
        
        print(f"\nRisk Assessment:")
        print(f"  Drought Impact: ${drought_impact['total_impact']:,.2f}")
        print(f"  High Risk Days: {drought_impact['high_risk_days']}")
        
        print(f"\nAlerts Generated: {len(alerts)}")
        print(self.alert_system.generate_alert_report())
        
        print(f"\nForecast Summary (Next {forecast_days} Days):")
        print(f"  Avg Temperature: {temp_forecast['yhat'].mean():.1f}°C")
        print(f"  Total Rainfall: {rain_forecast['yhat'].sum():.1f}mm")
        print(f"  Max Temperature: {temp_forecast['yhat'].max():.1f}°C")
        print(f"  Max Daily Rainfall: {rain_forecast['yhat'].max():.1f}mm")
        
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
        return {
            'temp_metrics': temp_metrics,
            'rain_metrics': rain_metrics,
            'temp_forecast': temp_forecast,
            'rain_forecast': rain_forecast,
            'drought_risk': drought_risk,
            'flood_risk': flood_risk,
            'heat_risk': heat_risk,
            'alerts': alerts,
            'financial_impact': drought_impact
        }