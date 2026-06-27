import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { fhirValidatorAPI } from '../services/api/fhirValidator';
import {
  ValidationResult,
  ValidationRequest,
  ProfilesByIG,
  IGInfo,
  ValidationHistoryEntry,
} from '../types/fhirValidator.types';

interface FHIRValidatorState {
  currentResource: string;
  selectedProfiles: string[];
  validationResult: ValidationResult | null;
  isValidating: boolean;
  error: string | null;
  
  profiles: string[];
  profilesByIG: ProfilesByIG;
  loadedIGs: Record<string, IGInfo>;
  isLoadingProfiles: boolean;
  isLoadingIGs: boolean;
  
  validationHistory: ValidationHistoryEntry[];
}

const initialState: FHIRValidatorState = {
  currentResource: '',
  selectedProfiles: [],
  validationResult: null,
  isValidating: false,
  error: null,
  
  profiles: [],
  profilesByIG: {},
  loadedIGs: {},
  isLoadingProfiles: false,
  isLoadingIGs: false,
  
  validationHistory: [],
};

export const validateResource = createAsyncThunk(
  'fhirValidator/validateResource',
  async (request: ValidationRequest) => {
    return await fhirValidatorAPI.validateResource(request);
  }
);

export const fetchProfiles = createAsyncThunk(
  'fhirValidator/fetchProfiles',
  async () => {
    return await fhirValidatorAPI.getProfiles();
  }
);

export const fetchProfilesByIG = createAsyncThunk(
  'fhirValidator/fetchProfilesByIG',
  async () => {
    return await fhirValidatorAPI.getProfilesByIG();
  }
);

export const fetchLoadedIGs = createAsyncThunk(
  'fhirValidator/fetchLoadedIGs',
  async () => {
    return await fhirValidatorAPI.listIGs();
  }
);

export const loadIG = createAsyncThunk(
  'fhirValidator/loadIG',
  async ({ packageId, version }: { packageId: string; version?: string }) => {
    return await fhirValidatorAPI.loadIG(packageId, version);
  }
);

const fhirValidatorSlice = createSlice({
  name: 'fhirValidator',
  initialState,
  reducers: {
    setCurrentResource: (state, action: PayloadAction<string>) => {
      state.currentResource = action.payload;
    },
    setSelectedProfiles: (state, action: PayloadAction<string[]>) => {
      state.selectedProfiles = action.payload;
    },
    addProfile: (state, action: PayloadAction<string>) => {
      if (!state.selectedProfiles.includes(action.payload)) {
        state.selectedProfiles.push(action.payload);
      }
    },
    removeProfile: (state, action: PayloadAction<string>) => {
      state.selectedProfiles = state.selectedProfiles.filter(
        (p) => p !== action.payload
      );
    },
    clearValidationResult: (state) => {
      state.validationResult = null;
      state.error = null;
    },
    addToHistory: (state, action: PayloadAction<ValidationHistoryEntry>) => {
      state.validationHistory.unshift(action.payload);
      if (state.validationHistory.length > 50) {
        state.validationHistory = state.validationHistory.slice(0, 50);
      }
    },
    clearHistory: (state) => {
      state.validationHistory = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(validateResource.pending, (state) => {
        state.isValidating = true;
        state.error = null;
      })
      .addCase(validateResource.fulfilled, (state, action) => {
        state.isValidating = false;
        state.validationResult = action.payload;
        
        const historyEntry: ValidationHistoryEntry = {
          id: Date.now().toString(),
          timestamp: new Date(),
          resourceType: action.payload.resourceType,
          profiles: action.payload.profiles,
          result: action.payload,
        };
        state.validationHistory.unshift(historyEntry);
        if (state.validationHistory.length > 50) {
          state.validationHistory = state.validationHistory.slice(0, 50);
        }
      })
      .addCase(validateResource.rejected, (state, action) => {
        state.isValidating = false;
        state.error = action.error.message || 'Validation failed';
      })
      
      .addCase(fetchProfiles.pending, (state) => {
        state.isLoadingProfiles = true;
      })
      .addCase(fetchProfiles.fulfilled, (state, action) => {
        state.isLoadingProfiles = false;
        state.profiles = action.payload;
      })
      .addCase(fetchProfiles.rejected, (state) => {
        state.isLoadingProfiles = false;
      })
      
      .addCase(fetchProfilesByIG.pending, (state) => {
        state.isLoadingProfiles = true;
      })
      .addCase(fetchProfilesByIG.fulfilled, (state, action) => {
        state.isLoadingProfiles = false;
        state.profilesByIG = action.payload;
      })
      .addCase(fetchProfilesByIG.rejected, (state) => {
        state.isLoadingProfiles = false;
      })
      
      .addCase(fetchLoadedIGs.pending, (state) => {
        state.isLoadingIGs = true;
      })
      .addCase(fetchLoadedIGs.fulfilled, (state, action) => {
        state.isLoadingIGs = false;
        state.loadedIGs = action.payload;
      })
      .addCase(fetchLoadedIGs.rejected, (state) => {
        state.isLoadingIGs = false;
      })
      
      .addCase(loadIG.fulfilled, (state, action) => {
        state.loadedIGs[action.payload.id] = action.payload;
      });
  },
});

export const {
  setCurrentResource,
  setSelectedProfiles,
  addProfile,
  removeProfile,
  clearValidationResult,
  addToHistory,
  clearHistory,
} = fhirValidatorSlice.actions;

export default fhirValidatorSlice.reducer;
