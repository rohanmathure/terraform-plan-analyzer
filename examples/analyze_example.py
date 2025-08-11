"""
Example script demonstrating the use of the Terraform Plan Analyzer.
"""
import json
import sys
from pathlib import Path

# Add the parent directory to the Python path to import the agent
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import analyze_terraform_plan


def main():
    """Run the example."""
    # Load the example plan with errors
    example_file = Path(__file__).parent / 'example_plan_with_errors.txt'
    with open(example_file, 'r') as f:
        plan_output = f.read()
    
    # Analyze the plan
    result_json = analyze_terraform_plan(plan_output)
    
    # Parse and pretty print the result
    result = json.loads(result_json)
    pretty_json = json.dumps(result, indent=2)
    print(pretty_json)


if __name__ == "__main__":
    main()