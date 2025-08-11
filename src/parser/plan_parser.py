"""
Parser module for Terraform plan output.
"""
import re
from typing import Dict, List, Optional, Tuple

from src.models import ResourceCounts


class TerraformPlanParser:
    """
    Parser for Terraform plan output that extracts structured information.
    """

    def __init__(self, plan_output: str):
        """
        Initialize the parser with the terraform plan output.
        
        Args:
            plan_output: Raw terraform plan output as a string
        """
        self.plan_output = plan_output
        self.plan_sections = self._split_into_sections()
        
    def _split_into_sections(self) -> Dict[str, str]:
        """
        Split the plan output into meaningful sections.
        
        Returns:
            Dictionary containing sections of the plan
        """
        sections = {
            'header': '',
            'terraform_version': '',
            'initialization': '',
            'plan': '',
            'changes': '',
            'errors': ''
        }
        
        # Extract terraform version
        version_match = re.search(r'Terraform\s+v(\d+\.\d+\.\d+)', self.plan_output)
        if version_match:
            sections['terraform_version'] = version_match.group(1)
        
        # Extract plan summary and changes
        plan_section = re.search(
            r'(Plan:.*?)(?=\n\n|\Z)', 
            self.plan_output, 
            re.DOTALL
        )
        if plan_section:
            sections['plan'] = plan_section.group(1).strip()
        
        # Extract error messages
        error_patterns = [
            r'Error: (.*?)(?=\n\n|\Z)',
            r'│ Error: (.*?)(?=\n\n|\Z)',
            r'╷\s*│\s*Error: (.*?)(?=\n\n|\Z)'
        ]
        
        all_errors = []
        for pattern in error_patterns:
            errors = re.findall(pattern, self.plan_output, re.DOTALL)
            all_errors.extend(errors)
        
        if all_errors:
            sections['errors'] = '\n\n'.join([e.strip() for e in all_errors])
        
        return sections
    
    def extract_resource_counts(self) -> Optional[ResourceCounts]:
        """
        Extract resource count information from the plan.
        
        Returns:
            ResourceCounts object containing the number of resources to add, change, destroy
        """
        if not self.plan_sections.get('plan'):
            return None
        
        plan_text = self.plan_sections['plan']
        
        # Extract resource counts using regex
        add_match = re.search(r'(\d+) to add', plan_text)
        change_match = re.search(r'(\d+) to change', plan_text)
        destroy_match = re.search(r'(\d+) to destroy', plan_text)
        
        add_count = int(add_match.group(1)) if add_match else 0
        change_count = int(change_match.group(1)) if change_match else 0
        destroy_count = int(destroy_match.group(1)) if destroy_match else 0
        
        return ResourceCounts(
            add=add_count,
            change=change_count,
            destroy=destroy_count
        )
    
    def has_errors(self) -> bool:
        """
        Check if the plan contains errors.
        
        Returns:
            True if errors were detected, False otherwise
        """
        return bool(self.plan_sections.get('errors'))
    
    def extract_error_contexts(self) -> List[Dict[str, str]]:
        """
        Extract errors with their surrounding context.
        
        Returns:
            List of dictionaries with error information and context
        """
        if not self.has_errors():
            return []
        
        error_contexts = []
        error_blocks = re.split(r'\n\s*\n', self.plan_sections['errors'])
        
        for block in error_blocks:
            # Skip empty blocks
            if not block.strip():
                continue
                
            # Extract the error message and any resource information
            error_message = block.strip()
            resource_match = re.search(r'on\s+([^:]+):(\d+)', block)
            resource_path = resource_match.group(1) if resource_match else None
            line_number = resource_match.group(2) if resource_match else None
            
            # Extract any resource address
            address_match = re.search(r'resource "([^"]+)" "([^"]+)"', block)
            resource_type = address_match.group(1) if address_match else None
            resource_name = address_match.group(2) if address_match else None
            
            # Extract resource address from other formats
            if not resource_type or not resource_name:
                alt_address = re.search(r'([a-zA-Z0-9_\-.]+\.[a-zA-Z0-9_\-.]+)(?:\[\d+\])?', block)
                if alt_address:
                    parts = alt_address.group(1).split('.')
                    if len(parts) >= 2:
                        resource_type = parts[-2]
                        resource_name = parts[-1]
            
            error_contexts.append({
                'message': error_message,
                'resource_path': resource_path,
                'line_number': line_number,
                'resource_type': resource_type,
                'resource_name': resource_name
            })
        
        return error_contexts