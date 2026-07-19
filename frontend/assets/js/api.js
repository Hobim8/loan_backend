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

/** Map status codes / raw API text to user-facing copy (never leak stack traces or “500” noise). */
function friendlyMessage(status, raw) {
  const text = (raw || "").trim();
  const lower = text.toLowerCase();

  // Prefer clear backend messages when they already read well
  if (text && !/^request failed/i.test(text) && !/internal server error/i.test(text)) {
    // Soften common technical phrasing
    if (lower.includes("staff access")) {
      return "You do not have permission to view this area. Please contact your administrator.";
    }
    if (lower.includes("invaild") || lower.includes("invalid credentials")) {
      return "Incorrect username or password. Please try again.";
    }
    if (lower.includes("invaild or expired") || lower.includes("invalid or expired token")) {
      return "Your session has expired. Please sign in again.";
    }
    if (lower.includes("invaild or expired verification") || lower.includes("invalid or expired verification")) {
      return "That verification code is invalid or has expired. Request a new code and try again.";
    }
    return text;
  }

  switch (status) {
    case 400:
      return "Please check your details and try again.";
    case 401:
      return "Incorrect username or password. Please try again.";
    case 403:
      return "You do not have permission to perform this action.";
    case 404:
      return "We could not find that account or resource.";
    case 422:
      return "Some fields are incomplete or invalid. Please review and try again.";
    case 429:
      return "Too many attempts. Please wait a moment and try again.";
    case 500:
    case 502:
    case 503:
    case 504:
      return "Something went wrong on our side. Please try again in a moment.";
    default:
      return "Something went wrong. Please try again.";
  }
}

async function parseError(res) {
  let raw = "";
  try {
    const data = await res.json();
    if (typeof data.detail === "string") raw = data.detail;
    else if (Array.isArray(data.detail))
      raw = data.detail.map((d) => d.msg || d.loc?.join(".") || "Invalid field").join("; ");
    else if (data.message) raw = data.message;
  } catch {
    /* ignore non-JSON bodies */
  }
  const err = new Error(friendlyMessage(res.status, raw));
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
