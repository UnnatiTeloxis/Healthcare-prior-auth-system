from typing import List, Dict, Any
from app.services.inferno_client import inferno_client
from app.utils.fhir_utils import detect_resource_type, parse_operation_outcome
from app.models.responses import ValidationResult, ValidationIssue, BatchValidationResult
import logging

logger = logging.getLogger(__name__)


class ValidationService:
    
    async def validate_resource(
        self,
        resource: str,
        profiles: List[str],
        resource_type: str = None
    ) -> ValidationResult:
        """
        Validate a single FHIR resource.
        """
        if not resource_type:
            resource_type = detect_resource_type(resource)
        
        try:
            operation_outcome = await inferno_client.validate_resource(resource, profiles)
            
            is_valid, issues = parse_operation_outcome(operation_outcome)
            
            # Count issues by severity
            error_count = sum(1 for i in issues if i['severity'] == 'error')
            warning_count = sum(1 for i in issues if i['severity'] == 'warning')
            info_count = sum(1 for i in issues if i['severity'] == 'information')
            
            # Generate summary
            if is_valid:
                if warning_count > 0 or info_count > 0:
                    summary = f"✅ Validation successful with {warning_count} warning(s) and {info_count} info message(s)"
                else:
                    summary = "✅ Validation successful - No issues found"
            else:
                summary_parts = [f"❌ Validation failed with {error_count} error(s)"]
                
                # Extract missing/invalid fields from error messages
                missing_fields = []
                invalid_fields = []
                
                for issue in issues:
                    if issue['severity'] == 'error':
                        msg = issue['message'].lower()
                        # Check for missing required fields
                        if 'minimum required' in msg or 'required element' in msg:
                            if issue['location']:
                                missing_fields.append(issue['location'])
                        # Check for invalid values
                        elif 'invalid' in msg or 'not valid' in msg:
                            if issue['location']:
                                invalid_fields.append(issue['location'])
                
                if missing_fields:
                    summary_parts.append(f"Missing required: {', '.join(set(missing_fields[:3]))}")
                if invalid_fields:
                    summary_parts.append(f"Invalid values in: {', '.join(set(invalid_fields[:3]))}")
                
                summary = " | ".join(summary_parts)
            
            return ValidationResult(
                valid=is_valid,
                resource_type=resource_type,
                profiles=profiles,
                issues=[ValidationIssue(**issue) for issue in issues],
                summary=summary,
                error_count=error_count,
                warning_count=warning_count,
                info_count=info_count,
                operation_outcome=operation_outcome
            )
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return ValidationResult(
                valid=False,
                resource_type=resource_type,
                profiles=profiles,
                issues=[
                    ValidationIssue(
                        severity="error",
                        code="exception",
                        message=f"Validation service error: {str(e)}"
                    )
                ],
                summary=f"❌ Validation failed: {str(e)}",
                error_count=1,
                warning_count=0,
                info_count=0
            )
    
    async def validate_batch(
        self,
        resources: List[str],
        profiles: List[str]
    ) -> BatchValidationResult:
        """
        Validate multiple FHIR resources.
        """
        results = []
        
        for resource in resources:
            result = await self.validate_resource(resource, profiles)
            results.append(result)
        
        valid_count = sum(1 for r in results if r.valid)
        invalid_count = len(results) - valid_count
        
        return BatchValidationResult(
            results=results,
            total=len(results),
            valid_count=valid_count,
            invalid_count=invalid_count
        )


validation_service = ValidationService()
