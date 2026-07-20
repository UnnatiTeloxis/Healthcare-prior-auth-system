import apiClient from "./client";
import type {
  BatchValidationRequest,
  BatchValidationResult,
  IGListResponse,
  IGLoadResponse,
  IGLoadedResponse,
  ProfilesByIGResponse,
  ValidationRequest,
  ValidationResult,
} from "../../types/fhirValidator.types";

const LONG_TIMEOUT_MS = 600_000;

export async function validateResource(request: ValidationRequest): Promise<ValidationResult> {
  const { data } = await apiClient.post<ValidationResult>("/fhir/validate", request, {
    timeout: LONG_TIMEOUT_MS,
  });
  return data;
}

export async function validateBatch(request: BatchValidationRequest): Promise<BatchValidationResult> {
  const { data } = await apiClient.post<BatchValidationResult>("/fhir/batch", request, {
    timeout: LONG_TIMEOUT_MS,
  });
  return data;
}

export async function listAvailableIGs(options?: {
  q?: string;
  source?: "local" | "inferno" | "all";
  limit?: number;
  refresh?: boolean;
}): Promise<IGListResponse> {
  const { data } = await apiClient.get<IGListResponse>("/igs/available", {
    params: {
      q: options?.q,
      source: options?.source ?? "all",
      limit: options?.limit ?? 500,
      refresh: options?.refresh ?? false,
    },
    timeout: 60_000,
  });
  return data;
}

export async function loadIG(
  packageId: string,
  version?: string | null,
  retry = false
): Promise<IGLoadResponse> {
  const { data } = await apiClient.post<IGLoadResponse>(
    "/igs/load",
    {
      package_id: packageId,
      package_name: packageId,
      version: version || null,
      retry,
    },
    { timeout: retry ? LONG_TIMEOUT_MS : 30_000 }
  );
  return data;
}

export async function listLoadedIGs(): Promise<IGLoadedResponse> {
  const { data } = await apiClient.get<IGLoadedResponse>("/igs/loaded");
  return data;
}

export async function getProfiles(): Promise<string[]> {
  const { data } = await apiClient.get<string[]>("/fhir/profiles");
  return data;
}

export async function getProfilesByIG(): Promise<ProfilesByIGResponse> {
  const { data } = await apiClient.get<ProfilesByIGResponse>("/fhir/profiles/by-ig");
  return data;
}

export async function getValidatorHealth(): Promise<Record<string, unknown>> {
  const { data } = await apiClient.get<Record<string, unknown>>("/fhir/health");
  return data;
}

export function igKey(packageId: string, version?: string | null): string {
  return version ? `${packageId}#${version}` : packageId;
}
