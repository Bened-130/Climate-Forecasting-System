import pandas as pd
import numpy as np
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RiskAssessor:
    """Assess climate-related risks"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize risk assessor"""
        self.config = config or {}
        logger.info("RiskAssessor initialized")
    
    def assess_drought_risk(self, forecast_df: pd.DataFrame) -> pd.DataFrame:
        """Assess drought risk from rainfall forecast"""
        logger.info("Assessing drought risk")
        
        risk_df = forecast_df.copy()
        
        # Calculate 21-day rolling sum of rainfall
        risk_df['rainfall_21d'] = risk_df['yhat'].rolling(21).sum()
        
        # Get thresholds from config
        thresholds = self.config.get('drought', {})
        
        # Define drought thresholds
        risk_df['drought_risk'] = pd.cut(
            risk_df['rainfall_21d'],
            bins=[-np.inf, thresholds.get('high', 50), thresholds.get('medium', 150), np.inf],
            labels=['High', 'Medium', 'Low']
        )
        
        # Calculate risk score (0-100)
        risk_df['risk_score'] = 100 - np.clip(risk_df['rainfall_21d'] / 3, 0, 100)
        
        return risk_df
    
    def assess_flood_risk(self, forecast_df: pd.DataFrame) -> pd.DataFrame:
        """Assess flood risk from rainfall forecast"""
        logger.info("Assessing flood risk")
        
        risk_df = forecast_df.copy()
        
        # Calculate 7-day rolling sum
        risk_df['rainfall_7d'] = risk_df['yhat'].rolling(7).sum()
        
        # Get thresholds from config
        thresholds = self.config.get('flood', {})
        
        # Define flood thresholds
        risk_df['flood_risk'] = pd.cut(
            risk_df['rainfall_7d'],
            bins=[-np.inf, thresholds.get('low', 100), thresholds.get('medium', 200), np.inf],
            labels=['Low', 'Medium', 'High']
        )
        
        # Calculate risk score
        risk_df['risk_score'] = np.clip(risk_df['rainfall_7d'] / 5, 0, 100)
        
        return risk_df
    
    def assess_extreme_heat(self, forecast_df: pd.DataFrame) -> pd.DataFrame:
        """Assess extreme heat risk"""
        logger.info("Assessing extreme heat risk")
        
        risk_df = forecast_df.copy()
        
        # Get thresholds from config
        thresholds = self.config.get('extreme_heat', {})
        
        # Define heat thresholds
        risk_df['heat_risk'] = pd.cut(
            risk_df['yhat'],
            bins=[-np.inf, thresholds.get('medium', 30), thresholds.get('high', 35), np.inf],
            labels=['Low', 'Medium', 'High']
        )
        
        # Calculate consecutive hot days
        risk_df['consecutive_hot_days'] = (
            (risk_df['yhat'] > thresholds.get('high', 35)).groupby(
                (risk_df['yhat'] <= thresholds.get('high', 35)).cumsum()
            ).cumsum()
        )
        
        return risk_df
    
    def calculate_financial_impact(self, risk_df: pd.DataFrame, 
                                   risk_type: str = 'drought') -> Dict[str, Any]:
        """Calculate potential financial impact"""
        logger.info(f"Calculating financial impact of {risk_type}")
        
        # Get impact values from config
        impact_values = self.config.get('financial_impact', {})
        
        risk_col = f'{risk_type}_risk'
        if risk_col not in risk_df.columns:
            return {'total_impact': 0, 'high_risk_days': 0}
        
        # Calculate total potential impact
        total_impact = sum([
            impact_values.get(level, 0) * (risk_df[risk_col] == level).sum()
            for level in ['High', 'Medium', 'Low']
            if level in risk_df[risk_col].values
        ])
        
        high_risk_days = (risk_df[risk_col] == 'High').sum()
        
        return {
            'total_impact': total_impact,
            'high_risk_days': high_risk_days,
            'medium_risk_days': (risk_df[risk_col] == 'Medium').sum(),
            'low_risk_days': (risk_df[risk_col] == 'Low').sum()
        }