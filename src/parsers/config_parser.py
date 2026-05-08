"""
Configuration File Parser
Supports YAML and JSON configuration files
"""
import json
import yaml
from pathlib import Path

from src.models.configuration import Configuration


class ConfigParser:
    """Parse configuration files"""
    
    @staticmethod
    def parse_yaml(file_path: str) -> Configuration:
        """Parse YAML configuration file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return Configuration.from_dict(data)
    
    @staticmethod
    def parse_json(file_path: str) -> Configuration:
        """Parse JSON configuration file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return Configuration.from_dict(data)
    
    @staticmethod
    def parse_file(file_path: str) -> Configuration:
        """Parse configuration file (auto-detect format)"""
        ext = Path(file_path).suffix.lower()
        
        if ext in ['.yaml', '.yml']:
            return ConfigParser.parse_yaml(file_path)
        elif ext == '.json':
            return ConfigParser.parse_json(file_path)
        else:
            raise ValueError(f"Unsupported configuration format: {ext}")
    
    @staticmethod
    def save_yaml(config: Configuration, file_path: str):
        """Save configuration to YAML file"""
        with open(file_path, 'w') as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False)
    
    @staticmethod
    def save_json(config: Configuration, file_path: str):
        """Save configuration to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
