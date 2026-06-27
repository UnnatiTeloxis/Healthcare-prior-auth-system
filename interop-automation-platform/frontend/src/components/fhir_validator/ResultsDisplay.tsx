import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { ValidationIssue, IssueSeverity } from '../../types/fhirValidator.types';

const getSeverityIcon = (severity: IssueSeverity) => {
  switch (severity) {
    case 'error':
      return (
        <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      );
    case 'warning':
      return (
        <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      );
    case 'information':
      return (
        <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
        </svg>
      );
  }
};

const getSeverityBadgeColor = (severity: IssueSeverity) => {
  switch (severity) {
    case 'error':
      return 'bg-red-100 text-red-800';
    case 'warning':
      return 'bg-yellow-100 text-yellow-800';
    case 'information':
      return 'bg-blue-100 text-blue-800';
  }
};

export default function ResultsDisplay() {
  const { validationResult, isValidating } = useSelector(
    (state: RootState) => state.fhirValidator
  );

  if (isValidating) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Validation Results</h2>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Validating resource...</span>
        </div>
      </div>
    );
  }

  if (!validationResult) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Validation Results</h2>
        <div className="text-center py-12 text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>No validation results yet</p>
          <p className="text-sm mt-2">Enter a FHIR resource and click Validate to see results</p>
        </div>
      </div>
    );
  }

  const errorCount = validationResult.issues.filter(i => i.severity === 'error').length;
  const warningCount = validationResult.issues.filter(i => i.severity === 'warning').length;
  const infoCount = validationResult.issues.filter(i => i.severity === 'information').length;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Validation Results</h2>
      
      <div className="mb-6">
        {validationResult.valid ? (
          <div className="flex items-center gap-3 p-4 bg-green-50 border-l-4 border-green-500 rounded">
            <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="font-semibold text-green-800">Valid Resource</p>
              <p className="text-sm text-green-700">
                The FHIR resource passed all validation checks
              </p>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-3 p-4 bg-red-50 border-l-4 border-red-500 rounded">
            <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="font-semibold text-red-800">Invalid Resource</p>
              <p className="text-sm text-red-700">
                The FHIR resource has validation errors
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-red-50 p-4 rounded">
          <p className="text-sm text-red-600 font-medium">Errors</p>
          <p className="text-2xl font-bold text-red-800">{errorCount}</p>
        </div>
        <div className="bg-yellow-50 p-4 rounded">
          <p className="text-sm text-yellow-600 font-medium">Warnings</p>
          <p className="text-2xl font-bold text-yellow-800">{warningCount}</p>
        </div>
        <div className="bg-blue-50 p-4 rounded">
          <p className="text-sm text-blue-600 font-medium">Information</p>
          <p className="text-2xl font-bold text-blue-800">{infoCount}</p>
        </div>
      </div>

      {validationResult.resourceType && (
        <div className="mb-4 text-sm text-gray-600">
          <span className="font-medium">Resource Type:</span> {validationResult.resourceType}
        </div>
      )}

      {validationResult.profiles.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Validated Against:</p>
          <div className="flex flex-wrap gap-2">
            {validationResult.profiles.map((profile, index) => (
              <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                {profile.split('/').pop()}
              </span>
            ))}
          </div>
        </div>
      )}

      {validationResult.issues.length > 0 ? (
        <div>
          <h3 className="font-semibold text-gray-800 mb-3">Issues ({validationResult.issues.length})</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {validationResult.issues.map((issue, index) => (
              <div
                key={index}
                className="flex gap-3 p-3 border border-gray-200 rounded hover:bg-gray-50"
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getSeverityIcon(issue.severity)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-0.5 text-xs font-medium rounded ${getSeverityBadgeColor(issue.severity)}`}>
                      {issue.severity}
                    </span>
                    <span className="text-xs text-gray-500">{issue.code}</span>
                    {issue.line && (
                      <span className="text-xs text-gray-500">
                        Line {issue.line}{issue.column && `, Col ${issue.column}`}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700 break-words">{issue.message}</p>
                  {issue.location && (
                    <p className="text-xs text-gray-500 mt-1">
                      Location: {issue.location}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <p>No issues found</p>
        </div>
      )}
    </div>
  );
}
