"""
Error detection module for Terraform plan output.
"""
import re
from typing import Dict, List, Optional

from ..models import Error, ErrorType, AffectedResource


class ErrorDetector:
    """
    Detects and classifies errors in Terraform plan output.
    """
    
    # Error pattern to type mapping
    ERROR_PATTERNS = {
        # Validation errors
        r'validation failed': ErrorType.VALIDATION,
        r'expected\s+.*\s+but\s+got': ErrorType.VALIDATION,
        r'required field is not set': ErrorType.VALIDATION,
        r'value must be one of': ErrorType.VALIDATION,
        r'must contain at least': ErrorType.VALIDATION,
        r'invalid value': ErrorType.VALIDATION,
        
        # Dependency errors
        r'unknown resource': ErrorType.DEPENDENCY,
        r'depends on resource': ErrorType.DEPENDENCY,
        r'referenced by': ErrorType.DEPENDENCY,
        r'cyclic dependency': ErrorType.DEPENDENCY,
        r'cannot resolve': ErrorType.DEPENDENCY,
        
        # Permission errors
        r'access denied': ErrorType.PERMISSION,
        r'not authorized': ErrorType.PERMISSION,
        r'permission denied': ErrorType.PERMISSION,
        r'credentials': ErrorType.PERMISSION,
        r'authentication': ErrorType.PERMISSION,
        r'forbidden': ErrorType.PERMISSION,
        
        # Syntax errors
        r'syntax error': ErrorType.SYNTAX,
        r'expected ["\(]': ErrorType.SYNTAX,
        r'unexpected ["\)]': ErrorType.SYNTAX,
        r'invalid block definition': ErrorType.SYNTAX,
        
        # Resource conflicts
        r'already exists': ErrorType.RESOURCE_CONFLICT,
        r'conflicts with': ErrorType.RESOURCE_CONFLICT,
        r'duplicate': ErrorType.RESOURCE_CONFLICT,
        r'in use': ErrorType.RESOURCE_CONFLICT,
        
        # State mismatch
        r'state is out of date': ErrorType.STATE_MISMATCH,
        r'does not match': ErrorType.STATE_MISMATCH,
        r'importing': ErrorType.STATE_MISMATCH,
        r'drift detected': ErrorType.STATE_MISMATCH,
        
        # Provider errors
        r'provider': ErrorType.PROVIDER,
        r'plugin': ErrorType.PROVIDER,
        r'registry.terraform.io': ErrorType.PROVIDER,
        
        # Module errors
        r'module': ErrorType.MODULE,
        r'source': ErrorType.MODULE,
        r'version constraint': ErrorType.MODULE,
    }
    
    def __init__(self, error_contexts: List[Dict[str, str]]):
        """
        Initialize the error detector with error contexts from the parser.
        
        Args:
            error_contexts: List of error context dictionaries from the parser
        """
        self.error_contexts = error_contexts
    
    def detect_errors(self) -> List[Error]:
        """
        Detect and classify errors from the provided error contexts.
        
        Returns:
            List of Error objects with detected errors
        """
        errors = []
        
        for context in self.error_contexts:
            error_type = self._classify_error_type(context['message'])
            
            affected_resource = None
            if context.get('resource_type') and context.get('resource_name'):
                affected_resource = AffectedResource(
                    name=context['resource_name'],
                    type=context['resource_type'],
                    address=f"{context['resource_type']}.{context['resource_name']}"
                )
            
            error = Error(
                errorType=error_type,
                message=self._humanize_error_message(context['message'], error_type),
                affectedResources=[affected_resource] if affected_resource else []
            )
            
            errors.append(error)
            
        return errors
    
    def _classify_error_type(self, error_message: str) -> ErrorType:
        """
        Classify an error message into a specific error type.
        
        Args:
            error_message: The raw error message
            
        Returns:
            ErrorType enum value for the detected error type
        """
        for pattern, error_type in self.ERROR_PATTERNS.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                return error_type
        
        return ErrorType.OTHER
    
    def _humanize_error_message(self, error_message: str, error_type: ErrorType) -> str:
        """
        Convert the technical error message to a human-friendly explanation.
        
        Args:
            error_message: Raw error message
            error_type: Detected error type
            
        Returns:
            A human-friendly error explanation
        """
        # Extract the most relevant part of the error message
        # Remove common prefixes and normalize whitespace
        message = re.sub(r'Error:\s+', '', error_message)
        message = re.sub(r'\s+', ' ', message).strip()
        
        # Make the message more human-friendly based on error type
        if error_type == ErrorType.VALIDATION:
            # Extract the key validation information
            validation_info = re.search(r'(.*?)(expected|required|must|invalid)(.+)', message)
            if validation_info:
                field = validation_info.group(1).strip()
                issue = validation_info.group(2).strip() + validation_info.group(3).strip()
                return f"The value for '{field}' is invalid. {issue}."
            
        elif error_type == ErrorType.PERMISSION:
            return f"You don't have sufficient permissions: {message}"
            
        elif error_type == ErrorType.DEPENDENCY:
            return f"There's a dependency issue: {message}"
            
        elif error_type == ErrorType.SYNTAX:
            return f"There's a syntax error in your configuration: {message}"
            
        elif error_type == ErrorType.RESOURCE_CONFLICT:
            return f"Resource conflict detected: {message}"
            
        elif error_type == ErrorType.STATE_MISMATCH:
            return f"The Terraform state doesn't match the actual infrastructure: {message}"
        
        elif error_type == ErrorType.PROVIDER:
            return f"There's an issue with the provider configuration: {message}"
            
        elif error_type == ErrorType.MODULE:
            return f"There's an issue with a module: {message}"
        
        # If no specific humanizing rule applies, return the cleaned message
        return message