const API = "/api/v1";
const TOKEN_KEY = "studyos_admin_token";
const USER_KEY = "studyos_admin_user";

const $ = (id) => document.getElementById(id);

function token() {
  return localStorage.getItem(TOKEN_KEY);
}

function setSession(access, user) {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(USER_KEY, JSON.stringify(user || {}));
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  const t = token();
  if (t) headers.Authorization = `Bearer ${t}`;
  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (res.status === 401 || res.status === 403) {
    clearSession();
    showLogin();
    throw new Error("Oturum gerekli veya yetkisiz");
  }
  if (options.raw === true) {
    if (!res.ok) throw new Error(`Hata ${res.status}`);
    return res;
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    const body = await res.json();
    if (!res.ok || body.success === false) {
      const msg = body?.error?.message || body?.message || `Hata ${res.status}`;
      throw new Error(msg);
    }
    return body;
  }
  if (!res.ok) throw new Error(`Hata ${res.status}`);
  return res;
}

function showLogin() {
  $("login-view").hidden = false;
  $("app-view").hidden = true;
}

function showApp() {
  $("login-view").hidden = true;
  $("app-view").hidden = false;
  const user = JSON.parse(localStorage.getItem(USER_KEY) || "{}");
  $("admin-email").textContent = user.email || "";
  loadOverview();
  loadUsers();
}

$("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("login-error").hidden = true;
  try {
    const body = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: $("login-email").value.trim(),
        password: $("login-password").value,
      }),
    });
    const data = body.data;
    if (data.user?.role !== "system_admin") {
      throw new Error("Bu panel yalnızca system_admin hesabı içindir");
    }
    setSession(data.access_token, data.user);
    showApp();
  } catch (err) {
    $("login-error").textContent = err.message;
    $("login-error").hidden = false;
  }
});

$("logout-btn").addEventListener("click", () => {
  clearSession();
  showLogin();
});

document.querySelectorAll(".nav").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const tab = btn.dataset.tab;
    $("page-title").textContent =
      tab === "overview" ? "Özet" : tab === "users" ? "Kullanıcılar" : "Sorular";
    ["overview", "users", "questions"].forEach((t) => {
      $(`tab-${t}`).hidden = t !== tab;
    });
    if (tab === "overview") loadOverview();
    if (tab === "users") loadUsers();
    if (tab === "questions") loadQuestions();
  });
});

async function loadOverview() {
  const body = await api("/admin/overview");
  const d = body.data;
  const entries = [
    ["Kullanıcı", d.users_total],
    ["Aktif", d.users_active],
    ["Admin", d.users_admin],
    ["Çalışma planı", d.study_plans],
    ["Oturum", d.study_sessions],
    ["Soru kaydı", d.question_records],
    ["AI soru", d.generated_questions],
    ["Havuz kartı", d.pool_cards],
    ["Deneme", d.exams],
    ["Hedef", d.goals],
    ["Sohbet", d.conversations],
    ["Beta geri bildirim", d.beta_feedback],
  ];
  $("overview-grid").innerHTML = entries
    .map(
      ([l, n]) =>
        `<div class="card"><div class="n">${n}</div><div class="l">${l}</div></div>`
    )
    .join("");
}

async function loadUsers(q = "") {
  const qs = new URLSearchParams({ page: "1", page_size: "100" });
  if (q) qs.set("q", q);
  const body = await api(`/admin/users?${qs}`);
  const rows = body.data || [];
  $("users-body").innerHTML = rows
    .map(
      (u) => `<tr>
      <td>${escapeHtml(u.first_name)} ${escapeHtml(u.last_name)}</td>
      <td>${escapeHtml(u.email)}</td>
      <td>${escapeHtml(u.role)}</td>
      <td>${escapeHtml(u.status)}</td>
      <td>${u.study_plans}</td>
      <td>${u.study_sessions}</td>
      <td>${u.question_records}</td>
      <td><button data-id="${u.id}" class="secondary open-user">Detay</button></td>
    </tr>`
    )
    .join("");
  document.querySelectorAll(".open-user").forEach((btn) => {
    btn.addEventListener("click", () => openUser(btn.dataset.id));
  });
}

$("user-search-btn").addEventListener("click", () =>
  loadUsers($("user-search").value.trim())
);
$("user-search").addEventListener("keydown", (e) => {
  if (e.key === "Enter") loadUsers($("user-search").value.trim());
});

async function openUser(id) {
  const body = await api(`/admin/users/${id}`);
  const u = body.data;
  $("u-id").value = u.id;
  $("u-first").value = u.first_name;
  $("u-last").value = u.last_name;
  $("u-email").value = u.email;
  $("u-role").value = u.role;
  $("u-status").value = u.status;
  $("u-verified").checked = !!u.is_verified;
  $("u-password").value = "";
  $("user-form-error").hidden = true;
  $("user-dialog").showModal();
}

$("u-close").addEventListener("click", () => $("user-dialog").close());

$("user-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = $("u-id").value;
  const payload = {
    first_name: $("u-first").value.trim(),
    last_name: $("u-last").value.trim(),
    email: $("u-email").value.trim(),
    role: $("u-role").value,
    status: $("u-status").value,
    is_verified: $("u-verified").checked,
  };
  const pw = $("u-password").value;
  if (pw) payload.new_password = pw;
  try {
    await api(`/admin/users/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
    $("user-dialog").close();
    loadUsers($("user-search").value.trim());
    loadOverview();
  } catch (err) {
    $("user-form-error").textContent = err.message;
    $("user-form-error").hidden = false;
  }
});

$("u-export").addEventListener("click", async () => {
  const id = $("u-id").value;
  const res = await api(`/admin/users/${id}/export`, { raw: true });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `studyos-user-${id}.json`;
  a.click();
  URL.revokeObjectURL(url);
});

$("u-soft-delete").addEventListener("click", async () => {
  if (!confirm("Kullanıcı pasife alınsın mı?")) return;
  const id = $("u-id").value;
  await api(`/admin/users/${id}?hard=false`, { method: "DELETE" });
  $("user-dialog").close();
  loadUsers();
});

$("u-hard-delete").addEventListener("click", async () => {
  if (!confirm("KALICI silme — tüm ilişkili veriler silinebilir. Emin misiniz?")) return;
  const id = $("u-id").value;
  await api(`/admin/users/${id}?hard=true`, { method: "DELETE" });
  $("user-dialog").close();
  loadUsers();
});

async function loadQuestions() {
  const qs = new URLSearchParams({
    source: $("q-source").value,
    page: "1",
    page_size: "50",
  });
  const q = $("q-search").value.trim();
  if (q) qs.set("q", q);
  const body = await api(`/admin/questions?${qs}`);
  const items = body.data || [];
  $("questions-list").innerHTML = items.length
    ? items
        .map(
          (it) => `<div class="q-item">
        <div class="meta">
          <span class="badge">${escapeHtml(it.source)}</span>
          ${it.exam ? escapeHtml(it.exam) + " · " : ""}
          ${escapeHtml(it.subject || "")}
          ${it.topic ? " · " + escapeHtml(it.topic) : ""}
          ${it.difficulty ? " · " + escapeHtml(it.difficulty) : ""}
        </div>
        <div>${escapeHtml(it.stem || "")}</div>
      </div>`
        )
        .join("")
    : `<p class="muted">Soru bulunamadı.</p>`;
}

$("q-search-btn").addEventListener("click", loadQuestions);
$("q-source").addEventListener("change", loadQuestions);

function escapeHtml(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

// boot
(async function boot() {
  if (!token()) {
    showLogin();
    return;
  }
  try {
    await api("/admin/overview");
    showApp();
  } catch {
    showLogin();
  }
})();
