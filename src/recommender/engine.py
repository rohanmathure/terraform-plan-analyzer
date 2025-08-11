"""
Recommendation engine for Terraform plan errors.
"""
import re
from typing import Dict, List, Optional

from src.models import Error, ErrorType, Recommendation, ConfidenceLevel, AffectedResource


class RecommendationEngine:
    """
    Generates recommendations for fixing errors in Terraform plans.
    """
    
    def __init__(self, errors: List[Error]):
        """
        Initialize the recommendation engine with detected errors.
        
        Args:
            errors: List of Error objects from the error detector
        """
        self.errors = errors
    
    def generate_recommendations(self) -> List[Error]:
        """
        Generate recommendations for each error.
        
        Returns:
            Updated list of Error objects with recommendations added
        """
        for error in self.errors:
            recommendations = self._generate_recommendations_for_error(error)
            error.recommendations = recommendations
            
        return self.errors
    
    def _generate_recommendations_for_error(self, error: Error) -> List[Recommendation]:
        """
        Generate recommendations for a specific error.
        
        Args:
            error: An Error object
            
        Returns:
            List of Recommendation objects
        """
        if error.errorType == ErrorType.VALIDATION:
            return self._recommendations_for_validation(error)
        elif error.errorType == ErrorType.DEPENDENCY:
            return self._recommendations_for_dependency(error)
        elif error.errorType == ErrorType.PERMISSION:
            return self._recommendations_for_permission(error)
        elif error.errorType == ErrorType.SYNTAX:
            return self._recommendations_for_syntax(error)
        elif error.errorType == ErrorType.RESOURCE_CONFLICT:
            return self._recommendations_for_conflict(error)
        elif error.errorType == ErrorType.STATE_MISMATCH:
            return self._recommendations_for_state_mismatch(error)
        elif error.errorType == ErrorType.PROVIDER:
            return self._recommendations_for_provider(error)
        elif error.errorType == ErrorType.MODULE:
            return self._recommendations_for_module(error)
        else:
            return self._recommendations_for_other(error)
    
    def _recommendations_for_validation(self, error: Error) -> List[Recommendation]:
        """Generate recommendations for validation errors."""
        recommendations = []
        
        # Extract field and expected value patterns
        field_match = re.search(r'value for \'([^\']+)\'', error.message)
        expected_match = re.search(r'expected (.+)', error.message)
        required_match = re.search(r'required field', error.message)
        
        field = field_match.group(1) if field_match else "the field"
        
        if expected_match:
            expected_value = expected_match.group(1)
            recommendations.append(
                Recommendation(
                    description=f"Update {field} to match the expected format: {expected_value}",
                    confidence=ConfidenceLevel.HIGH
                )
            )
        
        elif required_match:
            resource_type = error.affectedResources[0].type if error.affectedResources else "resource"
            recommendations.append(
                Recommendation(
                    description=f"Add the required '{field}' field to your {resource_type} configuration",
                    code=f"resource \"{resource_type}\" \"name\" \n  # Add this required field\n  {field} = \"value\"\n  # ... other configuration ...\n",
                    confidence=ConfidenceLevel.HIGH
                )
            )
        
        else:
            recommendations.append(
                Recommendation(
                    description=f"Check the documentation for valid values of '{field}' and update your configuration accordingly",
                    confidence=ConfidenceLevel.MEDIUM
                )
            )
            
        return recommendations
    
    def _recommendations_for_dependency(self, error: Error) -> List[Recommendation]:
        """Generate recommendations for dependency errors."""
        recommendations = []
        
        # Check for unknown resource references
        unknown_match = re.search(r'unknown resource \'([^\']+)\'', error.message)
        cycle_match = re.search(r'cyclic dependency', error.message)
        
        if unknown_match:
            resource_ref = unknown_match.group(1)
            recommendations.append(
                Recommendation(
                    description=f"Define the missing resource '{resource_ref}' or correct the reference if it's misspelled",
                    confidence=ConfidenceLevel.HIGH
                )
            )
            
            recommendations.append(
                Recommendation(
                    description=f"Ensure that the resource '{resource_ref}' is in the correct module scope",
                    confidence=ConfidenceLevel.MEDIUM
                )
            )
            
        elif cycle_match:
            recommendations.append(
                Recommendation(
                    description="Break the circular dependency between resources by restructuring your configuration",
                    confidence=ConfidenceLevel.MEDIUM
                )
            )
            
            recommendations.append(
                Recommendation(
                    description="Consider using a local value or variable to break the dependency cycle",
                    code="locals {\n  intermediate_value = \"something\"\n}\n\nresource \"type\" \"name\" {\n  property = local.intermediate_value\n}",
                    confidence=ConfidenceLevel.MEDIUM
                )
            )
        
        else:
            recommendations.append(
                Recommendation(
                    description="Check that all referenced resources exist and are correctly spelled",
                    confidence=ConfidenceLevel.MEDIUM
                )
            )
            
            recommendations.append(
                Recommendation(
                    description="Make sure your resource dependencies are correctly defined using depends_on if needed",
                    code="resource \"type\" \"name\" {\n  # ...\n  depends_on = [\n    resource.dependency\n  ]\n}",
                    confidence=ConfidenceLevel.MEDIUM
                )
            )
            
        return recommendations
    
    def _recommendations_for_permission(self, error: Error) -> List[Recommendation]:
        """Generate recommendations for permission errors."""
        recommendations = []
        
        # Common provider patterns
        aws_match = re.search(r'(AWS|IAM|arn:aws)', error.message)
        azure_match = re.search(r'(Azure|Microsoft)', error.message)
        
        # General permission recommendation
        recommendations.append(
            Recommendation(
                description="Check that your credentials have sufficient permissions for this operation",
                confidence=ConfidenceLevel.HIGH
            )
        )
        
        if aws_match:
            recommendations.append(
                Recommendation(
                    description="Ensure your AWS IAM user or role has the necessary permissions to manage these resources",
                    code="{\n  \"Version\": \"2012-10-17\",\n  \"Statement\": [\n    {\n      \"Effect\": \"Allow\",\n      \"Action\": [\n        \"service:Action\"\n      ],\n      \"Resource\": \"*\"\n    }\n  ]\n}",
                    confidence=ConfidenceLevel.MEDIUM
                )
            )
            
        elif azure_match:
            recommendations.append(
                Recommendation(
                    description="Check that your Azure service principal has the required role assignments",
                    code="az role assignment create --assignee \"$CLIENT_ID\" --role \"Contributor\" --scope \"/subscriptions/$SUBSCRIPTION_ID\"",
                    confidence=ConfidenceLevel.MEDIUM
                )
            )
            
        recommendations.append(
            Recommendation(
                description="Verify that your authentication credentials are correct and not expired",
                confidence=ConfidenceLevel.MEDIUM
            )
        )
        
        return recommendations
    
    def _recommendations_for_syntax(self, error: Error) -> List[Recommendation]:
        """Generate recommendations for syntax errors."""
        recommendations = []
        
        # Common syntax issues
        quotes_match = re.search(r'(expected|missing) (quote|")', error.message)
        brackets_match = re.search(r'(expected|missing) (bracket|{|}|\(|\))', error.message)
        
        if quotes_match:
            recommendations.append(
                Recommendation(
                    description="Check for missing or unbalanced quotes in your configuration",
                    confidence=ConfidenceLevel.HIGH
                )
            )
            
        elif brackets_match:
            recommendations.append(
                Recommendation(
                    description="Fix unbalanced brackets or braces in your configuration",
                    confidence=ConfidenceLevel.HIGH
                )
            )
            
        recommendations.append(
            Recommendation(
                description="Run 'terraform fmt' to automatically fix minor syntax issues",
                code="terraform fmt",
                confidence=ConfidenceLevel.HIGH
            )
        )
        
        recommendations.append(
            Recommendation(
                description="Check the HCL syntax documentation for proper formatting",
                confidence=ConfidenceLevel.MEDIUM
            )
        )
        
        return recommendations
    
    def _recommendations_for_conflict(self, error: Error) -> List[Recommendation]:
        """Generate recommendations for resource conflicts."""
        recommendations = []
        
        # Extract resource information if available
        resource_type = error.affectedResources[0].type if error.affectedResources else "resource"
        resource_name = error.affectedResources[0].name if error.affectedResources else "name"
        
        # Check for common conflict patterns
        exists_match = re.search(r'already exists', error.message)
        in_use_match = re.search(r'in use', error.message)
        
        if exists_match:
            recommendations.append(
                Recommendation(
                    description=f"Import the existing resource into your Terraform state instead of creating a new one",
                    code=f"terraform import {resource_type}.{resource_name} <resource_id>",
                    confidence=ConfidenceLevel.HIGH
                )
            )
            
            recommendations.append(
                Recommendation(
                    description=f"Use a different name for your {resource_type} to avoid the conflict",
                    confidence=ConfidenceLevel.MEDIUM
                )
            )
            
        elif in_use_match:
            recommendations.append(
                Recommendation(
                    description="Identify and remove the dependency on this resource before making changes",
                    confidence=ConfidenceLevel.MEDIUM
                )
            )
            
        recommendations.append(
            Recommendation(
                description="Check if you can use 'terraform state rm' to remove the conflicting resource from state if it no longer exists",
                code=f"terraform state rm {resource_type}.{resource_name}",
                confidence=ConfidenceLevel.LOW
            )
        )
        
        return recommendations
    
    def _recommendations_for_state_mismatch(self, error: Error) -> List[Recommendation]:
        """Generate recommendations for state mismatch errors."""
        recommendations = []
        
        # Extract resource information if available
        resource_type = error.affectedResources[0].type if error.affectedResources else "resource"
        resource_name = error.affectedResources[0].name if error.affectedResources else "name"
        
        recommendations.append(
            Recommendation(
                description="Refresh the Terraform state to match the current real infrastructure",
                code="terraform refresh",
                confidence=ConfidenceLevel.HIGH
            )
        )
        
        recommendations.append(
            Recommendation(
                description=f"Import the existing resource into your Terraform state",
                code=f"terraform import {resource_type}.{resource_name} <resource_id>",
                confidence=ConfidenceLevel.MEDIUM
            )
        )
        
        recommendations.append(
            Recommendation(
                description="If the resource has been manually modified, update your configuration to match the current state",
                confidence=ConfidenceLevel.MEDIUM
            )
        )
        
        return recommendations
    
    def _recommendations_for_provider(self, error: Error) -> List[Recommendation]:
        """Generate recommendations for provider errors."""
        recommendations = []
        
        # Check for common provider issues
        version_match = re.search(r'version', error.message)
        plugin_match = re.search(r'plugin|binary', error.message)
        
        if version_match:
            recommendations.append(
                Recommendation(
                    description="Update your provider version constraint in the required_providers block",
                    code='terraform {\n  required_providers {\n    aws = {\n      source  = "hashicorp/aws"\n      version = "~> 4.0"\n    }\n  }\n}',
                    confidence=ConfidenceLevel.HIGH
                )
            )
            
        elif plugin_match:
            recommendations.append(
                Recommendation(
                    description="Reinstall the provider plugin by running terraform init",
                    code="terraform init -upgrade",
                    confidence=ConfidenceLevel.HIGH
                )
            )
            
        recommendations.append(
            Recommendation(
                description="Check your provider configuration for any missing required attributes",
                confidence=ConfidenceLevel.MEDIUM
            )
        )
        
        return recommendations
    
    def _recommendations_for_module(self, error: Error) -> List[Recommendation]:
        """Generate recommendations for module errors."""
        recommendations = []
        
        # Check for common module issues
        source_match = re.search(r'source', error.message)
        version_match = re.search(r'version', error.message)
        
        if source_match:
            recommendations.append(
                Recommendation(
                    description="Check that the module source URL is correct and accessible",
                    code='module "example" {\n  source = "hashicorp/consul/aws"\n  version = "0.1.0"\n}',
                    confidence=ConfidenceLevel.HIGH
                )
            )
            
        elif version_match:
            recommendations.append(
                Recommendation(
                    description="Update the module version to a compatible version",
                    code='module "example" {\n  source  = "hashicorp/consul/aws"\n  version = "~> 0.1.0"\n}',
                    confidence=ConfidenceLevel.HIGH
                )
            )
            
        recommendations.append(
            Recommendation(
                description="Run terraform init to download any missing modules",
                code="terraform init",
                confidence=ConfidenceLevel.MEDIUM
            )
        )
        
        return recommendations
    
    def _recommendations_for_other(self, error: Error) -> List[Recommendation]:
        """Generate general recommendations for unclassified errors."""
        recommendations = [
            Recommendation(
                description="Check the Terraform documentation for this specific error message",
                confidence=ConfidenceLevel.MEDIUM
            ),
            Recommendation(
                description="Try running 'terraform validate' for more detailed error information",
                code="terraform validate",
                confidence=ConfidenceLevel.MEDIUM
            ),
            Recommendation(
                description="Make sure you're using a compatible Terraform version for your configuration",
                confidence=ConfidenceLevel.LOW
            )
        ]
        
        return recommendations