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

  const timeoutMs = options.timeoutMs || 60000;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  const signal = options.signal || controller.signal;

  try {
    const res = await fetch(`${API}${path}`, { ...options, headers, signal });
    clearTimeout(timeoutId);
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
      let msg = body?.error?.message || body?.message;
      if (!msg && body?.detail) {
        msg = Array.isArray(body.detail)
          ? body.detail.map((d) => `${d.loc ? d.loc.join(".") + ": " : ""}${d.msg}`).join("; ")
          : String(body.detail);
      }
      throw new Error(msg || `Hata ${res.status}`);
    }
    return body;
  }
  if (!res.ok) throw new Error(`Hata ${res.status}`);
  return res;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === "AbortError") {
      throw new Error("İstek zaman aşımına uğradı (Timeout: 60s)");
    }
    throw err;
  }
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

const _tabMeta = {
  overview:        { title: "Özet",           subtitle: "Sistem durumu ve aktivite" },
  users:           { title: "Kullanıcılar",   subtitle: "Kullanıcı yönetimi" },
  questions:       { title: "Sorular",        subtitle: "Tüm sorularda arama" },
  "question-pool": { title: "Soru Havuzu",    subtitle: "Soru envanteri ve üretim" },
  assets:          { title: "Assets",         subtitle: "Eğitim içerikleri" },
};

document.querySelectorAll(".nav").forEach((btn) => {
  btn.addEventListener("click", () => {
    if (!btn.dataset.tab) return;
    document.querySelectorAll(".nav").forEach((b) => {
      b.classList.remove("active");
      b.removeAttribute("aria-current");
    });
    btn.classList.add("active");
    btn.setAttribute("aria-current", "page");
    const tab = btn.dataset.tab;
    const meta = _tabMeta[tab] || { title: "Admin", subtitle: "" };
    $("page-title").textContent = meta.title;
    const sub = $("page-subtitle");
    if (sub) sub.textContent = meta.subtitle;
    ["overview", "users", "questions", "question-pool", "assets"].forEach((t) => {
      $(`tab-${t}`).hidden = t !== tab;
    });
    if (tab === "overview") loadOverview();
    if (tab === "users") loadUsers();
    if (tab === "questions") loadQuestions();
    if (tab === "question-pool") loadQuestionPool();
    if (tab === "assets") loadAssets();
    closeMobileMenu();
  });
});

async function loadQuestionPool() {
  // Scheduler status
  try {
    const ss = await api("/admin/question-pool/scheduler-status");
    const sd = ss.data;
    const mins = Math.round((sd.seconds_until_next || 0) / 60);
    $("qp-scheduler-status").textContent =
      `Scheduler: ${sd.enabled ? "ON" : "OFF"} | dry_run: ${sd.dry_run} | Son çalışma: ${sd.last_run ? new Date(sd.last_run).toLocaleString() : "—"} | Sonraki: ${mins} dk sonra`;
  } catch { $("qp-scheduler-status").textContent = ""; }

  const metrics = await api("/admin/question-pool/metrics");
  const m = metrics.data;
  $("qp-metrics-grid").innerHTML = `
    <div class="qp-metric-primary">
      <span class="qp-metric-val">${_fmtNum(m.total_questions)}</span>
      <span class="qp-metric-lbl">Toplam Soru</span>
    </div>
    <div class="qp-metric-primary">
      <span class="qp-metric-val" style="color:var(--color-success)">${m.healthy_topics || 0}</span>
      <span class="qp-metric-lbl">Healthy</span>
    </div>
    <div class="qp-metric-primary">
      <span class="qp-metric-val" style="color:var(--color-warning)">${m.low_topics || 0}</span>
      <span class="qp-metric-lbl">Low</span>
    </div>
    <div class="qp-metric-primary">
      <span class="qp-metric-val" style="color:var(--color-danger)">${m.empty_topics || 0}</span>
      <span class="qp-metric-lbl">Empty</span>
    </div>
    <div class="qp-metric-secondary">
      <span class="qp-metric-sm-val">${m.today_generated || 0}</span><span class="qp-metric-sm-lbl">bugün</span>
      <span class="qp-metric-sm-val">${m.yesterday_generated || 0}</span><span class="qp-metric-sm-lbl">dün</span>
      <span class="qp-metric-sm-val">${m.weekly_generated || 0}</span><span class="qp-metric-sm-lbl">hafta</span>
      <span class="qp-metric-sm-val">${m.gemini_calls_today || 0}</span><span class="qp-metric-sm-lbl">API</span>
      <span class="qp-metric-sm-val">${m.cache_hit_pct != null ? m.cache_hit_pct.toFixed(0) + "%" : "—"}</span><span class="qp-metric-sm-lbl">cache</span>
    </div>
  `;

  const inv = await api("/admin/question-pool/inventory");
  const rows = inv.data || [];
  const grouped = {};
  for (const r of rows) {
    if (!grouped[r.exam]) grouped[r.exam] = { total: 0, subjects: {} };
    grouped[r.exam].total += (r.current || 0);
    if (!grouped[r.exam].subjects[r.subject_code]) grouped[r.exam].subjects[r.subject_code] = { total: 0, topics: [] };
    grouped[r.exam].subjects[r.subject_code].total += (r.current || 0);
    grouped[r.exam].subjects[r.subject_code].topics.push(r);
  }

  let html = "";
  for (const [exam, exData] of Object.entries(grouped)) {
    const eCls = "ex-" + escapeHtml(exam).replace(/\W/g, "_");
    html += `<tr class="inv-exam-row" onclick="document.querySelectorAll('.${eCls}').forEach(el=>el.hidden=!el.hidden)">
      <td colspan="10">
        <strong>${escapeHtml(exam).toUpperCase()}</strong>
        <span class="inv-count">${exData.total} soru</span>
      </td>
    </tr>`;
    for (const [subj, subData] of Object.entries(exData.subjects)) {
      const sCls = eCls + "-sub-" + escapeHtml(subj).replace(/\W/g, "_");
      html += `<tr class="${eCls} inv-subj-row" hidden onclick="document.querySelectorAll('.${sCls}').forEach(el=>el.hidden=!el.hidden)">
        <td colspan="10">
          <span class="inv-subj-name">${escapeHtml(subj)}</span>
          <span class="inv-count">${subData.total} soru</span>
        </td>
      </tr>`;
      for (const r of subData.topics) {
        const suggested = Math.max(0, (r.target || 0) - (r.current || 0));
        const disable = suggested <= 0;
        html += `<tr class="${eCls} ${sCls} inv-topic-row" hidden>
          <td class="inv-topic-exam">${escapeHtml(r.exam)}</td>
          <td class="inv-topic-subj">${escapeHtml(r.subject_code)}</td>
          <td><strong>${escapeHtml(r.topic_code)}</strong></td>
          <td>${r.current}</td>
          <td>${r.minimum}</td>
          <td>${r.target}</td>
          <td>${escapeHtml(r.status)}</td>
          <td>${r.quality === null || r.quality === undefined ? "-" : r.quality.toFixed(1)}</td>
          <td>${r.last_generated ? new Date(r.last_generated).toLocaleString() : "-"}</td>
          <td>
            <div class="inv-actions">
              <button ${disable ? "disabled" : ""} class="s-btn s-btn-secondary qp-topup-btn" data-planned="${suggested}" data-exam="${escapeAttr(r.exam)}" data-subject="${escapeAttr(r.subject_code)}" data-topic="${escapeAttr(r.topic_code)}" data-diff="${escapeAttr(r.difficulty_band)}">
                Üret
              </button>
              <button class="s-btn s-btn-ghost qp-preview-topic-btn" data-exam="${escapeAttr(r.exam)}" data-subject="${escapeAttr(r.subject_code)}" data-topic="${escapeAttr(r.topic_code)}" data-diff="${escapeAttr(r.difficulty_band)}">
                Önizle
              </button>
              <button class="s-btn s-btn-danger qp-delete-btn" data-exam="${escapeAttr(r.exam)}" data-subject="${escapeAttr(r.subject_code)}" data-topic="${escapeAttr(r.topic_code)}" data-diff="${escapeAttr(r.difficulty_band)}">
                Sil
              </button>
            </div>
          </td>
        </tr>`;
      }
    }
  }
  $("qp-inventory-body").innerHTML = html;

  document.querySelectorAll(".qp-topup-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        const count = parseInt(btn.dataset.planned || "0", 10);
        if (!count) return;
        const payload = {
          exam: btn.dataset.exam,
          subject_code: btn.dataset.subject,
          topic_code: btn.dataset.topic,
          difficulty_band: btn.dataset.diff,
          count: count,
          dry_run: $("qp-dry-run").checked,
        };
        const res = await api("/admin/question-pool/fill", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        $("qp-last-result").textContent = `OK: accepted=${res.data.accepted || 0}, rejected=${res.data.rejected || 0}`;
        loadQuestionPool();
      } catch (err) {
        $("qp-last-result").textContent = `Hata: ${err.message}`;
      }
    });
  });

  document.querySelectorAll(".qp-delete-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        if (!confirm("Bu konudaki tüm havuz soruları silinsin mi?")) return;
        const payload = {
          exam: btn.dataset.exam,
          subject_code: btn.dataset.subject,
          topic_code: btn.dataset.topic,
          difficulty_band: btn.dataset.diff,
          dry_run: $("qp-dry-run").checked,
        };
        const res = await api("/admin/question-pool/delete", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        $("qp-last-result").textContent = `OK: ${JSON.stringify(res.data || {})}`;
        loadQuestionPool();
      } catch (err) {
        $("qp-last-result").textContent = `Hata: ${err.message}`;
      }
    });
  });

  document.querySelectorAll(".qp-regenerate-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        const count = parseInt(btn.dataset.planned || "0", 10);
        if (!count) return;
        const payload = {
          exam: btn.dataset.exam,
          subject_code: btn.dataset.subject,
          topic_code: btn.dataset.topic,
          difficulty_band: btn.dataset.diff,
          count: count,
          dry_run: $("qp-dry-run").checked,
        };
        const res = await api("/admin/question-pool/regenerate", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        $("qp-last-result").textContent = `OK: accepted=${res.data.accepted || 0}, rejected=${res.data.rejected || 0}`;
        loadQuestionPool();
      } catch (err) {
        $("qp-last-result").textContent = `Hata: ${err.message}`;
      }
    });
  });

  document.querySelectorAll(".qp-rebuild-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        const count = parseInt(btn.dataset.planned || "0", 10);
        if (!count) return;
        const payload = {
          exam: btn.dataset.exam,
          subject_code: btn.dataset.subject,
          topic_code: btn.dataset.topic,
          difficulty_band: btn.dataset.diff,
          count: count,
          dry_run: $("qp-dry-run").checked,
        };
        const res = await api("/admin/question-pool/rebuild", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        $("qp-last-result").textContent = `OK: accepted=${res.data.accepted || 0}, rejected=${res.data.rejected || 0}`;
        loadQuestionPool();
      } catch (err) {
        $("qp-last-result").textContent = `Hata: ${err.message}`;
      }
    });
  });

  document.querySelectorAll(".qp-review-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        const count = parseInt(btn.dataset.planned || "0", 10);
        if (!count) return;
        const payload = {
          exam: btn.dataset.exam,
          subject_code: btn.dataset.subject,
          topic_code: btn.dataset.topic,
          difficulty_band: btn.dataset.diff,
          count: count,
          dry_run: $("qp-dry-run").checked,
        };
        const res = await api("/admin/question-pool/review", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        $("qp-last-result").textContent = `OK: accepted=${res.data.accepted || 0}, rejected=${res.data.rejected || 0}`;
        loadQuestionPool();
      } catch (err) {
        $("qp-last-result").textContent = `Hata: ${err.message}`;
      }
    });
  });

  document.querySelectorAll(".qp-preview-topic-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        const payload = {
          exam: btn.dataset.exam,
          subject_code: btn.dataset.subject,
          topic_code: btn.dataset.topic,
          difficulty_band: btn.dataset.diff,
          dry_run: false,
        };
        const res = await api("/admin/question-pool/preview-latest", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        renderPreviewData(res.data);
      } catch (err) {
        $("qp-last-result").textContent = `Hata: ${err.message}`;
      }
    });
  });
}

$("qp-fill-missing-btn").addEventListener("click", async () => {
  try {
    $("qp-last-result").textContent = "Çalışıyor...";
    const payload = { dry_run: $("qp-dry-run").checked };
    const res = await api("/admin/question-pool/fill-missing", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    $("qp-last-result").textContent = `OK planned=${res.data.planned || 0}, accepted=${res.data.accepted || 0}`;
    loadQuestionPool();
  } catch (err) {
    $("qp-last-result").textContent = `Hata: ${err.message}`;
  }
});

$("qp-run-scheduler-btn").addEventListener("click", async () => {
  if (!confirm("Scheduler'ı şimdi çalıştırmak istediğinize emin misiniz? (fill-missing, non-dry)")) return;
  try {
    $("qp-last-result").textContent = "Scheduler çalışıyor...";
    const res = await api("/admin/question-pool/run-scheduler", { method: "POST" });
    $("qp-last-result").textContent = `Scheduler OK: planned=${res.data.planned || 0}, accepted=${res.data.accepted || 0}`;
    loadQuestionPool();
  } catch (err) {
    $("qp-last-result").textContent = `Scheduler hata: ${err.message}`;
  }
});

$("qp-trigger-trial-exams-btn").addEventListener("click", async () => {
  if (!confirm("Deneme üretimini (Trial Exams) şimdi tetiklemek istediğinize emin misiniz?")) return;
  try {
    const exam = $("qp-trial-exam-select").value;
    const url = exam ? `/admin/trial-exams/trigger?exam=${exam}` : "/admin/trial-exams/trigger";
    
    $("qp-last-result").textContent = "Deneme üretimi tetikleniyor...";
    const res = await api(url, { method: "POST" });
    $("qp-last-result").textContent = `Deneme üretimi OK: ${res.data.message || 'Başlatıldı'}`;
  } catch (err) {
    $("qp-last-result").textContent = `Deneme üretimi hata: ${err.message}`;
  }
});

$("qp-fill-selected-btn").addEventListener("click", async () => {
  const exam = $("qp-fill-exam").value.trim();
  const subject = $("qp-fill-subject").value.trim();
  const topic = $("qp-fill-topic").value.trim();
  const diff = $("qp-fill-diff").value;
  const count = parseInt($("qp-fill-count").value || "20", 10);
  if (!exam || !subject || !topic) {
    $("qp-fill-selected-result").textContent = "Exam, subject ve topic zorunlu.";
    return;
  }
  try {
    $("qp-fill-selected-result").textContent = "Üretiliyor...";
    const res = await api("/admin/question-pool/fill", {
      method: "POST",
      body: JSON.stringify({
        exam, subject_code: subject, topic_code: topic,
        difficulty_band: diff, count, dry_run: $("qp-dry-run").checked,
      }),
    });
    $("qp-fill-selected-result").textContent = `OK: accepted=${res.data.accepted || 0}, rejected=${res.data.rejected || 0}`;
    await loadQuestionPool();
    try { await loadOverview(); } catch { /* ignore */ }
  } catch (err) {
    $("qp-fill-selected-result").textContent = `Hata: ${err.message}`;
  }
});

function _fmtNum(n) {
  if (n == null) return "0";
  if (n >= 1000000) return (n / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
  if (n >= 10000) return (n / 1000).toFixed(1).replace(/\.0$/, "") + "K";
  return String(n);
}

async function loadOverview() {
  const body = await api("/admin/overview");
  const d = body.data;

  $("overview-grid").innerHTML = `
    <div class="dash-hero">
      <div class="dash-hero-primary">
        <div class="dash-metric-lg">
          <span class="dash-metric-value">${_fmtNum(d.users_total)}</span>
          <span class="dash-metric-label">Toplam Kullanıcı</span>
        </div>
        <div class="dash-metric-lg">
          <span class="dash-metric-value">${_fmtNum(d.pool_cards)}</span>
          <span class="dash-metric-label">Havuz Kartı</span>
        </div>
        <div class="dash-metric-lg">
          <span class="dash-metric-value">${_fmtNum(d.study_sessions)}</span>
          <span class="dash-metric-label">Oturum</span>
        </div>
      </div>
    </div>

    <div class="dash-grid">
      <div class="dash-section">
        <h3 class="dash-section-title">Kullanıcılar</h3>
        <div class="dash-stats">
          <div class="dash-stat">
            <span class="dash-stat-value">${_fmtNum(d.users_active)}</span>
            <span class="dash-stat-label">Aktif</span>
          </div>
          <div class="dash-stat">
            <span class="dash-stat-value">${_fmtNum(d.users_admin)}</span>
            <span class="dash-stat-label">Admin</span>
          </div>
          <div class="dash-stat">
            <span class="dash-stat-value">${_fmtNum(d.study_plans)}</span>
            <span class="dash-stat-label">Çalışma Planı</span>
          </div>
        </div>
      </div>

      <div class="dash-section">
        <h3 class="dash-section-title">Sorular</h3>
        <div class="dash-stats">
          <div class="dash-stat">
            <span class="dash-stat-value">${_fmtNum(d.generated_questions)}</span>
            <span class="dash-stat-label">AI Üretimi</span>
          </div>
          <div class="dash-stat">
            <span class="dash-stat-value">${_fmtNum(d.question_records)}</span>
            <span class="dash-stat-label">Soru Kaydı</span>
          </div>
        </div>
      </div>

      <div class="dash-section">
        <h3 class="dash-section-title">Platform</h3>
        <div class="dash-stats">
          <div class="dash-stat">
            <span class="dash-stat-value">${_fmtNum(d.exams)}</span>
            <span class="dash-stat-label">Deneme</span>
          </div>
          <div class="dash-stat">
            <span class="dash-stat-value">${_fmtNum(d.goals)}</span>
            <span class="dash-stat-label">Hedef</span>
          </div>
          <div class="dash-stat">
            <span class="dash-stat-value">${_fmtNum(d.conversations)}</span>
            <span class="dash-stat-label">Sohbet</span>
          </div>
          <div class="dash-stat">
            <span class="dash-stat-value">${_fmtNum(d.beta_feedback)}</span>
            <span class="dash-stat-label">Geri Bildirim</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

function _roleBadge(role) {
  const cls = role === "system_admin" ? "s-badge-primary" : "s-badge-neutral";
  return `<span class="s-badge ${cls}">${escapeHtml(role)}</span>`;
}
function _statusBadge(status) {
  const map = { active: "s-badge-success", inactive: "s-badge-neutral", pending_deletion: "s-badge-warning", anonymized: "s-badge-neutral" };
  return `<span class="s-badge ${map[status] || "s-badge-neutral"}">${escapeHtml(status)}</span>`;
}

async function loadUsers(q = "") {
  const qs = new URLSearchParams({ page: "1", page_size: "100" });
  if (q) qs.set("q", q);
  const body = await api(`/admin/users?${qs}`);
  const rows = body.data || [];
  $("users-body").innerHTML = rows
    .map(
      (u) => `<tr>
      <td><strong>${escapeHtml(u.first_name)} ${escapeHtml(u.last_name)}</strong></td>
      <td class="usr-email">${escapeHtml(u.email)}</td>
      <td>${_roleBadge(u.role)}</td>
      <td>${_statusBadge(u.status)}</td>
      <td>${u.study_plans}</td>
      <td>${u.study_sessions}</td>
      <td>${u.question_records}</td>
      <td><button data-id="${u.id}" class="s-btn s-btn-ghost open-user">Detay</button></td>
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
  const grouped = {};
  const ungrouped = [];
  
  for (const it of items) {
    if (it.exam && it.subject) {
      if (!grouped[it.exam]) grouped[it.exam] = {};
      if (!grouped[it.exam][it.subject]) grouped[it.exam][it.subject] = [];
      grouped[it.exam][it.subject].push(it);
    } else {
      ungrouped.push(it);
    }
  }

  let html = "";
  for (const [exam, subjects] of Object.entries(grouped)) {
    const examCls = "qe-" + escapeHtml(exam).replace(/\W/g, "_");
    const examCount = Object.values(subjects).reduce((s, arr) => s + arr.length, 0);
    html += `<div class="qs-group">
      <div class="qs-exam-row" onclick="document.querySelectorAll('.${examCls}').forEach(el=>el.hidden=!el.hidden)">
        <svg class="qs-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        <strong>${escapeHtml(exam).toUpperCase()}</strong>
        <span class="qs-count">${examCount}</span>
      </div>`;
    for (const [subj, subItems] of Object.entries(subjects)) {
      const subjCls = examCls + "-qs-" + escapeHtml(subj).replace(/\W/g, "_");
      html += `<div class="${examCls} qs-subj-row" hidden onclick="document.querySelectorAll('.${subjCls}').forEach(el=>el.hidden=!el.hidden)">
        <svg class="qs-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        <span class="qs-subj-name">${escapeHtml(subj)}</span>
        <span class="qs-count">${subItems.length}</span>
      </div>`;
      for (const it of subItems) {
        html += `<div class="${examCls} ${subjCls} qs-q-row" hidden>
          <div class="qs-q-meta">
            <span class="badge">${escapeHtml(it.source)}</span>
            ${it.topic ? `<span>${escapeHtml(it.topic)}</span>` : ""}
            ${it.difficulty ? `<span class="qs-q-diff">${escapeHtml(it.difficulty)}</span>` : ""}
          </div>
          <div class="qs-q-stem">${escapeHtml(it.stem || "")}</div>
        </div>`;
      }
    }
    html += `</div>`;
  }

  for (const it of ungrouped) {
    html += `<div class="qs-q-row qs-q-ungrouped">
      <div class="qs-q-meta">
        <span class="badge">${escapeHtml(it.source)}</span>
        ${it.exam ? `<span>${escapeHtml(it.exam)}</span>` : ""}
        ${it.subject ? `<span>${escapeHtml(it.subject)}</span>` : ""}
        ${it.topic ? `<span>${escapeHtml(it.topic)}</span>` : ""}
        ${it.difficulty ? `<span class="qs-q-diff">${escapeHtml(it.difficulty)}</span>` : ""}
      </div>
      <div class="qs-q-stem">${escapeHtml(it.stem || "")}</div>
    </div>`;
  }

  $("questions-list").innerHTML = items.length ? html : `<p class="qs-empty">Soru bulunamadı.</p>`;
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

function escapeAttr(s) {
  // Attribute context: quote/ampersand kaçışları yeterli.
  return escapeHtml(s).replaceAll("'", "&#39;");
}

// M34 — Preview dialog
$("qp-preview-close").addEventListener("click", () => $("qp-preview-dialog").close());

function renderPreviewData(d) {
  if (!d) return;
  const sc = d.scorecard || {};
  const bp = d.blueprint || {};
  const ef = d.exam_feel || {};
  const ms = d.multi_stage || {};
  const ob = d.option_balance || {};
  const dq = d.distractor_quality || {};

  let choicesHtml = "";
  for (const [k, v] of Object.entries(d.choices || {})) {
    const marker = k === d.correct_key ? " ✅" : "";
    choicesHtml += `<div style="margin:4px 0;"><strong>${escapeHtml(k)})</strong> ${escapeHtml(v)}${marker}</div>`;
  }

  $("qp-preview-body").innerHTML = `
    <div style="margin-bottom:12px;">
      <span class="badge">${escapeHtml(d.exam)}</span>
      <span class="muted">${escapeHtml(d.subject_code)} · ${escapeHtml(d.topic_code)} · ${escapeHtml(d.difficulty_band)}</span>
    </div>
    <div style="background:var(--bg-alt,#f8f8f8);padding:12px;border-radius:8px;margin-bottom:12px;">
      <div style="font-size:14px;line-height:1.6;">${escapeHtml(d.stem)}</div>
      <div style="margin-top:8px;">${choicesHtml}</div>
    </div>
    ${d.explanation ? `<div class="muted" style="margin-bottom:12px;"><strong>Açıklama:</strong> ${escapeHtml(d.explanation)}</div>` : ""}
    <h4>M34 Scorecard (overall: ${sc.overall || 0})</h4>
    <table style="width:100%;font-size:13px;">
      <tr><td>Style</td><td>${sc.style}</td><td>Difficulty</td><td>${sc.difficulty}</td></tr>
      <tr><td>Exam Feel</td><td>${sc.exam_feel}</td><td>Naturalness</td><td>${sc.naturalness}</td></tr>
      <tr><td>Reasoning</td><td>${sc.reasoning}</td><td>Distractors</td><td>${sc.distractors}</td></tr>
      <tr><td>Blueprint</td><td>${sc.blueprint}</td><td>Language</td><td>${sc.language}</td></tr>
      <tr><td>Fairness</td><td>${sc.fairness}</td><td>Virtual Student</td><td>${sc.virtual_student}</td></tr>
    </table>
    <h4>Blueprint Match: ${bp.score || 0}</h4>
    <h4>Exam Feel V2: ${ef.score || 0} ${ef.passed ? "✅" : "❌"}</h4>
    ${
      ef.detected_phrases && ef.detected_phrases.length
        ? `<div class="muted">Detected: ${ef.detected_phrases.map(escapeHtml).join(", ")}</div>`
        : ""
    }
    <h4>Multi-Stage Review: ${ms.score || 0} ${ms.passed ? "✅" : "❌"}</h4>
    ${
      ms.failed_stage
        ? `<div class="muted">Failed stage: ${escapeHtml(ms.failed_stage)}</div>`
        : ""
    }
    <h4>Option Balance: ${ob.score || 0}</h4>
    <h4>Distractor Quality: ${dq.score || 0}</h4>
    ${
      d.reject_reason
        ? `<div style="color:var(--danger,red);margin-top:8px;"><strong>Reject:</strong> ${escapeHtml(d.reject_reason)}</div>`
        : `<div style="color:green;margin-top:8px;">✅ Accepted</div>`
    }
  `;

  $("qp-preview-dialog").showModal();
}

async function showPreview(cardId) {
  try {
    const res = await api(`/admin/question-pool/preview/${cardId}`);
    const d = res.data;
    if (!d) return;
    const sc = d.scorecard || {};
    const bp = d.blueprint || {};
    const ef = d.exam_feel || {};
    const ms = d.multi_stage || {};
    const ob = d.option_balance || {};
    const dq = d.distractor_quality || {};

    let choicesHtml = "";
    for (const [k, v] of Object.entries(d.choices || {})) {
      const marker = k === d.correct_key ? " ✅" : "";
      choicesHtml += `<div style="margin:4px 0;"><strong>${escapeHtml(k)})</strong> ${escapeHtml(v)}${marker}</div>`;
    }

    $("qp-preview-body").innerHTML = `
      <div style="margin-bottom:12px;">
        <span class="badge">${escapeHtml(d.exam)}</span>
        <span class="muted">${escapeHtml(d.subject_code)} · ${escapeHtml(d.topic_code)} · ${escapeHtml(d.difficulty_band)}</span>
      </div>
      <div style="background:var(--bg-alt,#f8f8f8);padding:12px;border-radius:8px;margin-bottom:12px;">
        <div style="font-size:14px;line-height:1.6;">${escapeHtml(d.stem)}</div>
        <div style="margin-top:8px;">${choicesHtml}</div>
      </div>
      ${d.explanation ? `<div class="muted" style="margin-bottom:12px;"><strong>Açıklama:</strong> ${escapeHtml(d.explanation)}</div>` : ""}
      <h4>M34 Scorecard (overall: ${sc.overall || 0})</h4>
      <table style="width:100%;font-size:13px;">
        <tr><td>Style</td><td>${sc.style}</td><td>Difficulty</td><td>${sc.difficulty}</td></tr>
        <tr><td>Exam Feel</td><td>${sc.exam_feel}</td><td>Naturalness</td><td>${sc.naturalness}</td></tr>
        <tr><td>Reasoning</td><td>${sc.reasoning}</td><td>Distractors</td><td>${sc.distractors}</td></tr>
        <tr><td>Blueprint</td><td>${sc.blueprint}</td><td>Language</td><td>${sc.language}</td></tr>
        <tr><td>Fairness</td><td>${sc.fairness}</td><td>Virtual Student</td><td>${sc.virtual_student}</td></tr>
      </table>
      <h4>Blueprint Match: ${bp.score || 0}</h4>
      <h4>Exam Feel V2: ${ef.score || 0} ${ef.passed ? "✅" : "❌"}</h4>
      ${ef.detected_phrases && ef.detected_phrases.length ? `<div class="muted">Detected: ${ef.detected_phrases.map(escapeHtml).join(", ")}</div>` : ""}
      <h4>Multi-Stage Review: ${ms.score || 0} ${ms.passed ? "✅" : "❌"}</h4>
      ${ms.failed_stage ? `<div class="muted">Failed stage: ${escapeHtml(ms.failed_stage)}</div>` : ""}
      <h4>Option Balance: ${ob.score || 0}</h4>
      <h4>Distractor Quality: ${dq.score || 0}</h4>
      ${d.reject_reason ? `<div style="color:var(--danger,red);margin-top:8px;"><strong>Reject:</strong> ${escapeHtml(d.reject_reason)}</div>` : `<div style="color:green;margin-top:8px;">✅ Accepted</div>`}
    `;
    $("qp-preview-dialog").showModal();
  } catch (err) {
    alert("Preview yüklenemedi: " + err.message);
  }
}

// M34 — Batch Report
async function loadBatchReport() {
  try {
    $("qp-last-result").textContent = "Rapor yükleniyor...";
    const res = await api("/admin/question-pool/batch-report?limit=100");
    const r = res.data.report || {};
    const samples = res.data.sample_results || [];

    let html = `<h4>Batch Quality Report</h4>
      <table style="width:100%;font-size:13px;">
        <tr><td>Toplam</td><td>${r.total}</td><td>Accepted</td><td>${r.accepted}</td></tr>
        <tr><td>Rejected</td><td>${r.rejected}</td><td>Rewritten</td><td>${r.rewritten}</td></tr>
        <tr><td>Avg Quality</td><td>${r.average_quality}</td><td>Avg Exam Feel</td><td>${r.average_exam_feel}</td></tr>
        <tr><td>Avg Difficulty</td><td>${r.average_difficulty}</td><td>Gemini Cost</td><td>${r.gemini_cost}</td></tr>
      </table>`;

    if (Object.keys(r.reject_reasons || {}).length) {
      html += `<h4>Reject Reasons</h4><ul>`;
      for (const [reason, count] of Object.entries(r.reject_reasons)) {
        html += `<li>${escapeHtml(reason)}: ${count}</li>`;
      }
      html += `</ul>`;
    }

    if (samples.length) {
      html += `<h4>Sample Results (first 20)</h4><table style="width:100%;font-size:12px;">
        <tr><th>Stem</th><th>OK</th><th>Overall</th><th>Blueprint</th><th>Feel</th><th>Reject</th></tr>`;
      for (const s of samples) {
        html += `<tr>
          <td>${escapeHtml(s.stem_preview)}</td>
          <td>${s.accepted ? "✅" : "❌"}</td>
          <td>${s.overall}</td>
          <td>${s.blueprint}</td>
          <td>${s.exam_feel}</td>
          <td>${escapeHtml(s.reject_reason || "")}</td>
        </tr>`;
      }
      html += `</table>`;
    }

    $("qp-preview-body").innerHTML = html;
    $("qp-preview-dialog").showModal();
    $("qp-last-result").textContent = "";
  } catch (err) {
    $("qp-last-result").textContent = "Hata: " + err.message;
  }
}

async function loadProductionReport() {
  try {
    $("qp-last-result").textContent = "Production raporu yükleniyor...";
    const res = await api("/admin/question-pool/production-report");
    const r = res.data || {};

    $("qp-preview-body").innerHTML = `<h4>Production Report</h4>
      <table style="width:100%;font-size:13px;">
        <tr><td>Total Batches</td><td>${r.total_batches}</td></tr>
        <tr><td>Total Questions</td><td>${r.total_questions}</td></tr>
        <tr><td>Reject Rate</td><td>${r.reject_rate}%</td></tr>
        <tr><td>Rewrite Rate</td><td>${r.rewrite_rate}%</td></tr>
        <tr><td>Blueprint Match Avg</td><td>${r.blueprint_match_avg}</td></tr>
        <tr><td>Exam Feel Avg</td><td>${r.exam_feel_avg}</td></tr>
        <tr><td>Best Topic</td><td>${escapeHtml(r.best_topic)}</td></tr>
        <tr><td>Weakest Topic</td><td>${escapeHtml(r.weakest_topic)}</td></tr>
        <tr><td>Production Ready</td><td>${r.production_ready ? "✅ YES" : "❌ NO"}</td></tr>
      </table>`;
    $("qp-preview-dialog").showModal();
    $("qp-last-result").textContent = "";
  } catch (err) {
    $("qp-last-result").textContent = "Hata: " + err.message;
  }
}

$("qp-batch-report-btn").addEventListener("click", loadBatchReport);
$("qp-production-report-btn").addEventListener("click", loadProductionReport);

// ── M34.5 Live progress / cost gate / validate / stop ────────
let _qpProgressTimer = null;
let _qpWasActive = false;

function renderLivePreview(previews) {
  if (!previews) {
    $("qp-live-preview-body").textContent = "Henüz soru yok.";
    return;
  }

  const items = Array.isArray(previews) ? previews : [previews];
  if (items.length === 0) {
    $("qp-live-preview-body").textContent = "Henüz soru yok.";
    return;
  }

  $("qp-live-preview-body").innerHTML = items.map((preview, index) => {

    const scores = preview.scores || {};

    let choicesHtml = "";

    for (const [k, v] of Object.entries(preview.choices || {})) {
      const mark = k === preview.correct_key ? " ✅" : "";
      choicesHtml += `<div><strong>${escapeHtml(k)})</strong> ${escapeHtml(v)}${mark}</div>`;
    }

    return `
      <div style="
          margin-bottom:24px;
          padding:16px;
          border:1px solid #ddd;
          border-radius:8px;
          background:#fff;
      ">

        <h4>Soru ${index + 1}</h4>

        <div class="muted" style="margin-bottom:6px;">
          ${escapeHtml(preview.exam || "")}
          ·
          ${escapeHtml(preview.subject_code || "")}
          ·
          ${escapeHtml(preview.topic_code || "")}
        </div>

        <div style="line-height:1.6;margin-bottom:10px;">
          ${escapeHtml(preview.stem || "")}
        </div>

        ${choicesHtml}

        <div style="margin-top:10px;font-size:12px;">
          style=${scores.style ?? "-"}
          · blueprint=${scores.blueprint ?? "-"}
          · review=${scores.review ?? scores.exam_feel ?? "-"}
          · vsse=${scores.virtual_student ?? "-"}
          · overall=${scores.overall ?? "-"}
        </div>

      </div>
    `;

  }).join("");
}
function renderLiveProgress(p, options = {}) {
  if (!p) {
    $("qp-live-progress-body").textContent = "Idle";
    return;
  }
  $("qp-live-progress-body").innerHTML = `
    Status: <strong>${escapeHtml(p.status || "idle")}</strong> · mode=${escapeHtml(p.approval_mode || "auto")}<br/>
    Exam: ${escapeHtml(p.exam || "—")} · Topic: ${escapeHtml(p.topic_code || "—")}<br/>
    Question: ${p.current_index || 0} / ${p.planned || 0} ·
    Accepted: ${p.accepted || 0} · Rejected: ${p.rejected || 0} · Rewrite: ${p.rewrite || 0} · Failed: ${p.failed || 0}<br/>
    Gemini Calls: ${p.gemini_calls || 0} · Est. Cost: ${p.estimated_cost != null ? p.estimated_cost : "—"} ·
    Remaining: ${p.remaining != null ? p.remaining : "—"}
  `;
  if (p.last_preview && !options.skipPreview) renderLivePreview(p.last_preview);
}

async function refreshCostGate() {
  try {
    const res = await api("/admin/question-pool/cost-gate?planned_count=10");
    const g = res.data || {};
    $("qp-cost-gate").textContent =
      `Can Generate: ${g.can_generate ? "YES" : "NO"}` +
      (g.reason ? ` (${g.reason})` : "") +
      ` | daily ${g.daily_remaining}/${g.daily_limit}` +
      ` | hourly ${g.hourly_remaining}/${g.hourly_limit}` +
      ` | minute ${g.minute_remaining}/${g.minute_limit}` +
      ` | batch≈${g.suggested_batch_size}` +
      (g.estimated_batch_cost != null ? ` | est$${g.estimated_batch_cost}` : "");
  } catch {
    $("qp-cost-gate").textContent = "";
  }
}

async function refreshLiveProgress() {
  try {
    const res = await api("/admin/question-pool/live-progress");
    renderLiveProgress(res.data);
    const st = (res.data && res.data.status) || "idle";
    const active = st === "running" || st === "stopping";
    if (active) {
      _qpWasActive = true;
      if (!_qpProgressTimer) {
        _qpProgressTimer = setInterval(refreshLiveProgress, 2000);
      }
    } else {
      if (_qpProgressTimer) {
        clearInterval(_qpProgressTimer);
        _qpProgressTimer = null;
      }
      // Üretim bitince metrik / inventory sayılarını yenile
      if (_qpWasActive) {
        _qpWasActive = false;
        try {
          await loadQuestionPool();
        } catch { /* ignore */ }
        refreshPending();
        refreshCostGate();
        try {
          if ($("tab-overview") && !$("tab-overview").hidden) await loadOverview();
        } catch { /* ignore */ }
      }
    }
  } catch { /* ignore */ }
}

async function refreshPending() {
  try {
    const res = await api("/admin/question-pool/pending");
    const items = res.data?.items || [];
    if (!items.length) {
      $("qp-pending-body").textContent = "Boş";
      return;
    }
    $("qp-pending-body").innerHTML = items
      .map(
        (it) => `<div style="margin:6px 0;padding:6px;border-bottom:1px solid #eee;">
          <div>${escapeHtml((it.stem || "").slice(0, 120))}…</div>
          <button class="secondary qp-approve-btn" data-id="${escapeAttr(it.id)}">Approve</button>
          <button class="danger qp-reject-btn" data-id="${escapeAttr(it.id)}">Reject</button>
        </div>`
      )
      .join("");
    document.querySelectorAll(".qp-approve-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        await api("/admin/question-pool/approve-pending", {
          method: "POST",
          body: JSON.stringify({ pending_id: btn.dataset.id }),
        });
        refreshPending();
        loadQuestionPool();
      });
    });
    document.querySelectorAll(".qp-reject-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        await api("/admin/question-pool/reject-pending", {
          method: "POST",
          body: JSON.stringify({ pending_id: btn.dataset.id }),
        });
        refreshPending();
      });
    });
  } catch {
    $("qp-pending-body").textContent = "Pending yüklenemedi";
  }
}

$("qp-stop-gen-btn").addEventListener("click", async () => {
  try {
    await api("/admin/question-pool/stop-generation", { method: "POST" });
    $("qp-last-result").textContent = "Stop istendi — mevcut soru bitince duracak.";
    refreshLiveProgress();
  } catch (err) {
    $("qp-last-result").textContent = `Stop hata: ${err.message}`;
  }
});

$("qp-validate-5-btn").addEventListener("click", async (e) => {
  const btn = e.currentTarget;
  if (btn.disabled) return;
  const exam = $("qp-fill-exam").value.trim() || "kpss";
  const subject = $("qp-fill-subject").value.trim();
  const topic = $("qp-fill-topic").value.trim();
  if (!subject || !topic) {
    $("qp-last-result").textContent = "Validate için Fill Selected Topic alanlarını doldurun.";
    return;
  }
  btn.disabled = true;
  try {
    $("qp-last-result").textContent = "Validate: 5 soru üretiliyor (kaydedilmeyecek)...";
    refreshCostGate();
    const res = await api("/admin/question-pool/validate-generate", {
      method: "POST",
      body: JSON.stringify({
        exam,
        subject_code: subject,
        topic_code: topic,
        difficulty_band: $("qp-fill-diff").value,
        count: 5,
      }),
    });
    const qs = res.data?.questions || [];
    $("qp-last-result").textContent = `Validate OK: ${qs.length} soru (not saved). can_generate=${res.data?.cost_gate?.can_generate}`;
    if (qs.length) renderLivePreview(qs);
    if (res.data?.progress) renderLiveProgress(res.data.progress, { skipPreview: true });
    refreshCostGate();
  } catch (err) {
    $("qp-last-result").textContent = `Validate hata: ${err.message}`;
  } finally {
    btn.disabled = false;
  }
});

$("qp-run-missing-safe-btn").addEventListener("click", async (e) => {
  const btn = e.currentTarget;
  if (btn.disabled) return;
  if (!confirm("Sadece current < minimum topic'ler için güvenli üretim başlasın mı?")) return;
  btn.disabled = true;
  try {
    $("qp-last-result").textContent = "Safe missing run başlıyor...";
    refreshCostGate();
    if (_qpProgressTimer) clearInterval(_qpProgressTimer);
    _qpProgressTimer = setInterval(refreshLiveProgress, 2000);
    const res = await api("/admin/question-pool/run-missing-safe", {
      method: "POST",
      body: JSON.stringify({
        approval_mode: $("qp-approval-mode").value || "auto",
      }),
    });
    $("qp-last-result").textContent =
      `Safe OK: accepted=${res.data?.accepted || 0}, rejected=${res.data?.rejected || 0}, skipped=${res.data?.skipped_topics || 0}`;
    await refreshLiveProgress();
    await refreshPending();
    await refreshCostGate();
    await loadQuestionPool();
    try { await loadOverview(); } catch { /* ignore */ }
  } catch (err) {
    $("qp-last-result").textContent = `Safe run hata: ${err.message}`;
  } finally {
    btn.disabled = false;
  }
});

// ── Assets (EAE) ─────────────────────────────────────────────
let _selectedAssetId = null;
let _selectedAssetDetail = null;
let _assetSvgContent = "";

async function loadAssets() {
  const q = ($("asset-search")?.value || "").trim();
  const domain = $("asset-domain")?.value || "";
  const params = new URLSearchParams({ page: "1", page_size: "50" });
  if (q) params.set("q", q);
  if (domain) params.set("domain", domain);
  try {
    const res = await api(`/assets/search?${params}`);
    const items = res.data || [];
    $("assets-body").innerHTML = items
      .map((a) => {
        const title = a.title?.tr || a.title?.en || a.asset_id;
        return `<tr>
          <td>${title}</td>
          <td class="muted" style="font:var(--text-caption);">${a.asset_id}</td>
          <td>${a.version}</td>
          <td><button data-asset-id="${a.id}" class="s-btn s-btn-secondary asset-open-btn">Aç</button></td>
        </tr>`;
      })
      .join("");
    document.querySelectorAll(".asset-open-btn").forEach((btn) => {
      btn.addEventListener("click", () => openAsset(btn.dataset.assetId));
    });
  } catch (err) {
    $("assets-body").innerHTML = `<tr><td colspan="4">${err.message}</td></tr>`;
  }
}

async function openAsset(assetDbId) {
  _selectedAssetId = assetDbId;
  try {
    const res = await api(`/assets/${assetDbId}`);
    _selectedAssetDetail = res.data;
    const title = _selectedAssetDetail.title?.tr || _selectedAssetDetail.asset_id;
    $("asset-preview-meta").textContent = `${title} · ${_selectedAssetDetail.version} · nodes=${(_selectedAssetDetail.nodes || []).length}`;

    // Prefer bundle SVG for preview
    try {
      const raw = await api(`/assets/${assetDbId}/bundle`, { raw: true });
      const buf = await raw.arrayBuffer();
      const inflated = await inflateZlib(new Uint8Array(buf));
      const parsed = JSON.parse(new TextDecoder().decode(inflated));
      _assetSvgContent = parsed.svg_content || "";
    } catch (_) {
      _assetSvgContent = "";
    }
    renderAssetPreview(null);
    renderAssetNodes();
  } catch (err) {
    $("asset-preview-meta").textContent = err.message;
  }
}

function renderAssetPreview(highlightNodeId) {
  const host = $("asset-preview-svg");
  if (!_assetSvgContent) {
    host.innerHTML = `<div class="muted" style="padding:16px;">Bundle SVG yok — node listesinden highlight deneyin.</div>`;
    return;
  }
  let svg = _assetSvgContent;
  if (highlightNodeId) {
    svg = svg.replace(
      new RegExp(`id="${highlightNodeId.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"`, "g"),
      `id="${highlightNodeId}" fill="#FBBF24" stroke="#B45309" stroke-width="2.5"`
    );
  }
  host.innerHTML = svg;
}

function renderAssetNodes() {
  const q = ($("asset-node-search")?.value || "").trim().toLowerCase();
  const nodes = _selectedAssetDetail?.nodes || [];
  const filtered = nodes.filter((n) => {
    const name = (n.name?.tr || n.name?.en || "").toLowerCase();
    return !q || n.node_id.toLowerCase().includes(q) || name.includes(q);
  });
  $("asset-nodes-body").innerHTML = filtered
    .map(
      (n) => `<tr>
      <td class="muted" style="font:var(--text-caption);">${n.node_id}</td>
      <td>${n.name?.tr || n.name?.en || ""}</td>
      <td style="display:flex;gap:var(--space-1);">
        <button class="s-btn s-btn-secondary asset-hl-btn" data-node="${n.node_id}">Highlight</button>
        <button class="s-btn s-btn-secondary asset-edit-btn" data-node="${n.node_id}">Düzenle</button>
      </td>
    </tr>`
    )
    .join("");
  document.querySelectorAll(".asset-hl-btn").forEach((btn) => {
    btn.addEventListener("click", () => renderAssetPreview(btn.dataset.node));
  });
  document.querySelectorAll(".asset-edit-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const node = nodes.find((n) => n.node_id === btn.dataset.node);
      if (!node) return;
      $("asset-edit-node-id").value = node.node_id;
      $("asset-edit-name").value = JSON.stringify(node.name || {}, null, 2);
      $("asset-edit-attrs").value = JSON.stringify(node.attributes || {}, null, 2);
    });
  });
}

async function inflateZlib(bytes) {
  if (typeof DecompressionStream !== "undefined") {
    // browsers often lack raw zlib; fall back to manual inflate via pako-less approach
  }
  // Use Response + CompressionStream deflate-raw fallback: try DecompressionStream('deflate')
  try {
    const ds = new DecompressionStream("deflate");
    const stream = new Blob([bytes]).stream().pipeThrough(ds);
    const ab = await new Response(stream).arrayBuffer();
    return new Uint8Array(ab);
  } catch (_) {
    // zlib wrapper: strip 2-byte header + 4-byte checksum if present
    const raw = bytes.length > 6 ? bytes.slice(2, bytes.length - 4) : bytes;
    const ds = new DecompressionStream("deflate-raw");
    const stream = new Blob([raw]).stream().pipeThrough(ds);
    const ab = await new Response(stream).arrayBuffer();
    return new Uint8Array(ab);
  }
}

$("asset-search-btn")?.addEventListener("click", loadAssets);
$("asset-node-search")?.addEventListener("input", renderAssetNodes);
$("asset-compile-btn")?.addEventListener("click", async () => {
  const file = $("asset-svg-file").files?.[0];
  const manifest = $("asset-manifest-json").value.trim();
  if (!file || !manifest) {
    $("asset-compile-result").textContent = "SVG ve manifest gerekli";
    return;
  }
  const fd = new FormData();
  fd.append("svg_file", file);
  fd.append("manifest_json", manifest);
  try {
    const t = token();
    const res = await fetch(`${API}/assets/compile`, {
      method: "POST",
      headers: t ? { Authorization: `Bearer ${t}` } : {},
      body: fd,
    });
    const body = await res.json();
    if (!res.ok || body.success === false) {
      throw new Error(body?.error?.message || body?.message || `Hata ${res.status}`);
    }
    $("asset-compile-result").textContent = `OK: ${body.data?.asset_id}`;
    loadAssets();
  } catch (err) {
    $("asset-compile-result").textContent = err.message;
  }
});
$("asset-node-save-btn")?.addEventListener("click", async () => {
  if (!_selectedAssetId) return;
  const nodeId = $("asset-edit-node-id").value;
  if (!nodeId) return;
  try {
    const name = JSON.parse($("asset-edit-name").value || "{}");
    const attributes = JSON.parse($("asset-edit-attrs").value || "{}");
    await api(`/assets/${_selectedAssetId}/nodes/${encodeURIComponent(nodeId)}`, {
      method: "PATCH",
      body: JSON.stringify({ name, attributes }),
    });
    $("asset-node-save-result").textContent = "Kaydedildi";
    openAsset(_selectedAssetId);
  } catch (err) {
    $("asset-node-save-result").textContent = err.message;
  }
});

// Manual Question Add
$("qp-manual-add-btn")?.addEventListener("click", async () => {
  const btn = $("qp-manual-add-btn");
  const res = $("qp-manual-add-result");
  btn.disabled = true;
  res.textContent = "Kaydediliyor...";
  
  try {
    let eaeJson = null;
    const eaeText = $("qp-manual-eae").value.trim();
    if (eaeText) {
      eaeJson = JSON.parse(eaeText);
    }
    
    const payload = {
      exam: $("qp-manual-exam").value || "kpss",
      subject_code: $("qp-manual-subject").value || "cografya",
      topic_code: $("qp-manual-topic").value || "turkiye-haritasi",
      difficulty_band: $("qp-manual-diff").value || "medium",
      stem: $("qp-manual-stem").value,
      choices: {
        "A": $("qp-manual-a").value,
        "B": $("qp-manual-b").value,
        "C": $("qp-manual-c").value,
        "D": $("qp-manual-d").value,
      },
      correct_key: $("qp-manual-correct").value,
      explanation: $("qp-manual-explanation").value || null,
      eae_interaction: eaeJson
    };
    
    await api("/admin/question-pool/card", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    
    res.textContent = "Soru başarıyla havuza eklendi!";
    res.style.color = "green";
    
    // reset form fields
    $("qp-manual-stem").value = "";
    $("qp-manual-a").value = "";
    $("qp-manual-b").value = "";
    $("qp-manual-c").value = "";
    $("qp-manual-d").value = "";
    $("qp-manual-eae").value = "";
    
    await loadQuestionPool();
  } catch (err) {
    res.textContent = "Hata: " + err.message;
    res.style.color = "red";
  } finally {
    btn.disabled = false;
  }
});

// ── Theme toggle ─────────────────────────────────────────────
const THEME_KEY = "studyos_admin_theme";

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem(THEME_KEY, theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  applyTheme(current === "dark" ? "light" : "dark");
}

(function initTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  applyTheme(saved || "dark");
})();

document.querySelectorAll(".theme-toggle").forEach((btn) => {
  btn.addEventListener("click", toggleTheme);
});

// ── Mobile menu ──────────────────────────────────────────────
function openMobileMenu() {
  const sidebar = $("sidebar");
  const overlay = $("sidebar-overlay");
  const btn = $("mobile-menu-btn");
  if (!sidebar) return;
  sidebar.classList.add("open");
  if (overlay) { overlay.hidden = false; requestAnimationFrame(() => overlay.classList.add("visible")); }
  if (btn) btn.setAttribute("aria-expanded", "true");
}

function closeMobileMenu() {
  const sidebar = $("sidebar");
  const overlay = $("sidebar-overlay");
  const btn = $("mobile-menu-btn");
  if (!sidebar) return;
  sidebar.classList.remove("open");
  if (overlay) { overlay.classList.remove("visible"); setTimeout(() => { overlay.hidden = true; }, 250); }
  if (btn) btn.setAttribute("aria-expanded", "false");
}

if ($("mobile-menu-btn")) {
  $("mobile-menu-btn").addEventListener("click", () => {
    const sidebar = $("sidebar");
    if (sidebar && sidebar.classList.contains("open")) closeMobileMenu();
    else openMobileMenu();
  });
}

if ($("sidebar-overlay")) {
  $("sidebar-overlay").addEventListener("click", closeMobileMenu);
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
    refreshCostGate();
    refreshLiveProgress();
    refreshPending();
  } catch {
    showLogin();
  }
})();
