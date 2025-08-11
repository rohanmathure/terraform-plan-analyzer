"""
Main agent module that orchestrates the Terraform plan analysis.
"""
import json
from typing import Dict, Any, Optional

from .parser.plan_parser import TerraformPlanParser
from .error_detector.detector import ErrorDetector
from .recommender.engine import RecommendationEngine
from .formatter.response_formatter import ResponseFormatter
from .models import AnalysisResponse, ResponseStatus


def analyze_terraform_plan(plan_output: str) -> str:
    """
    Analyze a Terraform plan output and provide recommendations.
    
    Args:
        plan_output: Raw Terraform plan output as a string
        
    Returns:
        JSON string with analysis results and recommendations
    """
    # 1. Parse the plan output
    parser = TerraformPlanParser(plan_output)
    resource_counts = parser.extract_resource_counts()
    error_contexts = parser.extract_error_contexts()
    
    # If no errors detected and we have resource counts, return success
    if not error_contexts:
        formatter = ResponseFormatter([], resource_counts)
        return formatter.format_response()
    
    # 2. Detect and classify errors
    detector = ErrorDetector(error_contexts)
    errors = detector.detect_errors()
    
    # If no errors could be detected from the contexts, return unknown
    if not errors:
        formatter = ResponseFormatter([], resource_counts)
        return formatter.format_response()
    
    # 3. Generate recommendations for errors
    recommender = RecommendationEngine(errors)
    errors_with_recommendations = recommender.generate_recommendations()
    
    # 4. Format the response
    formatter = ResponseFormatter(errors_with_recommendations, resource_counts)
    return formatter.format_response()


def parse_json_response(json_str: str) -> Dict[str, Any]:
    """
    Parse the JSON response string to a dictionary.
    
    Args:
        json_str: JSON response string
        
    Returns:
        Dictionary representation of the JSON response
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "summary": "Failed to parse analysis results",
            "errors": []
        }