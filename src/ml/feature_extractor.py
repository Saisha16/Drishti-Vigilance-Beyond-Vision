"""
Feature Extraction Engine
Extracts 45+ behavioral features from user activities
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
from collections import Counter

from src.models.data_models import UserActivity
from src.models.configuration import Configuration


class FeatureExtractor:
    """Extracts behavioral features from user activities"""
    
    def __init__(self, config: Configuration):
        self.config = config
    
    def extract_features(self, activities: List[UserActivity], reference_date: datetime = None) -> Dict[str, float]:
        """
        Extract comprehensive feature set from activities
        
        Returns dictionary with 45+ features across categories:
        - Temporal (time-based patterns)
        - Volume (activity counts and rates)
        - Behavioral (diversity and patterns)
        - Contextual (resource sensitivity, anomalies)
        """
        if not activities:
            return self._empty_features()
        
        if reference_date is None:
            reference_date = datetime.now()
        
        # Convert to DataFrame for easier analysis
        df = self._activities_to_dataframe(activities)
        
        features = {}
        
        # Temporal Features
        features.update(self._extract_temporal_features(df, reference_date))
        
        # Volume Features
        features.update(self._extract_volume_features(df))
        
        # Behavioral Features
        features.update(self._extract_behavioral_features(df))
        
        # Contextual Features
        features.update(self._extract_contextual_features(df))
        
        return features
    
    def _activities_to_dataframe(self, activities: List[UserActivity]) -> pd.DataFrame:
        """Convert activities to pandas DataFrame"""
        data = []
        for activity in activities:
            data.append({
                'timestamp': activity.timestamp,
                'action': activity.action,
                'resource_id': activity.resource_id,
                'resource_type': activity.resource_type,
                'hour': activity.timestamp.hour,
                'day_of_week': activity.timestamp.weekday(),
                'is_weekend': activity.timestamp.weekday() >= 5,
                'metadata': activity.metadata
            })
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        return df
    
    def _extract_temporal_features(self, df: pd.DataFrame, reference_date: datetime) -> Dict[str, float]:
        """Extract time-based behavioral patterns"""
        features = {}
        
        # Hour of day distribution
        hour_counts = df['hour'].value_counts()
        features['avg_hour_of_activity'] = df['hour'].mean()
        features['std_hour_of_activity'] = df['hour'].std()
        
        # Peak activity hours
        if len(hour_counts) > 0:
            features['peak_activity_hour'] = hour_counts.idxmax()
            features['peak_activity_concentration'] = hour_counts.max() / len(df)
        else:
            features['peak_activity_hour'] = 12
            features['peak_activity_concentration'] = 0
        
        # Business hours activity (9 AM - 5 PM)
        business_hours = df[(df['hour'] >= 9) & (df['hour'] <= 17)]
        features['business_hours_ratio'] = len(business_hours) / len(df) if len(df) > 0 else 0
        
        # After hours activity (10 PM - 6 AM)
        after_hours = df[(df['hour'] >= 22) | (df['hour'] <= 6)]
        features['after_hours_ratio'] = len(after_hours) / len(df) if len(df) > 0 else 0
        
        # Weekend activity
        features['weekend_activity_ratio'] = df['is_weekend'].sum() / len(df) if len(df) > 0 else 0
        
        # Day of week distribution
        features['day_of_week_entropy'] = self._calculate_entropy(df['day_of_week'].value_counts())
        
        # Activity recency
        if len(df) > 0:
            most_recent = df['timestamp'].max()
            features['days_since_last_activity'] = (reference_date - most_recent).total_seconds() / 86400
        else:
            features['days_since_last_activity'] = 999
        
        # Activity span
        if len(df) > 1:
            activity_span = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 86400
            features['activity_span_days'] = activity_span
        else:
            features['activity_span_days'] = 0
        
        return features
    
    def _extract_volume_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract activity volume and rate features"""
        features = {}
        
        # Total activity count
        features['total_activities'] = len(df)
        
        # Daily activity statistics
        if len(df) > 0:
            df['date'] = df['timestamp'].dt.date
            daily_counts = df.groupby('date').size()
            
            features['avg_daily_activities'] = daily_counts.mean()
            features['std_daily_activities'] = daily_counts.std()
            features['max_daily_activities'] = daily_counts.max()
            features['min_daily_activities'] = daily_counts.min()
        else:
            features['avg_daily_activities'] = 0
            features['std_daily_activities'] = 0
            features['max_daily_activities'] = 0
            features['min_daily_activities'] = 0
        
        # Hourly activity rate
        if len(df) > 1:
            time_span_hours = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
            features['hourly_activity_rate'] = len(df) / time_span_hours if time_span_hours > 0 else 0
        else:
            features['hourly_activity_rate'] = 0
        
        # Activity bursts (high activity in short time)
        features['activity_burst_score'] = self._calculate_burst_score(df)
        
        return features
    
    def _extract_behavioral_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract behavioral diversity and pattern features"""
        features = {}
        
        # Resource access patterns
        features['unique_resources_accessed'] = df['resource_id'].nunique()
        features['unique_resource_types'] = df['resource_type'].nunique()
        
        # Resource access frequency
        resource_counts = df['resource_id'].value_counts()
        features['avg_resource_access_frequency'] = resource_counts.mean()
        features['max_resource_access_frequency'] = resource_counts.max()
        
        # Resource concentration (Gini coefficient)
        features['resource_access_concentration'] = self._calculate_gini(resource_counts.values)
        
        # Action diversity
        action_counts = df['action'].value_counts()
        features['unique_actions'] = len(action_counts)
        features['action_entropy'] = self._calculate_entropy(action_counts)
        
        # Action distribution
        total_actions = len(df)
        for action in ['read', 'write', 'delete', 'download', 'share']:
            count = len(df[df['action'] == action])
            features[f'{action}_action_ratio'] = count / total_actions if total_actions > 0 else 0
        
        # Session patterns (activities within 1 hour = session)
        features['estimated_sessions'] = self._estimate_sessions(df)
        features['avg_activities_per_session'] = len(df) / features['estimated_sessions'] if features['estimated_sessions'] > 0 else 0
        
        # Resource type distribution
        resource_type_counts = df['resource_type'].value_counts()
        features['resource_type_entropy'] = self._calculate_entropy(resource_type_counts)
        
        return features
    
    def _extract_contextual_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract context-aware features"""
        features = {}
        
        # Resource sensitivity scoring
        sensitivity_scores = []
        for resource_type in df['resource_type']:
            score = self.config.resource_sensitivity_weights.get(resource_type, 0.5)
            sensitivity_scores.append(score)
        
        features['avg_resource_sensitivity'] = np.mean(sensitivity_scores) if sensitivity_scores else 0
        features['max_resource_sensitivity'] = np.max(sensitivity_scores) if sensitivity_scores else 0
        features['high_sensitivity_access_ratio'] = sum(1 for s in sensitivity_scores if s >= 0.8) / len(sensitivity_scores) if sensitivity_scores else 0
        
        # Unusual time access (accessing sensitive resources after hours)
        sensitive_resources = df[df['resource_type'].isin(['classified_documents', 'source_code', 'customer_data'])]
        after_hours_sensitive = sensitive_resources[(sensitive_resources['hour'] >= 22) | (sensitive_resources['hour'] <= 6)]
        features['unusual_time_sensitive_access'] = len(after_hours_sensitive) / len(df) if len(df) > 0 else 0
        
        # Sequential pattern anomalies
        features['action_sequence_diversity'] = self._calculate_sequence_diversity(df)
        
        return features
    
    def _calculate_entropy(self, counts: pd.Series) -> float:
        """Calculate Shannon entropy"""
        if len(counts) == 0:
            return 0
        probabilities = counts / counts.sum()
        return -np.sum(probabilities * np.log2(probabilities + 1e-10))
    
    def _calculate_gini(self, values: np.ndarray) -> float:
        """Calculate Gini coefficient (0 = perfect equality, 1 = perfect inequality)"""
        if len(values) == 0:
            return 0
        sorted_values = np.sort(values)
        n = len(values)
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n
    
    def _calculate_burst_score(self, df: pd.DataFrame) -> float:
        """Calculate activity burst score (high activity in short windows)"""
        if len(df) < 2:
            return 0
        
        # Calculate activities per 1-hour window
        df = df.sort_values('timestamp')
        window_counts = []
        
        for i in range(len(df)):
            window_end = df.iloc[i]['timestamp']
            window_start = window_end - timedelta(hours=1)
            count = len(df[(df['timestamp'] >= window_start) & (df['timestamp'] <= window_end)])
            window_counts.append(count)
        
        # Burst score is the 95th percentile of window counts
        return np.percentile(window_counts, 95) if window_counts else 0
    
    def _estimate_sessions(self, df: pd.DataFrame) -> int:
        """Estimate number of sessions (gap > 1 hour = new session)"""
        if len(df) < 2:
            return 1
        
        df = df.sort_values('timestamp')
        time_diffs = df['timestamp'].diff()
        session_breaks = (time_diffs > timedelta(hours=1)).sum()
        return session_breaks + 1
    
    def _calculate_sequence_diversity(self, df: pd.DataFrame) -> float:
        """Calculate diversity of action sequences"""
        if len(df) < 2:
            return 0
        
        # Create bigrams of consecutive actions
        actions = df.sort_values('timestamp')['action'].tolist()
        bigrams = [(actions[i], actions[i+1]) for i in range(len(actions)-1)]
        
        # Calculate unique bigrams ratio
        unique_bigrams = len(set(bigrams))
        total_bigrams = len(bigrams)
        
        return unique_bigrams / total_bigrams if total_bigrams > 0 else 0
    
    def _empty_features(self) -> Dict[str, float]:
        """Return empty feature set with default values"""
        return {
            'avg_hour_of_activity': 12,
            'std_hour_of_activity': 0,
            'peak_activity_hour': 12,
            'peak_activity_concentration': 0,
            'business_hours_ratio': 0,
            'after_hours_ratio': 0,
            'weekend_activity_ratio': 0,
            'day_of_week_entropy': 0,
            'days_since_last_activity': 999,
            'activity_span_days': 0,
            'total_activities': 0,
            'avg_daily_activities': 0,
            'std_daily_activities': 0,
            'max_daily_activities': 0,
            'min_daily_activities': 0,
            'hourly_activity_rate': 0,
            'activity_burst_score': 0,
            'unique_resources_accessed': 0,
            'unique_resource_types': 0,
            'avg_resource_access_frequency': 0,
            'max_resource_access_frequency': 0,
            'resource_access_concentration': 0,
            'unique_actions': 0,
            'action_entropy': 0,
            'read_action_ratio': 0,
            'write_action_ratio': 0,
            'delete_action_ratio': 0,
            'download_action_ratio': 0,
            'share_action_ratio': 0,
            'estimated_sessions': 0,
            'avg_activities_per_session': 0,
            'resource_type_entropy': 0,
            'avg_resource_sensitivity': 0,
            'max_resource_sensitivity': 0,
            'high_sensitivity_access_ratio': 0,
            'unusual_time_sensitive_access': 0,
            'action_sequence_diversity': 0
        }
