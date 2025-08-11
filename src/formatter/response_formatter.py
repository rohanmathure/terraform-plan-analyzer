"""
Response formatter for generating the final consolidated JSON output.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional

from src.models import AnalysisResponse, Error, ResponseStatus, Metadata, ResourceCounts


class ResponseFormatter:
    """
    Formats the analysis results into the final JSON response.
    """
    
    def __init__(self, errors: List[Error], resource_counts: Optional[ResourceCounts] = None):
        """
        Initialize the formatter with detected errors and resource counts.
        
        Args:
            errors: List of Error objects with recommendations
            resource_counts: Optional ResourceCounts object with plan resource counts
        """
        self.errors = errors
        self.resource_counts = resource_counts
    
    def format_response(self) -> str:
        """
        Format the final JSON response.
        
        Returns:
            JSON string with the formatted response
        """
        # Generate metadata
        metadata = Metadata(
            timestamp=datetime.now(),
            resourceCount=self.resource_counts
        )
        
        # Determine overall status
        status = self._determine_status()
        
        # Generate summary
        summary = self._generate_summary(status)
        
        # Create the response object
        response = AnalysisResponse(
            status=status,
            summary=summary,
            errors=self.errors,
            metadata=metadata
        )
        
        # Convert to JSON
        return response.model_dump_json(indent=2, exclude_none=True)
    
    def _determine_status(self) -> ResponseStatus:
        """
        Determine the overall status of the analysis.
        
        Returns:
            ResponseStatus enum value
        """
        if not self.errors:
            return ResponseStatus.SUCCESS
        
        # If we have errors but no recommendations with high confidence
        high_confidence_recs = any(
            any(rec.confidence == "high" for rec in error.recommendations)
            for error in self.errors
        )
        
        if not high_confidence_recs:
            return ResponseStatus.UNKNOWN
            
        return ResponseStatus.ERROR
    
    def _generate_summary(self, status: ResponseStatus) -> str:
        """
        Generate a friendly summary of the analysis.
        
        Args:
            status: The determined response status
            
        Returns:
            Summary string
        """
        if status == ResponseStatus.SUCCESS:
            return "Your Terraform plan looks good! No errors were detected."
        
        error_count = len(self.errors)
        
        if status == ResponseStatus.UNKNOWN:
            return f"Found {error_count} issue{'s' if error_count != 1 else ''} in your Terraform plan, but couldn't determine specific solutions. Check the error details for more information."
        
        # Group errors by type
        error_types = {}
        for error in self.errors:
            if error.errorType not in error_types:
                error_types[error.errorType] = 0
            error_types[error.errorType] += 1
        
        # Find the most common error type
        most_common_type = max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        
        if most_common_type:
            return f"Found {error_count} issue{'s' if error_count != 1 else ''} in your Terraform plan. Most are related to {most_common_type} problems. Check the recommendations for solutions."
        else:
            return f"Found {error_count} issue{'s' if error_count != 1 else ''} in your Terraform plan. Check the recommendations for solutions."