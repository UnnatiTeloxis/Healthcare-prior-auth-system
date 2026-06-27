import { apiClient } from './client';
import {
  ValidationRequest,
  ValidationResult,
  BatchValidationRequest,
  BatchValidationResult,
  ProfilesByIG,
  IGInfo,
} from '../../types/fhirValidator.types';

class FHIRValidatorAPI {
  async validateResource(request: ValidationRequest): Promise<ValidationResult> {
    return apiClient.post<ValidationResult>('/api/v1/validate/', request);
  }

  async validateBatch(request: BatchValidationRequest): Promise<BatchValidationResult> {
    return apiClient.post<BatchValidationResult>('/api/v1/validate/batch', request);
  }

  async getProfiles(): Promise<string[]> {
    return apiClient.get<string[]>('/api/v1/validate/profiles');
  }

  async getProfilesByIG(): Promise<ProfilesByIG> {
    return apiClient.get<ProfilesByIG>('/api/v1/validate/profiles/by-ig');
  }

  async listIGs(): Promise<Record<string, any>> {
    return apiClient.get<Record<string, any>>('/api/v1/igs/');
  }

  async loadIG(packageId: string, version?: string): Promise<IGInfo> {
    const endpoint = version
      ? `/api/v1/igs/${packageId}?version=${version}`
      : `/api/v1/igs/${packageId}`;
    return apiClient.put<IGInfo>(endpoint);
  }

  async uploadIG(file: File): Promise<IGInfo> {
    return apiClient.uploadFile<IGInfo>('/api/v1/igs/upload', file);
  }

  async getVersion(): Promise<Record<string, string>> {
    return apiClient.get<Record<string, string>>('/api/v1/igs/version');
  }
}

export const fhirValidatorAPI = new FHIRValidatorAPI();
