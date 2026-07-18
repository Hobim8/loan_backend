/**
 * Thin API client for the loan risk backend.
 * Same origin when served by FastAPI; override with window.__API_BASE__ if needed.
 */
const API_BASE = (window.__API_BASE__ || "").replace(/\/$/, "");

const TOKEN_KEY = "apex_access_token";
const USER_KEY = "apex_login_id";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setSession(token, loginId) {
  localStorage.setItem(TOKEN_KEY, token);
  if (loginId) localStorage.setItem(USER_KEY, loginId);
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getLoginId() {
  return localStorage.getItem(USER_KEY) || "";
}

export function isLoggedIn() {
  return Boolean(getToken());
}

async function parseError(res) {
  let detail = `Request failed (${res.status})`;
  try {
    const data = await res.json();
    if (typeof data.detail === "string") detail = data.detail;
    else if (Array.isArray(data.detail))
      detail = data.detail.map((d) => d.msg || JSON.stringify(d)).join("; ");
    else if (data.message) detail = data.message;
  } catch {
    /* ignore */
  }
  const err = new Error(detail);
  err.status = res.status;
  return err;
}

async function request(path, { method = "GET", body, auth = false } = {}) {
  const headers = {};
  if (auth) {
    const token = getToken();
    if (!token) {
      const err = new Error("Please sign in first");
      err.status = 401;
      throw err;
    }
    headers.Authorization = `Bearer ${token}`;
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) throw await parseError(res);
  if (res.status === 204) return null;
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function loginRequest(usernameOrEmail, password) {
  const body = new URLSearchParams();
  body.set("username", usernameOrEmail);
  body.set("password", password);

  const res = await fetch(`${API_BASE}/auth/Login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw await parseError(res);
  return res.json();
}

export const api = {
  signup(data) {
    return request("/auth/Signup", { method: "POST", body: data });
  },

  verifyEmail(data) {
    return request("/auth/verify-email", { method: "POST", body: data });
  },

  login: loginRequest,

  forgotPassword(email) {
    return request("/auth/forgot-password", {
      method: "POST",
      body: { email },
    });
  },

  resetPassword(data) {
    return request("/auth/reset-password", { method: "POST", body: data });
  },

  predict(loan) {
    return request("/loan/predict", { method: "POST", body: loan, auth: true });
  },

  monitoringHealth() {
    return request("/monitoring/health", { auth: true });
  },

  monitoringSummary(days = 7) {
    return request(`/monitoring/summary?days=${days}`, { auth: true });
  },

  monitoringPredictions(limit = 25) {
    return request(`/monitoring/predictions?limit=${limit}`, { auth: true });
  },

  monitoringPerformance() {
    return request("/monitoring/performance", { auth: true });
  },

  recordOutcome(data) {
    return request("/monitoring/outcomes", {
      method: "POST",
      body: data,
      auth: true,
    });
  },
};
