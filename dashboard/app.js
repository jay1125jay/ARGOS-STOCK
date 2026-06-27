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
    const runner = await get("/runner");
    const technical = await get("/technical");

    document.getElementById("apiStatus").textContent = "API ONLINE";
    document.getElementById("apiStatus").className = "good";

    document.getElementById("runnerStatus").textContent = runner.running ? "RUNNING" : "STOP";
    document.getElementById("loopCount").textContent = runner.loop_count ?? "-";
    document.getElementById("historyCount").textContent = runner.history ?? "-";
    document.getElementById("winRate").textContent = runner.pnl?.win_rate ?? "-";

    const finalSignal = runner.final_signal || report.final_signal || decision.signal || "-";
    document.getElementById("selectedSymbol").textContent = runner.symbol ?? "-";
    document.getElementById("selectedPrice").textContent = runner.price ?? "-";
    document.getElementById("finalSignal").textContent = finalSignal;
    document.getElementById("finalSignal").className = "signal " + clsSignal(finalSignal);

    document.getElementById("totalScore").textContent = runner.decision_score ?? report.total_score ?? "-";
    document.getElementById("mode").textContent = runner.mode || report.mode || decision.mode || "-";

    document.getElementById("health").textContent = (health.health ?? 0) + "%";
    document.getElementById("health").className = "health " + (health.health >= 90 ? "good" : "bad");
    document.getElementById("okCount").textContent = health.ok ?? "-";
    document.getElementById("totalCount").textContent = health.total ?? "-";

    document.getElementById("cash").textContent = runner.pnl?.cash ?? account.cash ?? "-";
    document.getElementById("equity").textContent = runner.pnl?.equity ?? account.equity ?? "-";
    document.getElementById("pnl").textContent = runner.pnl?.total_pnl ?? account.total_pnl ?? "-";

    document.getElementById("execSignal").textContent = execution.signal ?? "-";
    document.getElementById("execAction").textContent = runner.execution_action ?? execution.action ?? "-";
    document.getElementById("execPositions").textContent = runner.positions ?? execution.positions ?? "-";

    document.getElementById("selectedSymbol").textContent = runner.symbol ?? "-";
    document.getElementById("selectedPrice").textContent = runner.price ?? "-";

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

    const top20 = document.getElementById("top20");
    top20.innerHTML = "";

    (technical.top20 || []).forEach((x, i) => {
        const div = document.createElement("div");

        div.className = "item";

        div.innerHTML =
            "<b>" +
            (i + 1) +
            ". " +
            x.symbol +
            "</b><br>" +
            x.signal +
            " | Score : " +
            x.score +
            "<br>₩ " +
            Number(x.price).toLocaleString();

        top20.appendChild(div);
    });

    document.getElementById("systemBox").textContent = JSON.stringify({
      runner,
      decision,
      execution,
      market: system.market,
      macro: system.macro
    }, null, 2);

    document.getElementById("btnStart").onclick = async () => {
      await fetch(API + "/start", { method: "POST" });
      loadDashboard();
    };

    document.getElementById("btnStop").onclick = async () => {
      await fetch(API + "/stop", { method: "POST" });
      loadDashboard();
    };

  } catch (e) {
    document.getElementById("apiStatus").textContent = "API OFFLINE";
    document.getElementById("apiStatus").className = "bad";
    document.getElementById("systemBox").textContent = String(e);
  }
}

loadDashboard();
setInterval(loadDashboard, 3000);