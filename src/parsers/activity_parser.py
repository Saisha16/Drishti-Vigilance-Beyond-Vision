"""
Activity Log Parsers
Supports JSON, CSV, and Syslog formats
"""
import json
import csv
import re
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from src.models.data_models import UserActivity


class ActivityParser:
    """Parse activity logs from various formats"""
    
    @staticmethod
    def parse_json(file_path: str) -> List[UserActivity]:
        """Parse JSON format activity logs"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        activities = []
        for item in data:
            activity = UserActivity(
                user_id=item['user_id'],
                timestamp=datetime.fromisoformat(item['timestamp']),
                action=item['action'],
                resource_id=item['resource_id'],
                resource_type=item['resource_type'],
                metadata=item.get('metadata', {})
            )
            activities.append(activity)
        
        return activities
    
    @staticmethod
    def parse_csv(file_path: str) -> List[UserActivity]:
        """Parse CSV format activity logs"""
        activities = []
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse metadata if present
                metadata = {}
                if 'metadata' in row and row['metadata']:
                    try:
                        metadata = json.loads(row['metadata'])
                    except:
                        metadata = {'raw': row['metadata']}
                
                activity = UserActivity(
                    user_id=row['user_id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    action=row['action'],
                    resource_id=row['resource_id'],
                    resource_type=row['resource_type'],
                    metadata=metadata
                )
                activities.append(activity)
        
        return activities
    
    @staticmethod
    def parse_syslog(file_path: str) -> List[UserActivity]:
        """
        Parse Syslog format activity logs
        
        Expected format:
        <timestamp> <hostname> <service>: user=<user_id> action=<action> resource=<resource_id> type=<resource_type>
        """
        activities = []
        
        # Syslog pattern
        pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+\S+\s+\S+:\s+user=(\S+)\s+action=(\S+)\s+resource=(\S+)\s+type=(\S+)'
        
        with open(file_path, 'r') as f:
            for line in f:
                match = re.search(pattern, line)
                if match:
                    timestamp_str, user_id, action, resource_id, resource_type = match.groups()
                    
                    # Parse timestamp
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    except:
                        # Fallback to current time if parsing fails
                        timestamp = datetime.now()
                    
                    activity = UserActivity(
                        user_id=user_id,
                        timestamp=timestamp,
                        action=action,
                        resource_id=resource_id,
                        resource_type=resource_type,
                        metadata={}
                    )
                    activities.append(activity)
        
        return activities
    
    @staticmethod
    def parse_file(file_path: str, format: str = None) -> List[UserActivity]:
        """
        Parse activity log file (auto-detect format if not specified)
        
        Args:
            file_path: Path to log file
            format: Format type ('json', 'csv', 'syslog') or None for auto-detect
        
        Returns:
            List of UserActivity objects
        """
        if format is None:
            # Auto-detect format from extension
            ext = Path(file_path).suffix.lower()
            if ext == '.json':
                format = 'json'
            elif ext == '.csv':
                format = 'csv'
            elif ext in ['.log', '.syslog']:
                format = 'syslog'
            else:
                raise ValueError(f"Cannot auto-detect format for extension: {ext}")
        
        if format == 'json':
            return ActivityParser.parse_json(file_path)
        elif format == 'csv':
            return ActivityParser.parse_csv(file_path)
        elif format == 'syslog':
            return ActivityParser.parse_syslog(file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
