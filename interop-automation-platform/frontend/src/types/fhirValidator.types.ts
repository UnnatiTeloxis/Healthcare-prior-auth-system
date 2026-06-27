export type IssueSeverity = 'error' | 'warning' | 'information';

export interface ValidationIssue {
  severity: IssueSeverity;
  code: string;
  message: string;
  location?: string;
  line?: number;
  column?: number;
}

export interface ValidationRequest {
  resource: string;
  profiles: string[];
  resourceType?: string;
}

export interface ValidationResult {
  valid: boolean;
  resourceType?: string;
  profiles: string[];
  issues: ValidationIssue[];
  operationOutcome?: any;
}

export interface BatchValidationRequest {
  resources: string[];
  profiles: string[];
}

export interface BatchValidationResult {
  results: ValidationResult[];
  total: number;
  validCount: number;
  invalidCount: number;
}

export interface ProfileInfo {
  url: string;
  name?: string;
  ig?: string;
}

export interface IGInfo {
  id: string;
  version: string;
  profiles: string[];
  canonicalUrl?: string;
}

export interface ProfilesByIG {
  [igId: string]: string[];
}

export interface ValidationHistoryEntry {
  id: string;
  timestamp: Date;
  resourceType?: string;
  profiles: string[];
  result: ValidationResult;
}
