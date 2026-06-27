import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { clearHistory, setCurrentResource, setSelectedProfiles } from '../../store/fhirValidatorSlice';
import { ValidationHistoryEntry } from '../../types/fhirValidator.types';

export default function ValidationHistory() {
  const dispatch = useDispatch<AppDispatch>();
  const validationHistory = useSelector(
    (state: RootState) => state.fhirValidator.validationHistory
  );

  const handleRerun = (entry: ValidationHistoryEntry) => {
    const resource = JSON.stringify(entry.result.operationOutcome, null, 2);
    dispatch(setCurrentResource(resource));
    dispatch(setSelectedProfiles(entry.profiles));
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all validation history?')) {
      dispatch(clearHistory());
    }
  };

  const formatTimestamp = (date: Date) => {
    const d = new Date(date);
    return d.toLocaleString();
  };

  if (validationHistory.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Validation History</h2>
        <div className="text-center py-8 text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>No validation history</p>
          <p className="text-sm mt-2">Your validation history will appear here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Validation History</h2>
        <button
          onClick={handleClearHistory}
          className="text-sm text-red-600 hover:text-red-700"
        >
          Clear History
        </button>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {validationHistory.map((entry) => (
          <div
            key={entry.id}
            className="border border-gray-200 rounded p-4 hover:bg-gray-50"
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                {entry.result.valid ? (
                  <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                )}
                <span className="font-medium text-gray-800">
                  {entry.resourceType || 'Unknown Resource'}
                </span>
              </div>
              <span className="text-xs text-gray-500">
                {formatTimestamp(entry.timestamp)}
              </span>
            </div>

            <div className="mb-2">
              <div className="flex gap-3 text-sm">
                <span className="text-red-600">
                  {entry.result.issues.filter(i => i.severity === 'error').length} errors
                </span>
                <span className="text-yellow-600">
                  {entry.result.issues.filter(i => i.severity === 'warning').length} warnings
                </span>
                <span className="text-blue-600">
                  {entry.result.issues.filter(i => i.severity === 'information').length} info
                </span>
              </div>
            </div>

            {entry.profiles.length > 0 && (
              <div className="mb-2">
                <p className="text-xs text-gray-500 mb-1">Profiles:</p>
                <div className="flex flex-wrap gap-1">
                  {entry.profiles.map((profile, index) => (
                    <span key={index} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                      {profile.split('/').pop()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end mt-3">
              <button
                onClick={() => handleRerun(entry)}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
