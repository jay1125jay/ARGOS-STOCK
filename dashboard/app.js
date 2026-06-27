const API = "http://127.0.0.1:8000/api/v1";

async function get(path) {
  const res = await fetch(API + path);
  return await res.json();
}

function clsSignal(v) {
  if (v === "BUY" || v === "BUY_WATCH" || v === "READY") return "good";
  if (v === "SELL" || v === "SELL_WATCH" || v === "HIGH") return "bad";
  if (v === "WAIT" || v === "NORMAL") return "wait";
  return "warn";
}

async function loadDashboard() {
  try {
    const health = await get("/health");
    const decision = await get("/decision");
    const report = await get("/report");
    const account = await get("/account");
    const execution = await get("/execution");
    const system = await get("/system");

    document.getElementById("apiStatus").textContent = "API ONLINE";
    document.getElementById("apiStatus").className = "good";

    const finalSignal = report.final_signal || decision.signal || "-";
    document.getElementById("finalSignal").textContent = finalSignal;
    document.getElementById("finalSignal").className = "signal " + clsSignal(finalSignal);

    document.getElementById("totalScore").textContent = report.total_score ?? "-";
    document.getElementById("mode").textContent = report.mode || decision.mode || "-";

    document.getElementById("health").textContent = (health.health ?? 0) + "%";
    document.getElementById("health").className = "health " + (health.health >= 90 ? "good" : "bad");
    document.getElementById("okCount").textContent = health.ok ?? "-";
    document.getElementById("totalCount").textContent = health.total ?? "-";

    document.getElementById("cash").textContent = account.cash ?? "-";
    document.getElementById("equity").textContent = account.equity ?? "-";
    document.getElementById("pnl").textContent = account.total_pnl ?? "-";

    document.getElementById("execSignal").textContent = execution.signal ?? "-";
    document.getElementById("execAction").textContent = execution.action ?? "-";
    document.getElementById("execPositions").textContent = execution.positions ?? "-";

    const aiBox = document.getElementById("aiStatus");
    aiBox.innerHTML = "";
    (health.items || []).forEach(x => {
      const div = document.createElement("div");
      div.className = "item";
      div.innerHTML = `<b>${x.module}</b><br><span class="${clsSignal(x.status)}">${x.status}</span>`;
      aiBox.appendChild(div);
    });

    const modBox = document.getElementById("modules");
    modBox.innerHTML = "";
    const modules = report.modules || {};
    Object.keys(modules).forEach(k => {
      const m = modules[k] || {};
      const div = document.createElement("div");
      div.className = "item";
      div.innerHTML = `<b>${k}</b><br>${m.signal || "-"}<br>Score: ${m.score ?? "-"}`;
      modBox.appendChild(div);
    });

    document.getElementById("systemBox").textContent = JSON.stringify({
      decision,
      execution,
      runner: system.runner,
      market: system.market,
      macro: system.macro
    }, null, 2);

  } catch (e) {
    document.getElementById("apiStatus").textContent = "API OFFLINE";
    document.getElementById("apiStatus").className = "bad";
    document.getElementById("systemBox").textContent = String(e);
  }
}

loadDashboard();
setInterval(loadDashboard, 3000);