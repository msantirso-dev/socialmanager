import { clearAuth, getAccessToken, getRefreshToken, saveTokens, type AuthTokens, type LoginResponse, type User } from "./auth";

// Vacío = rutas relativas /api/... (proxy Next.js en dev). Producción: NEXT_PUBLIC_API_URL completa.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message);
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return data.detail || data.message || res.statusText;
  } catch {
    return res.statusText;
  }
}

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  const res = await fetch(`${API_URL}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!res.ok) return false;

  const tokens: AuthTokens = await res.json();
  saveTokens(tokens);
  return true;
}

export async function apiFetch<T>(path: string, options?: RequestInit, retry = true): Promise<T> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (res.status === 401 && retry && (await refreshAccessToken())) {
    return apiFetch<T>(path, options, false);
  }

  if (!res.ok) {
    throw new ApiError(await parseError(res), res.status);
  }

  return res.json();
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  return apiFetch<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function register(data: {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
}): Promise<LoginResponse> {
  return apiFetch<LoginResponse>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function fetchMe(): Promise<User> {
  return apiFetch<User>("/api/v1/auth/me");
}

export async function logoutApi(): Promise<void> {
  try {
    await apiFetch("/api/v1/auth/logout", { method: "POST" });
  } catch {
    // ignore — clear local state anyway
  }
  clearAuth();
}

export { API_URL };
