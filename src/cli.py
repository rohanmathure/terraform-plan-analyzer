"""
Command-line interface for the Terraform plan analyzer.
"""
import argparse
import sys
import json
from typing import Optional

from src.agent import analyze_terraform_plan, parse_json_response


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze Terraform plan output and provide recommendations"
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to file containing Terraform plan output (if not provided, reads from stdin)",
        type=str
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to output JSON file (if not provided, prints to stdout)",
        type=str
    )
    parser.add_argument(
        "--pretty",
        help="Pretty print the JSON output",
        action="store_true"
    )
    args = parser.parse_args()
    
    # Read plan output from file or stdin
    if args.file:
        try:
            with open(args.file, 'r') as f:
                plan_output = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        plan_output = sys.stdin.read()
    
    # Analyze the plan
    result = analyze_terraform_plan(plan_output)
    
    # Pretty print if requested
    if args.pretty:
        try:
            parsed = json.loads(result)
            result = json.dumps(parsed, indent=2)
        except:
            # If parsing fails, use the original result
            pass
    
    # Output to file or stdout
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(result)
        except Exception as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Print to stdout
        print(result)


if __name__ == "__main__":
    main()