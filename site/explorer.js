// Render untrusted benchmark answers exclusively as text nodes.
const byId = id => document.getElementById(id);
let data = {rows: [], groups: [], budget: {}};
let filtered = [];
function el(tag, text) {
  const node = document.createElement(tag);
  node.textContent = text;
  return node;
}
function matches(row) {
  return (!byId("phase").value || row.phase === byId("phase").value) &&
    (!byId("domain").value || row.domain === byId("domain").value) &&
    (!byId("method").value || row.arm === byId("method").value);
}

function renderInventory() {
  const body = byId("experiment-rows");
  const filter = byId("experiment-status");
  const selection = filter.value;
  const rows = data.inventory || [];
  const statuses = [...new Set(rows.map(row => row.status))];
  filter.replaceChildren(new Option("All statuses", ""));
  for (const status of statuses) filter.append(new Option(status, status));
  if (statuses.includes(selection)) filter.value = selection;
  body.replaceChildren();
  for (const row of rows) {
    if (filter.value && row.status !== filter.value) continue;
    const tr = el("tr", "");
    for (const value of [row.name, row.kind, row.status, row.done + " / " + (row.planned ?? "pending"), row.purpose]) {
      tr.append(el("td", value));
    }
    body.append(tr);
  }
}

function openLinkedInventory() {
  if (location.hash === "#experiments") byId("experiments").open = true;
}

function renderSizeChart() {
  const phase = byId("size-phase").value;
  const domain = byId("size-domain").value;
  const metric = byId("size-metric").value;
  const groups = (data.size_groups || []).filter(g => g.phase === phase && g.domain === domain);
  const chart = byId("size-chart");
  chart.replaceChildren();
  const caption = byId("size-caption");
  if (!groups.length) {
    caption.textContent = "Awaiting a question scored at all four sizes in this panel.";
    return;
  }
  const quality = metric === "mean";
  const percent = domain === "news";
  const maximum = quality ? (percent ? 1 : 100) : Math.max(...groups.map(g => g[metric]), 0.000001);
  function format(value) {
    if (metric === "cost") return "$" + value.toFixed(4);
    if (metric === "p50") return value.toFixed(1) + " s";
    return percent ? (value * 100).toFixed(1) + "%" : value.toFixed(1);
  }
  const questionCount = groups[0].n;
  caption.textContent = "All four sizes answered the same " + questionCount +
    (questionCount === 1 ? " question. " : " questions. ") +
    (quality ? (percent ? "Strict exact match" : "Rubric score out of 100") + " with 95% intervals." :
     metric === "cost" ? "US dollars per question, excluding grading." : "Elapsed seconds per question.");
  for (const group of groups) {
    const size = Number(group.arm.slice(5));
    const row = el("div", "");
    row.className = "size-row";
    row.append(el("strong", size + (size === 1 ? " agent" : " agents")));
    const track = el("div", "");
    track.className = "size-track";
    track.setAttribute("aria-hidden", "true");
    const bar = el("span", "");
    bar.className = "size-bar";
    bar.style.width = (100 * group[metric] / maximum) + "%";
    track.append(bar);
    if (quality) {
      const interval = el("span", "");
      interval.className = "size-interval";
      interval.style.left = (100 * group.low / maximum) + "%";
      interval.style.width = (100 * (group.high - group.low) / maximum) + "%";
      track.append(interval);
    }
    row.append(track, el("span", format(group[metric]) + (quality ?
      " [" + format(group.low) + ", " + format(group.high) + "]" : "")));
    chart.append(row);
  }
  const axis = el("div", "");
  axis.className = "size-axis";
  axis.append(el("span", format(0)), el("span", format(maximum)));
  chart.append(axis);
}
function details() {
  const row = filtered[Number(byId("example").value)];
  const detail = byId("detail");
  detail.replaceChildren();
  if (!row) return;
  detail.append(el("h3", row.question), el("p", row.answer || row.error), el("p", row.explanation || ""));
  if (row.reference) {
    const reference = el("details","");
    reference.append(el("summary","Reference answer and score"),el("p",row.reference),el("p","Score "+row.score+" / "+(row.domain==="news"?1:100)));
    detail.append(reference);
  }
  for (const c of row.citations || []) {
    detail.append(el("blockquote", c.quote), el("small", c.path + (c.line ? " · line "+c.line : "") + " · " + (c.valid ? "verified text" : "unverified text")));
  }
}
function render() {
  const body = byId("scores");
  body.replaceChildren();
  for (const g of data.groups.filter(matches)) {
    const fmt = x => (g.domain === "news" ? (100*x).toFixed(1)+"%" : x.toFixed(1));
    const tr = el("tr", "");
    const quality = fmt(g.mean)+" ["+fmt(g.low)+", "+fmt(g.high)+"]";
    for (const t of [g.phase,g.domain,g.arm,g.graded+"/"+g.n,quality,g.cost.toFixed(4),g.p50.toFixed(1)+" s",g.completed+"/"+g.requested]) tr.append(el("td", t));
    const bar = el("div", "");
    bar.className = "bar";
    bar.style.width = (g.domain === "news" ? 100*g.mean : g.mean)+"%";
    tr.children[4].append(bar);
    body.append(tr);
  }
  const q = byId("query").value.toLowerCase();
  const previous = filtered[Number(byId("example").value)]?.unit;
  filtered = data.rows.filter(r => matches(r) && (r.question+" "+r.arm+" "+r.id).toLowerCase().includes(q));
  const select = byId("example");
  select.replaceChildren();
  filtered.forEach((r,i) => {
    const o = el("option",r.arm+" · "+r.question);
    o.value = String(i);
    o.selected = r.unit === previous;
    select.append(o);
  });
  details();
}
async function refresh() {
  try {
    const response = await fetch("data.json", {cache:"no-store"});
    if (!response.ok) throw new Error("Measurements unavailable");
    data = await response.json();
    const method = byId("method"), selected = method.value;
    method.replaceChildren(new Option("All methods",""));
    for (const arm of [...new Set(data.rows.map(r=>r.arm))].sort()) method.append(new Option(arm,arm));
    method.value = selected;
    const used = Object.values(data.budget).reduce((a,b)=>a+b,0);
    const cost = data.balances ? "$"+(data.balances.settled||0).toFixed(2)+" settled upper estimate + $"+(data.balances.reserved||0).toFixed(2)+" reserved" : "$"+used.toFixed(2)+" charged or reserved";
    const run = data.operation?.state ? " · "+data.operation.action+" "+data.operation.state.replaceAll("_"," ") : "";
    byId("status").textContent = data.rows.length+" condition runs · "+cost+" of $50"+run+" · updated "+new Date(data.updated).toLocaleString();
    renderInventory();
    renderSizeChart();
    render();
  } catch (e) { byId("status").textContent = e.message; }
  finally {
    if (["127.0.0.1","localhost"].includes(location.hostname)) setTimeout(refresh,20000);
  }
}
for (const id of ["phase","domain","method","query"]) byId(id).addEventListener("input",render);
for (const id of ["size-phase", "size-domain", "size-metric"]) byId(id).addEventListener("change", renderSizeChart);
byId("example").addEventListener("change",details);
byId("experiment-status").addEventListener("change",renderInventory);
window.addEventListener("hashchange",openLinkedInventory);
openLinkedInventory();
refresh();
