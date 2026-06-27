import json
import re
from typing import Optional, Tuple


def detect_resource_type(resource_str: str) -> Optional[str]:
    """
    Detect FHIR resource type from JSON or XML string.
    """
    resource_str = resource_str.strip()
    
    if resource_str.startswith('{'):
        try:
            resource = json.loads(resource_str)
            return resource.get('resourceType')
        except json.JSONDecodeError:
            return None
    
    elif resource_str.startswith('<'):
        match = re.search(r'<(\w+)\s+xmlns', resource_str)
        if match:
            return match.group(1)
        
        match = re.search(r'<(\w+)[\s>]', resource_str)
        if match:
            return match.group(1)
    
    return None


def is_valid_json(resource_str: str) -> bool:
    """
    Check if string is valid JSON.
    """
    try:
        json.loads(resource_str)
        return True
    except json.JSONDecodeError:
        return False


def is_valid_xml(resource_str: str) -> bool:
    """
    Check if string is valid XML (basic check).
    """
    return resource_str.strip().startswith('<')


def parse_operation_outcome(operation_outcome: dict) -> Tuple[bool, list]:
    """
    Parse FHIR OperationOutcome and extract validation issues.
    Returns (is_valid, issues_list).
    """
    issues = []
    has_errors = False
    
    if not operation_outcome or 'issue' not in operation_outcome:
        return True, []
    
    for issue in operation_outcome.get('issue', []):
        severity = issue.get('severity', 'information')
        code = issue.get('code', 'unknown')
        
        # Get message from details.text first, then diagnostics, then empty
        message = ''
        if 'details' in issue and 'text' in issue['details']:
            message = issue['details']['text']
        elif 'diagnostics' in issue:
            message = issue['diagnostics']
        
        # Get location from expression or location field
        location = None
        if 'expression' in issue and issue['expression']:
            location = issue['expression'][0] if isinstance(issue['expression'], list) else issue['expression']
        elif 'location' in issue and issue['location']:
            location = issue['location'][0] if isinstance(issue['location'], list) else issue['location']
        
        # Extract line and column from extensions
        line = None
        column = None
        if 'extension' in issue:
            for ext in issue['extension']:
                if ext.get('url', '').endswith('operationoutcome-issue-line'):
                    line = ext.get('valueInteger')
                elif ext.get('url', '').endswith('operationoutcome-issue-col'):
                    column = ext.get('valueInteger')
        
        issues.append({
            'severity': severity,
            'code': code,
            'message': message,
            'location': location,
            'line': line,
            'column': column
        })
        
        if severity == 'error' or severity == 'fatal':
            has_errors = True
    
    return not has_errors, issues
