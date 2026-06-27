import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import {
  fetchProfilesByIG,
  fetchLoadedIGs,
  addProfile,
  removeProfile,
  setSelectedProfiles,
} from '../../store/fhirValidatorSlice';

export default function ProfileSelector() {
  const dispatch = useDispatch<AppDispatch>();
  const { profilesByIG, selectedProfiles, isLoadingProfiles } = useSelector(
    (state: RootState) => state.fhirValidator
  );
  
  const [selectedIG, setSelectedIG] = useState<string>('');
  const [expandedIGs, setExpandedIGs] = useState<Set<string>>(new Set());

  useEffect(() => {
    dispatch(fetchProfilesByIG());
    dispatch(fetchLoadedIGs());
  }, [dispatch]);

  const handleToggleProfile = (profileUrl: string) => {
    if (selectedProfiles.includes(profileUrl)) {
      dispatch(removeProfile(profileUrl));
    } else {
      dispatch(addProfile(profileUrl));
    }
  };

  const handleSelectAllFromIG = (igId: string) => {
    const profiles = profilesByIG[igId] || [];
    const allSelected = profiles.every(p => selectedProfiles.includes(p));
    
    if (allSelected) {
      profiles.forEach(p => dispatch(removeProfile(p)));
    } else {
      profiles.forEach(p => {
        if (!selectedProfiles.includes(p)) {
          dispatch(addProfile(p));
        }
      });
    }
  };

  const handleClearAll = () => {
    dispatch(setSelectedProfiles([]));
  };

  const toggleIGExpanded = (igId: string) => {
    const newExpanded = new Set(expandedIGs);
    if (newExpanded.has(igId)) {
      newExpanded.delete(igId);
    } else {
      newExpanded.add(igId);
    }
    setExpandedIGs(newExpanded);
  };

  if (isLoadingProfiles) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Profile Selection</h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading profiles...</span>
        </div>
      </div>
    );
  }

  const igIds = Object.keys(profilesByIG);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Profile Selection</h2>
        {selectedProfiles.length > 0 && (
          <button
            onClick={handleClearAll}
            className="text-sm text-red-600 hover:text-red-700"
          >
            Clear All ({selectedProfiles.length})
          </button>
        )}
      </div>

      {selectedProfiles.length > 0 && (
        <div className="mb-4 p-3 bg-blue-50 rounded">
          <p className="text-sm font-medium text-blue-900 mb-2">
            Selected Profiles ({selectedProfiles.length}):
          </p>
          <div className="flex flex-wrap gap-2">
            {selectedProfiles.map((profile) => (
              <span
                key={profile}
                className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
              >
                {profile.split('/').pop()}
                <button
                  onClick={() => handleToggleProfile(profile)}
                  className="hover:text-blue-900"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {igIds.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No Implementation Guides loaded.</p>
          <p className="text-sm mt-2">Default IGs will be loaded when the service starts.</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {igIds.map((igId) => {
            const profiles = profilesByIG[igId] || [];
            const isExpanded = expandedIGs.has(igId);
            const selectedCount = profiles.filter(p => selectedProfiles.includes(p)).length;
            
            return (
              <div key={igId} className="border border-gray-200 rounded">
                <div className="flex items-center justify-between p-3 bg-gray-50">
                  <button
                    onClick={() => toggleIGExpanded(igId)}
                    className="flex items-center gap-2 flex-1 text-left"
                  >
                    <svg
                      className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                    <span className="font-medium text-gray-700">{igId}</span>
                    <span className="text-sm text-gray-500">
                      ({profiles.length} profiles)
                    </span>
                    {selectedCount > 0 && (
                      <span className="text-sm text-blue-600 font-medium">
                        {selectedCount} selected
                      </span>
                    )}
                  </button>
                  <button
                    onClick={() => handleSelectAllFromIG(igId)}
                    className="text-sm text-blue-600 hover:text-blue-700 px-2"
                  >
                    {selectedCount === profiles.length ? 'Deselect All' : 'Select All'}
                  </button>
                </div>
                
                {isExpanded && (
                  <div className="p-3 space-y-2">
                    {profiles.map((profile) => (
                      <label
                        key={profile}
                        className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={selectedProfiles.includes(profile)}
                          onChange={() => handleToggleProfile(profile)}
                          className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700 break-all">{profile}</span>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
