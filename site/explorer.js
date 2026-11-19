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
    byId("status").textContent = data.rows.length+" condition runs · "+cost+" of $50 · updated "+new Date(data.updated).toLocaleString();
    render();
  } catch (e) { byId("status").textContent = e.message; }
}
for (const id of ["phase","domain","method","query"]) byId(id).addEventListener("input",render);
byId("example").addEventListener("change",details);
refresh();
if (["127.0.0.1","localhost"].includes(location.hostname)) setInterval(refresh,20000);
