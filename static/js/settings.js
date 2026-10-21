const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
let state = null, presets = [], roles = {}, writable = false;

const adminToken = () => { try { return sessionStorage.getItem("hakamAdmin") || ""; } catch { return ""; } };
const headers = () => ({ "Content-Type": "application/json", "X-Admin-Token": adminToken() });

function status(msg, cls = "note") { $("status").className = cls; $("status").textContent = msg; }

async function load() {
  const r = await fetch("/api/settings", { headers: headers() });
  const d = await r.json();
  if (!r.ok) { $("banner").hidden = false; $("banner").textContent = d.error; return; }
  state = d.settings; presets = d.presets; roles = d.roles; writable = d.writable;
  state.providers.forEach((p) => { p.original_id = p.id; });
  $("auth").hidden = writable || d.desktop;
  if (!d.desktop && !d.admin_configured) {
    $("auth").hidden = true;
    banner("الإعدادات للقراءة فقط: لم يُضبط HAKAM_ADMIN_TOKEN على الخادم. اضبطه، أو مرّر الإعدادات عبر HAKAM_SETTINGS_JSON.");
  } else if (d.source === "env") {
    banner("الإعدادات مأخوذة من متغير البيئة HAKAM_SETTINGS_JSON، ولا يمكن تعديلها من هنا.");
    writable = false;
  }
  $("preset").innerHTML = presets.map((p) => `<option value="${p.id}">${esc(p.name)}</option>`).join("");
  render();
}

function banner(text) { $("banner").hidden = false; $("banner").textContent = text; }

function providerCard(p, i) {
  return `<div class="card" data-i="${i}">
    <div class="grid">
      <label>المعرّف (id)<input data-k="id" value="${esc(p.id)}"></label>
      <label>الاسم<input data-k="name" value="${esc(p.name)}" style="direction:rtl;text-align:right"></label>
      <label>النوع<select data-k="type">
        <option value="openai" ${p.type === "openai" ? "selected" : ""}>متوافق مع OpenAI</option>
        <option value="anthropic" ${p.type === "anthropic" ? "selected" : ""}>Anthropic (أصلي)</option></select></label>
      <label>Base URL<input data-k="base_url" value="${esc(p.base_url)}"></label>
      <label>مفتاح API ${p.api_key_set ? '<span class="ok">✓ محفوظ</span>' : ""}<input data-k="api_key" type="password" value="${esc(p.api_key)}" placeholder="sk-… أو env:MY_KEY"></label>
    </div>
    <div class="row-actions">
      <button class="btn" data-act="models">جلب النماذج</button>
      <button class="btn" data-act="test">اختبار الاتصال</button>
      <button class="btn danger" data-act="remove">حذف</button>
      <span class="note" data-out></span>
    </div></div>`;
}

function render() {
  $("providers").innerHTML = state.providers.map(providerCard).join("");
  const opts = (sel) => state.providers.map((p) => `<option value="${esc(p.id)}" ${p.id === sel ? "selected" : ""}>${esc(p.name)}</option>`).join("");
  $("agents").innerHTML = Object.entries(roles).map(([role, label]) => {
    const a = state.agents[role] || {};
    return `<div><b>${esc(label)}</b>
      <label>المزود<select data-role="${role}" data-k="provider">${opts(a.provider)}</select></label>
      <label>النموذج<input data-role="${role}" data-k="model" list="modelList" value="${esc(a.model)}"></label></div>`;
  }).join("");
  $("threshold").value = state.verification_threshold;
  document.querySelectorAll(".settings input, .settings select, .settings button").forEach((el) => {
    if (["adminToken", "adminBtn"].includes(el.id)) return;
    if (!writable && el.id !== "preset") el.disabled = true;
  });
  $("addProvider").disabled = $("save").disabled = !writable;
}

function collect() {
  document.querySelectorAll("#providers .card").forEach((card) => {
    const p = state.providers[+card.dataset.i];
    card.querySelectorAll("[data-k]").forEach((el) => { p[el.dataset.k] = el.value.trim(); });
  });
  document.querySelectorAll("#agents [data-role]").forEach((el) => {
    state.agents[el.dataset.role] = state.agents[el.dataset.role] || {};
    state.agents[el.dataset.role][el.dataset.k] = el.value.trim();
  });
  state.verification_threshold = parseFloat($("threshold").value);
  return state;
}

$("providers").addEventListener("click", async (e) => {
  const act = e.target.dataset.act; if (!act) return;
  const card = e.target.closest(".card"), i = +card.dataset.i, out = card.querySelector("[data-out]");
  collect();
  const p = state.providers[i];
  if (act === "remove") {
    if (!confirm(`حذف المزود ${p.name}؟`)) return;
    state.providers.splice(i, 1); render(); return;
  }
  out.className = "note"; out.textContent = "…";
  const model = Object.values(state.agents).find((a) => a.provider === p.id)?.model || "";
  const url = act === "test" ? "/api/providers/test" : "/api/providers/models";
  if (act === "test" && !model) { out.className = "err"; out.textContent = "عيّن هذا المزود لوكيل أولاً لتحديد نموذج الاختبار"; return; }
  const r = await fetch(url, { method: "POST", headers: headers(), body: JSON.stringify({ provider: p, model }) });
  const d = await r.json();
  if (!d.ok) { out.className = "err"; out.textContent = d.error || "فشل"; return; }
  if (act === "test") { out.className = "ok"; out.textContent = `✓ يعمل (${model}): ${d.reply}`; }
  else {
    $("modelList").innerHTML = d.models.map((m) => `<option value="${esc(m)}">`).join("");
    out.className = "ok"; out.textContent = `✓ ${d.models.length} نموذجاً — تظهر الآن كاقتراحات في حقول النماذج`;
  }
});

$("addProvider").onclick = () => {
  collect();
  const pr = presets.find((p) => p.id === $("preset").value);
  let id = pr.id === "custom" ? "custom" : pr.id, n = 2;
  while (state.providers.some((p) => p.id === id)) id = `${pr.id}-${n++}`;
  state.providers.push({ id, name: pr.name, type: pr.type, base_url: pr.base_url, api_key: "", api_key_set: false });
  $("modelList").innerHTML = (pr.models || []).map((m) => `<option value="${esc(m)}">`).join("");
  render();
};

$("save").onclick = async () => {
  collect(); status("جارٍ الحفظ…");
  const r = await fetch("/api/settings", { method: "PUT", headers: headers(), body: JSON.stringify(state) });
  const d = await r.json();
  if (!r.ok) { status(d.error, "err"); return; }
  state = d.settings; state.providers.forEach((p) => { p.original_id = p.id; });
  render(); status("✓ حُفظت الإعدادات وستُطبَّق على السؤال التالي", "ok");
};

$("adminBtn").onclick = () => {
  try { sessionStorage.setItem("hakamAdmin", $("adminToken").value); } catch {}
  load();
};

load();
