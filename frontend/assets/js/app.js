import {
  api,
  clearSession,
  getLoginId,
  isLoggedIn,
  setSession,
} from "./api.js";

/* ——— enums matching backend schemas/loan.py ——— */
const EDUCATION = ["Bachelor's", "High School", "Master's", "PhD"];
const EMPLOYMENT = ["Full-time", "Part-time", "Self-employed", "Unemployed"];
const MARITAL = ["Divorced", "Married", "Single"];
const PURPOSE = ["Auto", "Business", "Education", "Home", "Other"];
const YES_NO = ["No", "Yes"];

const defaultLoan = () => ({
  age: 32,
  annual_Income: 2_400_000,
  loan_Amount: 1_200_000,
  credit_score: 680,
  months_employed: 36,
  interest_rate: 18.5,
  loan_term: 24,
  debt_to_income_ratio: 0.28,
  education_Level: "Bachelor's",
  type_of_Employment: "Full-time",
  marital_Status: "Single",
  has_Guarantor: "No",
  has_Dependents: "No",
  purpose_of_Loan: "Business",
});

const state = {
  loan: defaultLoan(),
  step: 0,
  lastResult: null,
  staff: null, // null | true | false
};

const $ = (sel, el = document) => el.querySelector(sel);
const appRoot = () => $("#app");

function formatNaira(n) {
  try {
    return new Intl.NumberFormat("en-NG", {
      style: "currency",
      currency: "NGN",
      maximumFractionDigits: 0,
    }).format(Number(n) || 0);
  } catch {
    return `₦${Number(n || 0).toLocaleString()}`;
  }
}

function formatPct(p, digits = 1) {
  if (p == null || Number.isNaN(Number(p))) return "—";
  const v = Number(p) <= 1 ? Number(p) * 100 : Number(p);
  return `${v.toFixed(digits)}%`;
}

function riskClass(level) {
  const l = (level || "").toLowerCase();
  if (l.includes("low")) return "low";
  if (l.includes("high")) return "high";
  return "medium";
}

function meterColor(level) {
  const c = riskClass(level);
  if (c === "low") return "#3d9b6e";
  if (c === "high") return "#c44b4b";
  return "#c4922a";
}

function route() {
  const hash = (location.hash || "#/").replace(/^#/, "") || "/";
  return hash.split("?")[0];
}

function navigate(path) {
  location.hash = path.startsWith("#") ? path : `#${path}`;
}

function optionsHtml(list, selected) {
  return list
    .map(
      (v) =>
        `<option value="${escapeAttr(v)}" ${v === selected ? "selected" : ""}>${escapeHtml(v)}</option>`
    )
    .join("");
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeAttr(s) {
  return escapeHtml(s).replaceAll("'", "&#39;");
}

function shell(content) {
  const logged = isLoggedIn();
  const id = getLoginId();
  return `
    <header class="topbar">
      <a class="brand" href="#/" style="text-decoration:none;color:inherit">
        <div class="brand-mark">A</div>
        <div class="brand-text">
          <strong>Apex Underwriting</strong>
          <span>Default risk desk</span>
        </div>
      </a>
      <nav class="nav">
        <a href="#/" class="${route() === "/" ? "active" : ""}">Overview</a>
        ${
          logged
            ? `
          <a href="#/assess" class="${route().startsWith("/assess") ? "active" : ""}">Assess facility</a>
          <a href="#/monitor" class="${route().startsWith("/monitor") ? "active" : ""}">Model desk</a>
          <span class="muted" style="padding:0 .5rem;font-size:.85rem">${escapeHtml(id)}</span>
          <button type="button" class="linkish" id="btn-logout">Sign out</button>
        `
            : `
          <a href="#/auth" class="${route().startsWith("/auth") ? "active" : ""}">Sign in</a>
        `
        }
      </nav>
    </header>
    <main class="main" id="page-main">${content}</main>
    <footer class="footer">
      Apex Underwriting · ML-assisted default probability · For decision support, not a sole credit decision
    </footer>
  `;
}

/* ——— Views ——— */

function viewHome() {
  return `
    <section class="hero stagger">
      <div>
        <p class="page-kicker">Credit risk · Origination desk</p>
        <h1>Price risk before you book the facility.</h1>
        <p class="lede">
          Apex scores loan applications with a trained default model: probability of default,
          risk band, and a clear flag for underwriting review — then logs every decision for model monitoring.
        </p>
        <div class="btn-row">
          ${
            isLoggedIn()
              ? `<a class="btn btn-primary" href="#/assess">Open assessment desk</a>
                 <a class="btn btn-ghost" href="#/monitor">Model health</a>`
              : `<a class="btn btn-primary" href="#/auth">Enter the desk</a>
                 <a class="btn btn-ghost" href="#/auth?tab=signup">Create officer account</a>`
          }
        </div>
      </div>
      <div class="panel hero-card">
        <p class="page-kicker">Sample risk read</p>
        <h2 style="margin-bottom:.25rem">Probability of default</h2>
        <p class="muted" style="margin-top:0">How a scored facility is presented</p>
        <div class="meter-wrap">
          <div class="meter js-meter" style="--p: 0; --meter-color: #c4922a" data-target="34"></div>
          <div class="meter-value">
            <div class="pct js-meter-pct" data-target="34">0%</div>
            <div class="label">model PD estimate</div>
          </div>
        </div>
        <div style="text-align:center;margin-top:.5rem">
          <span class="risk-badge medium">Medium risk</span>
        </div>
        <dl class="kv" style="margin-top:1.25rem">
          <dt>Currency context</dt><dd>₦ NGN</dd>
          <dt>Output</dt><dd>PD · band · flag</dd>
          <dt>Audit trail</dt><dd>Postgres log</dd>
        </dl>
      </div>
    </section>

    <section class="feature-grid stagger">
      <article class="feature">
        <h3>Facility assessment</h3>
        <p>Walk applicant, employment, and facility terms through a structured underwriting form aligned to the model features.</p>
      </article>
      <article class="feature">
        <h3>Risk decision card</h3>
        <p>See default probability on a meter, risk band (Low / Medium / High), and whether the model flags likely default.</p>
      </article>
      <article class="feature">
        <h3>Model operations</h3>
        <p>Staff officers review volume, latency, risk mix, recent scores, and ground-truth outcomes — not a vanity dashboard.</p>
      </article>
    </section>
  `;
}

function passwordFieldHtml({
  name,
  label = "Password",
  autocomplete = "current-password",
  minlength = null,
  required = true,
  hint = "",
}) {
  const minAttr = minlength != null ? ` minlength="${minlength}"` : "";
  const reqAttr = required ? " required" : "";
  return `
    <div class="field full">
      <label>${escapeHtml(label)}</label>
      <div class="password-field">
        <input name="${escapeAttr(name)}" type="password"${minAttr}${reqAttr} autocomplete="${escapeAttr(autocomplete)}" />
        <button type="button" class="toggle-password" data-toggle-password aria-label="Show password" title="Show password">Show</button>
      </div>
      ${hint ? `<span class="hint">${escapeHtml(hint)}</span>` : ""}
    </div>`;
}

function viewAuth() {
  const params = new URLSearchParams(location.hash.split("?")[1] || "");
  const tab = params.get("tab") || "login";
  const resetToken = params.get("token") || "";
  const resetEmail = params.get("email") || "";

  return `
    <div class="auth-wrap">
      <aside class="auth-side">
        <div>
          <p class="page-kicker">Officer access</p>
          <h2>Secure the desk before you score paper.</h2>
          <p class="muted">
            Sign in with your username or email. New accounts must verify their email
            before accessing the assessment desk.
          </p>
        </div>
        <div class="stat-strip">
          <div class="stat-chip"><strong>Secure</strong><span>Sign-in</span></div>
          <div class="stat-chip"><strong>Verified</strong><span>Email</span></div>
          <div class="stat-chip"><strong>Protected</strong><span>Desk</span></div>
        </div>
      </aside>

      <div class="panel">
        <div class="tabs" role="tablist">
          <button type="button" data-auth-tab="login" class="${tab === "login" ? "active" : ""}">Sign in</button>
          <button type="button" data-auth-tab="signup" class="${tab === "signup" ? "active" : ""}">Register</button>
          <button type="button" data-auth-tab="verify" class="${tab === "verify" ? "active" : ""}">Verify email</button>
          <button type="button" data-auth-tab="forgot" class="${tab === "forgot" ? "active" : ""}">Reset password</button>
        </div>

        <div id="auth-panel">
          ${authPanel(tab, { resetToken, resetEmail })}
        </div>
        <div id="auth-msg"></div>
      </div>
    </div>
  `;
}

function authPanel(tab, { resetToken = "", resetEmail = "" } = {}) {
  if (tab === "signup") {
    return `
      <form id="form-signup" class="form-grid">
        <div class="field"><label>Username</label><input name="username" minlength="3" required autocomplete="username" /></div>
        <div class="field"><label>Email</label><input name="email" type="email" required autocomplete="email" /></div>
        ${passwordFieldHtml({
          name: "password",
          label: "Password",
          autocomplete: "new-password",
          minlength: 8,
          hint: "Minimum 8 characters",
        })}
        <div class="field full btn-row" style="margin-top:.25rem">
          <button class="btn btn-primary" type="submit">Create account</button>
        </div>
      </form>`;
  }
  if (tab === "verify") {
    return `
      <form id="form-verify" class="form-grid">
        <div class="field full"><label>Email</label><input name="email" type="email" required autocomplete="email" /></div>
        <div class="field full"><label>Verification code</label><input name="code" required placeholder="Enter the code from your email" autocomplete="one-time-code" />
          <span class="hint">Check your inbox for the verification code we sent you.</span></div>
        <div class="field full btn-row"><button class="btn btn-primary" type="submit">Verify account</button></div>
      </form>`;
  }
  if (tab === "forgot") {
    return `
      <form id="form-forgot" class="form-grid">
        <div class="field full"><label>Account email</label><input name="email" type="email" required value="${escapeAttr(resetEmail)}" autocomplete="email" /></div>
        <div class="field full btn-row"><button class="btn btn-primary" type="submit">Send reset instructions</button></div>
      </form>
      <hr style="border:0;border-top:1px solid var(--line);margin:1.25rem 0" />
      <p class="muted" style="margin-top:0;font-size:.9rem">Already have a reset link? Enter the details below to choose a new password.</p>
      <form id="form-reset" class="form-grid">
        <div class="field full"><label>Email</label><input name="email" type="email" required value="${escapeAttr(resetEmail)}" autocomplete="email" /></div>
        <div class="field full"><label>Reset code</label><input name="token" required value="${escapeAttr(resetToken)}" autocomplete="one-time-code" />
          <span class="hint">From the password reset email we sent you.</span></div>
        ${passwordFieldHtml({
          name: "new_password",
          label: "New password",
          autocomplete: "new-password",
          minlength: 8,
          hint: "Minimum 8 characters",
        })}
        <div class="field full btn-row"><button class="btn btn-primary" type="submit">Update password</button></div>
      </form>`;
  }
  return `
    <form id="form-login" class="form-grid">
      <div class="field full">
        <label>Username or email</label>
        <input name="identifier" required autocomplete="username" placeholder="you@company.com" />
      </div>
      ${passwordFieldHtml({
        name: "password",
        label: "Password",
        autocomplete: "current-password",
      })}
      <div class="field full btn-row">
        <button class="btn btn-primary" type="submit">Sign in to desk</button>
        <button class="btn btn-ghost" type="button" data-auth-tab="forgot">Forgot password</button>
      </div>
    </form>`;
}

function viewAssess() {
  if (!isLoggedIn()) {
    return `
      <div class="panel">
        <h2>Authentication required</h2>
        <p class="muted">Sign in to run facility assessments against the live model.</p>
        <div class="btn-row"><a class="btn btn-primary" href="#/auth">Sign in</a></div>
      </div>`;
  }

  const steps = [
    { title: "Applicant", sub: "Profile & capacity" },
    { title: "Employment", sub: "Income stability" },
    { title: "Facility", sub: "Terms & structure" },
    { title: "Review", sub: "Confirm package" },
    { title: "Decision", sub: "Model output" },
  ];

  return `
    <p class="page-kicker">Origination · Score facility</p>
    <h1>Assessment desk</h1>
    <p class="lede">Capture the application package, then run the default model. Amounts are in Nigerian Naira (₦) to match training features.</p>

    <div class="wizard-layout">
      <aside class="steps">
        ${steps
          .map(
            (s, i) => `
          <div class="step ${i === state.step ? "active" : ""} ${i < state.step ? "done" : ""}">
            <div class="step-num">${i + 1}</div>
            <div><strong>${s.title}</strong><small>${s.sub}</small></div>
          </div>`
          )
          .join("")}
      </aside>
      <div class="panel step-enter" id="assess-panel">
        ${assessStepHtml()}
        <div id="assess-msg"></div>
      </div>
    </div>
  `;
}

function assessStepHtml() {
  const L = state.loan;
  if (state.step === 0) {
    return `
      <div class="panel-head"><h2>Applicant</h2><span class="muted">Step 1 of 5</span></div>
      <form id="step-form" class="form-grid">
        <div class="field"><label>Age</label><input name="age" type="number" min="18" max="100" value="${L.age}" required /></div>
        <div class="field"><label>Credit score</label><input name="credit_score" type="number" min="300" max="900" value="${L.credit_score}" required /></div>
        <div class="field"><label>Marital status</label><select name="marital_Status">${optionsHtml(MARITAL, L.marital_Status)}</select></div>
        <div class="field"><label>Education</label><select name="education_Level">${optionsHtml(EDUCATION, L.education_Level)}</select></div>
        <div class="field"><label>Has dependents?</label><select name="has_Dependents">${optionsHtml(YES_NO, L.has_Dependents)}</select></div>
        <div class="field"><label>Has guarantor?</label><select name="has_Guarantor">${optionsHtml(YES_NO, L.has_Guarantor)}</select></div>
        <div class="field full btn-row">
          <button type="submit" class="btn btn-primary">Continue</button>
        </div>
      </form>`;
  }
  if (state.step === 1) {
    return `
      <div class="panel-head"><h2>Employment & income</h2><span class="muted">Step 2 of 5</span></div>
      <form id="step-form" class="form-grid">
        <div class="field"><label>Employment type</label><select name="type_of_Employment">${optionsHtml(EMPLOYMENT, L.type_of_Employment)}</select></div>
        <div class="field"><label>Months employed</label><input name="months_employed" type="number" min="0" value="${L.months_employed}" required /></div>
        <div class="field">
          <label>Annual income</label>
          <div class="prefix-input"><span>₦</span><input name="annual_Income" type="number" min="0" step="1000" value="${L.annual_Income}" required /></div>
        </div>
        <div class="field">
          <label>Debt-to-income ratio</label>
          <input name="debt_to_income_ratio" type="number" min="0" max="5" step="0.01" value="${L.debt_to_income_ratio}" required />
          <span class="hint">e.g. 0.28 = 28% of income to debt service</span>
        </div>
        <div class="field full btn-row">
          <button type="button" class="btn btn-ghost" data-back>Back</button>
          <button type="submit" class="btn btn-primary">Continue</button>
        </div>
      </form>`;
  }
  if (state.step === 2) {
    return `
      <div class="panel-head"><h2>Facility terms</h2><span class="muted">Step 3 of 5</span></div>
      <form id="step-form" class="form-grid">
        <div class="field">
          <label>Loan amount</label>
          <div class="prefix-input"><span>₦</span><input name="loan_Amount" type="number" min="0" step="1000" value="${L.loan_Amount}" required /></div>
        </div>
        <div class="field"><label>Purpose</label><select name="purpose_of_Loan">${optionsHtml(PURPOSE, L.purpose_of_Loan)}</select></div>
        <div class="field"><label>Interest rate (%)</label><input name="interest_rate" type="number" min="0" step="0.1" value="${L.interest_rate}" required /></div>
        <div class="field"><label>Term (months)</label><input name="loan_term" type="number" min="1" value="${L.loan_term}" required /></div>
        <div class="field full btn-row">
          <button type="button" class="btn btn-ghost" data-back>Back</button>
          <button type="submit" class="btn btn-primary">Continue</button>
        </div>
      </form>`;
  }
  if (state.step === 3) {
    return `
      <div class="panel-head"><h2>Package review</h2><span class="muted">Step 4 of 5</span></div>
      <p class="muted">Confirm the application before scoring. You can go back to edit any section.</p>
      <dl class="kv">
        <dt>Age / credit</dt><dd>${L.age} yrs · score ${L.credit_score}</dd>
        <dt>Education / marital</dt><dd>${escapeHtml(L.education_Level)} · ${escapeHtml(L.marital_Status)}</dd>
        <dt>Employment</dt><dd>${escapeHtml(L.type_of_Employment)} · ${L.months_employed} mo</dd>
        <dt>Income</dt><dd>${formatNaira(L.annual_Income)}</dd>
        <dt>DTI</dt><dd class="mono">${L.debt_to_income_ratio}</dd>
        <dt>Facility</dt><dd>${formatNaira(L.loan_Amount)} · ${escapeHtml(L.purpose_of_Loan)}</dd>
        <dt>Pricing / tenor</dt><dd>${L.interest_rate}% · ${L.loan_term} mo</dd>
        <dt>Guarantor / dependents</dt><dd>${escapeHtml(L.has_Guarantor)} / ${escapeHtml(L.has_Dependents)}</dd>
      </dl>
      <div class="btn-row">
        <button type="button" class="btn btn-ghost" data-back>Back</button>
        <button type="button" class="btn btn-primary" id="btn-score">Run default model</button>
      </div>`;
  }

  /* step 4 decision */
  const r = state.lastResult;
  if (!r) {
    return `<p class="empty">No decision yet. Go back and run the model.</p>
      <div class="btn-row"><button type="button" class="btn btn-ghost" data-back>Back</button></div>`;
  }

  const prob = Number(r.default_probability ?? r.probability_of_default ?? 0);
  const pct = Math.round(Math.min(100, Math.max(0, prob * 100)));
  const level = r.risk_level || r.Risk_level || "—";
  const flag = r.risk_flag ?? r.Risk_flag;
  const pred = r.prediction;
  const rc = riskClass(level);

  return `
    <div class="panel-head">
      <h2>Credit decision card</h2>
      <span class="risk-badge ${rc}">${escapeHtml(level)} risk</span>
    </div>
    <div class="decision-layout">
      <div>
        <div class="meter-wrap">
          <div class="meter js-meter" style="--p: 0; --meter-color: ${meterColor(level)}" data-target="${pct}"></div>
          <div class="meter-value">
            <div class="pct js-meter-pct" data-target="${pct}">0%</div>
            <div class="label">probability of default</div>
          </div>
        </div>
        <p class="muted" style="text-align:center;font-size:.88rem">
          Model estimate for this facility package. Use with policy, KYC, and manual review.
        </p>
      </div>
      <div>
        <dl class="kv">
          <dt>Risk band</dt><dd>${escapeHtml(level)}</dd>
          <dt>Default flag</dt>
          <dd class="${flag == 1 || flag === true || pred === true || pred === "default" ? "flag-yes" : "flag-no"}">
            ${flag == 1 || flag === true ? "Likely default (flagged)" : "Below threshold"}
          </dd>
          <dt>Raw PD</dt><dd class="mono">${prob.toFixed(4)}</dd>
          <dt>Facility</dt><dd>${formatNaira(L.loan_Amount)}</dd>
          <dt>Income</dt><dd>${formatNaira(L.annual_Income)}</dd>
          <dt>Credit score</dt><dd class="mono">${L.credit_score}</dd>
        </dl>
        <div class="btn-row">
          <button type="button" class="btn btn-ghost" id="btn-new-assess">New assessment</button>
          <a class="btn btn-primary" href="#/monitor">Open model desk</a>
        </div>
      </div>
    </div>`;
}

function viewMonitor() {
  if (!isLoggedIn()) {
    return `
      <div class="panel">
        <h2>Sign in required</h2>
        <p class="muted">Please sign in to view model operations.</p>
        <div class="btn-row"><a class="btn btn-primary" href="#/auth">Sign in</a></div>
      </div>`;
  }

  return `
    <p class="page-kicker">Model operations</p>
    <h1>Model desk</h1>
    <p class="lede">
      Live health, score volume, risk mix, and recent predictions for authorized officers.
    </p>
    <div id="monitor-root">
      <div class="panel">
        <p class="muted">Loading model desk…</p>
        <div class="skeleton" style="margin-top:1rem"></div>
        <div class="skeleton" style="margin-top:.75rem;min-height:3rem"></div>
      </div>
    </div>
  `;
}

function renderMonitorData({ health, summary, predictions, perfError, accessDenied }) {
  const root = $("#monitor-root");
  if (!root) return;

  if (accessDenied) {
    root.innerHTML = `
      <div class="panel">
        <h2>Access restricted</h2>
        <p class="muted">
          You are signed in, but this model desk is limited to authorized underwriting staff.
          Please contact your administrator if you need access.
        </p>
        <div class="btn-row" style="margin-top:1rem">
          <a class="btn btn-primary" href="#/assess">Back to assessment desk</a>
        </div>
      </div>`;
    return;
  }

  const h = health || {};
  const s = summary || {};
  const mix = s.risk_level_mix || {};
  const mixTotal = Object.values(mix).reduce((a, b) => a + b, 0) || 1;
  const items = (predictions && predictions.items) || [];

  root.innerHTML = `
    <div class="kpi-row">
      <div class="kpi">
        <div class="label">Health</div>
        <div class="value"><span class="status-pill ${h.status === "ok" ? "ok" : "degraded"}">${escapeHtml(h.status || "—")}</span></div>
        <div class="sub mono">${escapeHtml(h.model_version || "")}</div>
      </div>
      <div class="kpi">
        <div class="label">Predictions (24h)</div>
        <div class="value">${h.predictions_last_24h ?? "—"}</div>
        <div class="sub">errors ${h.errors_last_24h ?? 0} · rate ${formatPct(h.error_rate_last_24h, 1)}</div>
      </div>
      <div class="kpi">
        <div class="label">Window volume</div>
        <div class="value">${s.total_predictions ?? "—"}</div>
        <div class="sub">${s.window_days ?? 7}d · success ${s.success_count ?? 0}</div>
      </div>
      <div class="kpi">
        <div class="label">Labeled outcomes</div>
        <div class="value">${h.outcomes_recorded ?? 0}</div>
        <div class="sub">joined ${h.predictions_with_outcomes ?? 0}</div>
      </div>
    </div>

    <div class="split-2">
      <div class="panel">
        <div class="panel-head"><h3>Risk mix</h3><span class="muted">${s.window_days || 7} days</span></div>
        <div class="mix-bars">
          ${["Low", "Medium", "High"]
            .map((k) => {
              const n = mix[k] || 0;
              const pct = Math.round((n / mixTotal) * 100);
              return `<div class="mix-row">
                <span>${k}</span>
                <div class="mix-track"><div class="mix-fill ${k.toLowerCase()}" data-width="${pct}" style="width:0%"></div></div>
                <span class="mono">${n}</span>
              </div>`;
            })
            .join("")}
        </div>
        <dl class="kv" style="margin-top:1.25rem">
          <dt>Mean PD</dt><dd class="mono">${s.probability?.mean ?? "—"}</dd>
          <dt>P95 PD</dt><dd class="mono">${s.probability?.p95 ?? "—"}</dd>
          <dt>Latency p50</dt><dd class="mono">${s.latency_ms?.p50 ?? "—"} ms</dd>
          <dt>Positive rate</dt><dd class="mono">${s.positive_rate != null ? formatPct(s.positive_rate, 1) : "—"}</dd>
        </dl>
      </div>

      <div class="panel">
        <div class="panel-head"><h3>Record outcome</h3><span class="muted">Ground truth</span></div>
        <p class="muted" style="margin-top:0;font-size:.9rem">Attach whether a loan actually defaulted — unlocks performance metrics.</p>
        <form id="form-outcome" class="form-grid">
          <div class="field"><label>Loan ID</label><input name="loan_id" type="number" min="1" required /></div>
          <div class="field"><label>Defaulted?</label>
            <select name="defaulted"><option value="false">No</option><option value="true">Yes</option></select>
          </div>
          <div class="field full"><label>Notes</label><input name="notes" placeholder="Optional" /></div>
          <div class="field full btn-row"><button class="btn btn-primary" type="submit">Save outcome</button></div>
        </form>
        <div id="outcome-msg"></div>
        ${
          perfError
            ? `<p class="alert info" style="margin-top:1rem">${escapeHtml(perfError)}</p>`
            : ""
        }
      </div>
    </div>

    <div class="panel" style="margin-top:1rem">
      <div class="panel-head"><h3>Recent predictions</h3>
        <button type="button" class="btn btn-ghost" id="btn-refresh-monitor">Refresh</button>
      </div>
      <div class="table-wrap">
        ${
          items.length
            ? `<table class="data">
          <thead>
            <tr>
              <th>ID</th><th>Loan</th><th>PD</th><th>Band</th><th>Flag</th><th>Latency</th><th>Status</th><th>When</th>
            </tr>
          </thead>
          <tbody>
            ${items
              .map(
                (row) => `<tr>
              <td class="mono">${row.id}</td>
              <td class="mono">${row.loan_id}</td>
              <td class="mono">${Number(row.probability_of_default).toFixed(3)}</td>
              <td><span class="risk-badge ${riskClass(row.risk_level)}" style="font-size:.7rem">${escapeHtml(row.risk_level || "—")}</span></td>
              <td class="mono">${row.risk_flag}</td>
              <td class="mono">${row.latency_ms != null ? `${row.latency_ms} ms` : "—"}</td>
              <td>${escapeHtml(row.status || "—")}</td>
              <td class="mono">${escapeHtml((row.created_at || "").slice(0, 19))}</td>
            </tr>`
              )
              .join("")}
          </tbody>
        </table>`
            : `<p class="empty">No predictions logged yet. Run an assessment first.</p>`
        }
      </div>
    </div>
  `;

  $("#btn-refresh-monitor")?.addEventListener("click", () => loadMonitor());
  $("#form-outcome")?.addEventListener("submit", onOutcomeSubmit);
}

async function loadMonitor() {
  const root = $("#monitor-root");
  if (!root) return;
  try {
    const [health, summary, predictions] = await Promise.all([
      api.monitoringHealth(),
      api.monitoringSummary(7),
      api.monitoringPredictions(25),
    ]);
    state.staff = true;
    let perfError = "";
    try {
      await api.monitoringPerformance();
    } catch (e) {
      perfError = e.message || "Performance metrics need recorded outcomes.";
    }
    renderMonitorData({ health, summary, predictions, perfError });
    animateMixBars();
    playPageEnter();
  } catch (e) {
    if (e.status === 403) {
      state.staff = false;
      renderMonitorData({ accessDenied: true });
      return;
    }
    if (e.status === 401) {
      clearSession();
      navigate("/auth");
      return;
    }
    root.innerHTML = `<div class="panel"><p class="alert error">${escapeHtml(e.message)}</p></div>`;
  }
}

async function onOutcomeSubmit(e) {
  e.preventDefault();
  const fd = new FormData(e.target);
  const msg = $("#outcome-msg");
  try {
    await api.recordOutcome({
      loan_id: Number(fd.get("loan_id")),
      defaulted: fd.get("defaulted") === "true",
      notes: fd.get("notes") || null,
    });
    if (msg) msg.innerHTML = `<p class="alert success">Outcome saved.</p>`;
    loadMonitor();
  } catch (err) {
    if (msg) msg.innerHTML = `<p class="alert error">${escapeHtml(err.message)}</p>`;
  }
}

/* ——— Motion helpers ——— */

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function easeOutCubic(t) {
  return 1 - (1 - t) ** 3;
}

function animateMeters() {
  document.querySelectorAll(".js-meter").forEach((meter) => {
    const target = Number(meter.dataset.target || 0);
    const pctEl = meter.parentElement?.querySelector(".js-meter-pct");

    if (prefersReducedMotion()) {
      meter.style.setProperty("--p", String(target));
      if (pctEl) pctEl.textContent = `${Math.round(target)}%`;
      return;
    }

    meter.style.setProperty("--p", "0");
    if (pctEl) pctEl.textContent = "0%";
    const start = performance.now();
    const duration = 1100;

    function frame(now) {
      const t = Math.min(1, (now - start) / duration);
      const v = target * easeOutCubic(t);
      meter.style.setProperty("--p", String(v));
      if (pctEl) pctEl.textContent = `${Math.round(v)}%`;
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  });
}

function animateMixBars() {
  document.querySelectorAll(".mix-fill[data-width]").forEach((el) => {
    const w = el.getAttribute("data-width") || "0";
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        el.style.width = `${w}%`;
      });
    });
  });
}

function playPageEnter() {
  const main = $("#page-main");
  if (!main) return;
  main.classList.remove("page-enter");
  // reflow so animation restarts on each navigation
  void main.offsetWidth;
  main.classList.add("page-enter");
  animateMeters();
}

/* ——— Render + events ——— */

function render() {
  const r = route();
  let body = viewHome();
  if (r.startsWith("/auth")) body = viewAuth();
  else if (r.startsWith("/assess")) body = viewAssess();
  else if (r.startsWith("/monitor")) body = viewMonitor();

  appRoot().innerHTML = shell(body);
  playPageEnter();

  $("#btn-logout")?.addEventListener("click", () => {
    clearSession();
    state.staff = null;
    navigate("/");
  });

  bindAuth();
  bindAssess();
  if (r.startsWith("/monitor")) loadMonitor();
}

function showMsg(sel, text, type = "error") {
  const el = $(sel);
  if (!el) return;
  el.innerHTML = text
    ? `<p class="alert ${type}">${escapeHtml(text)}</p>`
    : "";
}

function bindPasswordToggles() {
  document.querySelectorAll("[data-toggle-password]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const wrap = btn.closest(".password-field");
      const input = wrap?.querySelector("input");
      if (!input) return;
      const showing = input.type === "text";
      input.type = showing ? "password" : "text";
      btn.textContent = showing ? "Show" : "Hide";
      btn.setAttribute("aria-label", showing ? "Show password" : "Hide password");
      btn.title = showing ? "Show password" : "Hide password";
    });
  });
}

function bindAuth() {
  bindPasswordToggles();

  document.querySelectorAll("[data-auth-tab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const t = btn.getAttribute("data-auth-tab");
      navigate(`/auth?tab=${t}`);
    });
  });

  $("#form-login")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const id = String(fd.get("identifier") || "").trim();
    const password = String(fd.get("password") || "");
    try {
      const data = await api.login(id, password);
      setSession(data.access_token, id);
      showMsg("#auth-msg", "Signed in successfully. Opening the assessment desk…", "success");
      setTimeout(() => navigate("/assess"), 400);
    } catch (err) {
      showMsg("#auth-msg", err.message);
    }
  });

  $("#form-signup")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      const res = await api.signup({
        username: String(fd.get("username")).trim(),
        email: String(fd.get("email")).trim(),
        password: String(fd.get("password")),
      });
      showMsg(
        "#auth-msg",
        res.message ||
          "Account created. Please check your email for a verification code.",
        "success"
      );
      setTimeout(() => navigate("/auth?tab=verify"), 800);
    } catch (err) {
      showMsg("#auth-msg", err.message);
    }
  });

  $("#form-verify")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      const res = await api.verifyEmail({
        email: String(fd.get("email")).trim(),
        code: String(fd.get("code")).trim(),
      });
      showMsg(
        "#auth-msg",
        res.message || "Email verified. You can sign in now.",
        "success"
      );
      setTimeout(() => navigate("/auth?tab=login"), 700);
    } catch (err) {
      showMsg("#auth-msg", err.message);
    }
  });

  $("#form-forgot")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      const res = await api.forgotPassword(String(fd.get("email")).trim());
      showMsg(
        "#auth-msg",
        res.message ||
          "If that email is registered, password reset instructions have been sent. Please check your inbox.",
        "success"
      );
    } catch (err) {
      showMsg("#auth-msg", err.message);
    }
  });

  $("#form-reset")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      const res = await api.resetPassword({
        email: String(fd.get("email")).trim(),
        token: String(fd.get("token")).trim(),
        new_password: String(fd.get("new_password")),
      });
      showMsg(
        "#auth-msg",
        res.message || "Your password has been updated. You can sign in now.",
        "success"
      );
      setTimeout(() => navigate("/auth?tab=login"), 800);
    } catch (err) {
      showMsg("#auth-msg", err.message);
    }
  });
}

function readStepFields(form) {
  const fd = new FormData(form);
  const num = (k) => Number(fd.get(k));
  const str = (k) => String(fd.get(k));
  const keys = [...fd.keys()];
  for (const k of keys) {
    if (
      [
        "age",
        "annual_Income",
        "loan_Amount",
        "credit_score",
        "months_employed",
        "interest_rate",
        "loan_term",
        "debt_to_income_ratio",
      ].includes(k)
    ) {
      state.loan[k] = num(k);
    } else {
      state.loan[k] = str(k);
    }
  }
}

function bindAssess() {
  $("#step-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    readStepFields(e.target);
    state.step = Math.min(4, state.step + 1);
    render();
  });

  $("[data-back]")?.addEventListener("click", () => {
    state.step = Math.max(0, state.step - 1);
    render();
  });

  $("#btn-score")?.addEventListener("click", async () => {
    const msg = $("#assess-msg");
    const btn = $("#btn-score");
    if (btn) {
      btn.disabled = true;
      btn.classList.add("is-loading");
    }
    if (msg) {
      msg.innerHTML = `
        <p class="alert info">Scoring facility against the default model…</p>
        <div class="score-progress" aria-hidden="true"><i></i></div>`;
    }
    try {
      const result = await api.predict(state.loan);
      state.lastResult = result;
      state.step = 4;
      render();
    } catch (err) {
      if (msg) msg.innerHTML = `<p class="alert error">${escapeHtml(err.message)}</p>`;
      if (btn) {
        btn.disabled = false;
        btn.classList.remove("is-loading");
      }
      if (err.status === 401) {
        clearSession();
        setTimeout(() => navigate("/auth"), 600);
      }
    }
  });

  $("#btn-new-assess")?.addEventListener("click", () => {
    state.loan = defaultLoan();
    state.lastResult = null;
    state.step = 0;
    render();
  });
}

window.addEventListener("hashchange", render);
window.addEventListener("DOMContentLoaded", render);
