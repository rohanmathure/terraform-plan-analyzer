"""
Tests for the Terraform Plan Analyzer agent.
"""
import json
import os
import pytest
from pathlib import Path

# Add the src directory to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import analyze_terraform_plan, parse_json_response


def test_analyze_plan_with_errors():
    """Test analyzing a plan with errors."""
    # Load example plan with errors
    example_file = Path(__file__).parent.parent / 'examples' / 'example_plan_with_errors.txt'
    with open(example_file, 'r') as f:
        plan_output = f.read()
    
    # Analyze the plan
    result_json = analyze_terraform_plan(plan_output)
    
    # Parse the result
    result = parse_json_response(result_json)
    
    # Verify the basic structure
    assert 'status' in result
    assert 'summary' in result
    assert 'errors' in result
    assert 'metadata' in result
    
    # Verify the status
    assert result['status'] == 'error'
    
    # Verify we have errors
    assert len(result['errors']) > 0
    
    # Verify each error has recommendations
    for error in result['errors']:
        assert 'errorType' in error
        assert 'message' in error
        assert 'recommendations' in error
        assert len(error['recommendations']) > 0


def test_analyze_plan_no_errors():
    """Test analyzing a plan without errors."""
    # Create a minimal plan with no errors
    plan_output = """
Terraform v1.5.4
on darwin_amd64

No changes. Your infrastructure matches the configuration.

Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
"""
    
    # Analyze the plan
    result_json = analyze_terraform_plan(plan_output)
    
    # Parse the result
    result = parse_json_response(result_json)
    
    # Verify the status is success
    assert result['status'] == 'success'
    
    # Verify there are no errors
    assert len(result['errors']) == 0


if __name__ == "__main__":
    pytest.main([__file__])