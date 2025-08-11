# Terraform Plan Analyzer

A tool that analyzes Terraform plan outputs and provides helpful recommendations for fixing errors. It generates a structured JSON output with human-friendly error explanations and actionable solutions.

## Features

- Parses Terraform plan output to identify errors
- Categorizes errors by type (validation, dependency, permission, etc.)
- Generates targeted recommendations with confidence levels
- Provides sample code snippets for fixing issues
- Returns a consolidated JSON response for easy integration

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/terraform-plan-analyzer.git
cd terraform-plan-analyzer

# Install the package
pip install -e .
```

## Usage

### Command Line Interface

You can use the analyzer directly from the command line:

```bash
# Using a file as input
terraform plan -no-color > tf_plan.txt
python -m src.cli --file tf_plan.txt --pretty

# Or pipe the output directly
terraform plan -no-color | python -m src.cli --pretty
```

### Python API

You can also use the analyzer in your Python code:

```python
from terraform_plan_analyzer.agent import analyze_terraform_plan

# Get Terraform plan output
plan_output = subprocess.run(
    ["terraform", "plan", "-no-color"], 
    capture_output=True,
    text=True
).stdout

# Analyze the plan
result_json = analyze_terraform_plan(plan_output)

# Parse the JSON result
import json
result = json.loads(result_json)

# Access the recommendations
for error in result["errors"]:
    print(f"Error: {error['message']}")
    for rec in error["recommendations"]:
        print(f"  - {rec['description']}")
```

## Example Response

```json
{
  "status": "error",
  "summary": "Found 3 issues in your Terraform plan. Most are related to dependency problems. Check the recommendations for solutions.",
  "errors": [
    {
      "errorType": "dependency",
      "message": "There's a dependency issue: A managed resource \"aws_vpc\" \"main\" has not been declared in the root module.",
      "affectedResources": [
        {
          "name": "example",
          "type": "aws_security_group",
          "address": "aws_security_group.example"
        }
      ],
      "recommendations": [
        {
          "description": "Define the missing resource 'aws_vpc.main' or correct the reference if it's misspelled",
          "confidence": "high"
        },
        {
          "description": "Ensure that the resource 'aws_vpc.main' is in the correct module scope",
          "confidence": "medium"
        }
      ]
    },
    {
      "errorType": "syntax",
      "message": "There's a syntax error in your configuration: The provider hashicorp/aws does not support resource type \"aws_security_gruop\". Did you mean \"aws_security_group\"?",
      "affectedResources": [
        {
          "name": "another_example",
          "type": "aws_security_gruop",
          "address": "aws_security_gruop.another_example"
        }
      ],
      "recommendations": [
        {
          "description": "Fix the typo in the resource type from 'aws_security_gruop' to 'aws_security_group'",
          "confidence": "high"
        },
        {
          "description": "Run 'terraform fmt' to automatically fix minor syntax issues",
          "code": "terraform fmt",
          "confidence": "high"
        }
      ]
    }
  ],
  "metadata": {
    "timestamp": "2023-09-14T15:30:45.123456",
    "resourceCount": {
      "add": 2,
      "change": 0,
      "destroy": 0
    }
  }
}
```

## License

MIT