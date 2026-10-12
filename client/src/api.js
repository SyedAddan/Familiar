import axios from "axios";

export const apiBaseUrl = import.meta.env.VITE_SERVER_URL || "";

const api = axios.create({
  baseURL: apiBaseUrl,
  withCredentials: true,
});

let csrfToken;

api.interceptors.request.use((config) => {
  if (
    csrfToken &&
    !["get", "head", "options"].includes(config.method?.toLowerCase())
  ) {
    config.headers["X-CSRF-Token"] = csrfToken;
  }
  return config;
});

api.interceptors.response.use((response) => {
  const newToken = response.data?.csrfToken;
  if (typeof newToken === "string") {
    csrfToken = newToken;
    document
      .querySelector('meta[name="csrf-token"]')
      ?.setAttribute("content", csrfToken);
  }
  return response;
});

export async function ensureCsrfToken() {
  if (!csrfToken) {
    const response = await api.get("/csrf");
    csrfToken = response.data.csrfToken;
    document
      .querySelector('meta[name="csrf-token"]')
      ?.setAttribute("content", csrfToken);
  }
}

export default api;
