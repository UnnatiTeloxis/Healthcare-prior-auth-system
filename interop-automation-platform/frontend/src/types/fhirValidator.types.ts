export type IssueSeverity = "fatal" | "error" | "warning" | "information";

export interface ValidationIssue {
  severity: IssueSeverity;
  code: string;
  message: string;
  location?: string | null;
  line?: number | null;
  column?: number | null;
}

export interface ValidationRequest {
  resource: string;
  profiles?: string[];
  resource_type?: string | null;
  ig?: string | null;
  profile?: string | null;
}

export interface BatchValidationRequest {
  resources: string[];
  profiles?: string[];
  ig?: string | null;
  profile?: string | null;
}

export interface ValidationResult {
  valid: boolean;
  resource_type?: string | null;
  profiles: string[];
  issues: ValidationIssue[];
  summary: string;
  error_count: number;
  warning_count: number;
  info_count: number;
  operation_outcome?: Record<string, unknown> | null;
  selected_ig?: string | null;
  resolved_profile?: string | null;
  package_id?: string | null;
  package_version?: string | null;
}

export interface BatchValidationResult {
  results: ValidationResult[];
  total: number;
  valid_count: number;
  invalid_count: number;
}

export interface AvailableIG {
  package_id: string;
  name?: string;
  version?: string;
  title?: string;
  description?: string;
  fhir_version?: string | null;
  fhir_versions?: string[];
  filename?: string | null;
  canonical?: string;
  package_type?: string | null;
  structure_definition_count?: number;
  is_profile_ig?: boolean;
  source?: string;
  cached?: boolean;
  popular?: boolean;
  category?: string;
}

export interface IGListResponse {
  success: boolean;
  igs: AvailableIG[];
  count: number;
  total: number;
  catalog_source?: string | null;
  source_mode?: string;
}

export interface LoadedIG {
  package_id: string;
  package_name?: string;
  name?: string;
  version?: string;
  profiles: string[];
  status?: string;
  load_time_ms?: number;
  loaded_at?: number;
  preloaded?: boolean;
  error?: string | null;
}

export interface IGLoadResponse {
  success: boolean;
  ig: LoadedIG;
}

export interface IGLoadedResponse {
  success: boolean;
  igs: LoadedIG[];
  count: number;
}

export type ProfilesByIGResponse = Record<string, string[]>;

export interface ValidationHistoryEntry {
  id: string;
  timestamp: string;
  resourceType: string | null;
  valid: boolean;
  selectedIg: string | null;
  resolvedProfile: string | null;
  summary: string;
  errorCount: number;
  warningCount: number;
}
