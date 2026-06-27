import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { validateResource } from '../../store/fhirValidatorSlice';
import InputPanel from './InputPanel';
import ProfileSelector from './ProfileSelector';
import ResultsDisplay from './ResultsDisplay';
import ValidationHistory from './ValidationHistory';

export default function ValidatorDashboard() {
  const dispatch = useDispatch<AppDispatch>();
  const { currentResource, selectedProfiles, isValidating, error } = useSelector(
    (state: RootState) => state.fhirValidator
  );

  const handleValidate = () => {
    if (!currentResource.trim()) {
      alert('Please enter a FHIR resource to validate');
      return;
    }

    dispatch(validateResource({
      resource: currentResource,
      profiles: selectedProfiles,
    }));
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">FHIR Resource Validator</h1>
          <p className="text-gray-600">
            Validate FHIR resources against Implementation Guide profiles using the Inferno validator
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-semibold text-red-800">Validation Error</p>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <InputPanel />
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">Validation Controls</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {selectedProfiles.length > 0 
                      ? `Validating against ${selectedProfiles.length} profile(s)`
                      : 'Select profiles or validate against base FHIR specification'}
                  </p>
                </div>
                <button
                  onClick={handleValidate}
                  disabled={isValidating || !currentResource.trim()}
                  className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  {isValidating ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Validating...
                    </span>
                  ) : (
                    'Validate Resource'
                  )}
                </button>
              </div>
            </div>

            <ResultsDisplay />
          </div>

          <div className="space-y-6">
            <ProfileSelector />
            <ValidationHistory />
          </div>
        </div>
      </div>
    </div>
  );
}
