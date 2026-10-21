const $ = (id) => document.getElementById(id);
let conversationId = null;

const md = (text) => DOMPurify.sanitize(marked.parse(text || ""));
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function renderStages(stages) {
  if (!stages) return "";
  const parts = [];
  if (stages.A) parts.push(`<div class="stage"><h4>المرحلة A — التحليل الجنائي</h4>${md(stages.A.analysis)}</div>`);
  if (stages.B) {
    parts.push(`<div class="stage"><h4>المرحلة B — المداولة (${stages.B.passed_count}/${stages.B.total_count} مقبولة)</h4>`);
    for (const h of stages.B.hypotheses || []) {
      const ev = h.evaluation || {};
      const issues = (ev.issues || []).map((i) => `<li>${esc(i)}</li>`).join("");
      parts.push(`<details><summary>${esc(h.hypothesis_type_ar)}<span class="badge ${h.passed ? "ok" : "bad"}">${h.passed ? "مقبولة" : "مرفوضة"} · ${(+ev.score || 0).toFixed(2)}</span></summary>${md(h.hypothesis)}${issues ? `<p><b>ثغرات أثارها الادعاء:</b></p><ul>${issues}</ul>` : ""}</details>`);
    }
    parts.push("</div>");
  }
  return `<details class="stages"><summary>مراحل التفكير</summary>${parts.join("")}</details>`;
}

function addMessage(role, content, stages) {
  $("welcome")?.remove();
  const el = document.createElement("article");
  el.className = `msg ${role}`;
  el.innerHTML = role === "user" ? esc(content).replace(/\n/g, "<br>") : md(content) + renderStages(stages);
  $("thread").appendChild(el);
  el.scrollIntoView({ behavior: "smooth", block: "start" });
  return el;
}

async function loadArchive() {
  const items = await (await fetch("/api/conversations")).json();
  $("archive").innerHTML = "";
  for (const c of items) {
    const li = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = c.title || c.first_message || `قضية ${c.id}`;
    const del = document.createElement("button");
    del.className = "del"; del.title = "حذف القضية"; del.textContent = "✕";
    del.onclick = async (ev) => {
      ev.stopPropagation();
      if (!confirm("حذف هذه القضية نهائياً؟")) return;
      let token = ""; try { token = sessionStorage.getItem("hakamAdmin") || ""; } catch {}
      const r = await fetch(`/api/conversations/${c.id}`, { method: "DELETE", headers: { "X-Admin-Token": token } });
      if (!r.ok) { alert("الحذف متاح في نسخة سطح المكتب أو للمسؤول فقط"); return; }
      if (conversationId === c.id) $("newCase").click(); else loadArchive();
    };
    li.append(label, del);
    li.className = c.id === conversationId ? "active" : "";
    li.onclick = () => openConversation(c.id);
    $("archive").appendChild(li);
  }
}

async function openConversation(id) {
  conversationId = id;
  $("thread").innerHTML = "";
  const messages = await (await fetch(`/api/conversations/${id}`)).json();
  for (const m of messages) addMessage(m.role, m.content, m.metadata ? JSON.parse(m.metadata) : null);
  $("sidebar").classList.remove("open");
  loadArchive();
}

$("composer").addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = $("question").value.trim();
  if (!question) return;
  addMessage("user", question);
  $("question").value = "";
  $("send").disabled = true;
  const wait = addMessage("assistant", "");
  wait.innerHTML = '<p class="thinking">المحكمة منعقدة: تشريح الوقائع ← الفرضيات الثلاث ← المداولة ← الحكم…</p>';
  try {
    const res = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question, conversation_id: conversationId }) });
    const data = await res.json();
    wait.remove();
    if (!res.ok) throw new Error(data.error || res.statusText);
    conversationId = data.conversation_id;
    addMessage("assistant", data.response, data.stages);
    loadArchive();
  } catch (err) {
    wait.remove();
    addMessage("error", `⚠️ ${err.message}`);
  } finally {
    $("send").disabled = false;
  }
});

$("question").addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) $("composer").requestSubmit(); });
$("newCase").onclick = () => { conversationId = null; $("thread").innerHTML = '<div class="welcome" id="welcome"><h2>اعرض قضيتك</h2></div>'; loadArchive(); };
$("menu").onclick = () => $("sidebar").classList.toggle("open");
loadArchive();
