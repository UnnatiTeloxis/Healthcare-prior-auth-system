import axios from "axios";

// Relative URL — same origin in production (FastAPI serves UI + API on one host)
const baseURL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const apiClient = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail;
    let message: string;
    if (typeof detail === "string") {
      message = detail;
    } else if (detail && typeof detail === "object") {
      const obj = detail as { message?: string; candidates?: string[]; msg?: string };
      if (obj.message || obj.msg) {
        message = obj.message || obj.msg || "";
        if (Array.isArray(obj.candidates) && obj.candidates.length) {
          message += ` Candidates: ${obj.candidates.slice(0, 5).join(", ")}`;
        }
      } else {
        message = JSON.stringify(detail);
      }
    } else {
      message =
        error.message ||
        `Request failed: ${error.response?.status ?? "network error"}`;
    }
    return Promise.reject(new Error(message));
  }
);

export default apiClient;
