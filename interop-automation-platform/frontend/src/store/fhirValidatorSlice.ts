import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";
import * as fhirApi from "../services/api/fhirValidator";
import type {
  AvailableIG,
  ValidationHistoryEntry,
  ValidationRequest,
  ValidationResult,
} from "../types/fhirValidator.types";

export interface FhirValidatorState {
  availableIGs: AvailableIG[];
  selectedIG: AvailableIG | null;
  selectedProfile: string;
  profilesForIG: string[];
  resourceText: string;
  validationResult: ValidationResult | null;
  validationHistory: ValidationHistoryEntry[];
  igsLoading: boolean;
  igLoading: boolean;
  validating: boolean;
  error: string | null;
  igLoadStatus: string | null;
}

const initialState: FhirValidatorState = {
  availableIGs: [],
  selectedIG: null,
  selectedProfile: "",
  profilesForIG: [],
  resourceText: "",
  validationResult: null,
  validationHistory: [],
  igsLoading: false,
  igLoading: false,
  validating: false,
  error: null,
  igLoadStatus: null,
};

function formatError(err: unknown): string {
  if (err instanceof Error) return err.message;
  return String(err);
}

export const fetchAvailableIGs = createAsyncThunk(
  "fhirValidator/fetchAvailableIGs",
  async (query: string | undefined, { rejectWithValue }) => {
    try {
      const response = await fhirApi.listAvailableIGs({ q: query, source: "all", limit: 500 });
      return response.igs;
    } catch (err) {
      return rejectWithValue(formatError(err));
    }
  }
);

export const loadSelectedIG = createAsyncThunk(
  "fhirValidator/loadSelectedIG",
  async (
    payload: { packageId: string; version?: string | null },
    { rejectWithValue }
  ) => {
    try {
      const response = await fhirApi.loadIG(payload.packageId, payload.version, false);
      let profiles = response.ig.profiles || [];

      // Poll while Inferno loads in the background (preloaded IGs return ready immediately).
      let status = response.ig.status || "ready";
      let attempts = 0;
      let latest = response.ig;
      while (status === "loading" && attempts < 450) {
        await new Promise((r) => setTimeout(r, 2000));
        const poll = await fhirApi.loadIG(payload.packageId, payload.version, false);
        latest = poll.ig;
        status = poll.ig.status || "ready";
        profiles = poll.ig.profiles || profiles;
        attempts += 1;
        if (status !== "loading") break;
      }

      // Inferno-parity: fill profiles from GET /profiles-by-ig when load returned none
      if (status === "ready" && !profiles.length) {
        const byIg = await fhirApi.getProfilesByIG();
        const key = fhirApi.igKey(payload.packageId, payload.version);
        profiles =
          byIg[key] ||
          byIg[payload.packageId] ||
          Object.entries(byIg).find(([k]) => k.startsWith(`${payload.packageId}#`))?.[1] ||
          [];
      }

      return { ig: latest, profiles, status };
    } catch (err) {
      return rejectWithValue(formatError(err));
    }
  }
);

export const validateFhirResource = createAsyncThunk(
  "fhirValidator/validateFhirResource",
  async (request: ValidationRequest, { rejectWithValue }) => {
    try {
      return await fhirApi.validateResource(request);
    } catch (err) {
      return rejectWithValue(formatError(err));
    }
  }
);

const fhirValidatorSlice = createSlice({
  name: "fhirValidator",
  initialState,
  reducers: {
    setSelectedIG(state, action: PayloadAction<AvailableIG | null>) {
      state.selectedIG = action.payload;
      state.selectedProfile = "";
      state.profilesForIG = [];
      state.igLoadStatus = null;
      state.error = null;
    },
    setSelectedProfile(state, action: PayloadAction<string>) {
      state.selectedProfile = action.payload;
    },
    setResourceText(state, action: PayloadAction<string>) {
      state.resourceText = action.payload;
    },
    clearValidationResult(state) {
      state.validationResult = null;
      state.error = null;
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAvailableIGs.pending, (state) => {
        state.igsLoading = true;
        state.error = null;
      })
      .addCase(fetchAvailableIGs.fulfilled, (state, action) => {
        state.igsLoading = false;
        state.availableIGs = action.payload;
      })
      .addCase(fetchAvailableIGs.rejected, (state, action) => {
        state.igsLoading = false;
        state.error = (action.payload as string) || "Failed to load IG catalog";
      })
      .addCase(loadSelectedIG.pending, (state) => {
        state.igLoading = true;
        state.igLoadStatus = "loading";
        state.error = null;
      })
      .addCase(loadSelectedIG.fulfilled, (state, action) => {
        state.igLoading = false;
        state.igLoadStatus = action.payload.status || "ready";
        state.profilesForIG = action.payload.profiles;
      })
      .addCase(loadSelectedIG.rejected, (state, action) => {
        state.igLoading = false;
        state.igLoadStatus = "failed";
        state.error = (action.payload as string) || "Failed to load Implementation Guide";
      })
      .addCase(validateFhirResource.pending, (state) => {
        state.validating = true;
        state.error = null;
      })
      .addCase(validateFhirResource.fulfilled, (state, action) => {
        state.validating = false;
        state.validationResult = action.payload;
        const entry: ValidationHistoryEntry = {
          id: `VAL-${Date.now()}`,
          timestamp: new Date().toISOString(),
          resourceType: action.payload.resource_type ?? null,
          valid: action.payload.valid,
          selectedIg: action.payload.selected_ig ?? null,
          resolvedProfile: action.payload.resolved_profile ?? null,
          summary: action.payload.summary,
          errorCount: action.payload.error_count,
          warningCount: action.payload.warning_count,
        };
        state.validationHistory = [entry, ...state.validationHistory].slice(0, 25);
      })
      .addCase(validateFhirResource.rejected, (state, action) => {
        state.validating = false;
        state.error = (action.payload as string) || "Validation failed";
      });
  },
});

export const {
  setSelectedIG,
  setSelectedProfile,
  setResourceText,
  clearValidationResult,
  clearError,
} = fhirValidatorSlice.actions;

export default fhirValidatorSlice.reducer;
