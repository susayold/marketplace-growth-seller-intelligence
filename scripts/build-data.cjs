const fs = require('fs');
const path = require('path');

const sourceRoot = 'C:\\Users\\sangk\\Documents\\Codex\\2026-09-12\\che\\outputs\\Marketplace_Growth_Seller_Intelligence_Page1\\data\\release_v3_final\\reports';
const tablesRoot = path.join(sourceRoot, 'tables');
const modelRoot = 'C:\\Users\\sangk\\final market dashboard.SemanticModel\\definition\\tables';
const out = path.join(__dirname, '..', 'dist', 'data.js');

function csv(text) {
  const rows = [];
  let row = [], cell = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i], next = text[i + 1];
    if (ch === '"' && quoted && next === '"') { cell += '"'; i++; continue; }
    if (ch === '"') { quoted = !quoted; continue; }
    if (ch === ',' && !quoted) { row.push(cell); cell = ''; continue; }
    if ((ch === '\n' || ch === '\r') && !quoted) {
      if (ch === '\r' && next === '\n') i++;
      row.push(cell); cell = '';
      if (row.some(v => v !== '')) rows.push(row);
      row = [];
      continue;
    }
    cell += ch;
  }
  if (cell || row.length) { row.push(cell); if (row.some(v => v !== '')) rows.push(row); }
  const headers = rows.shift().map(v => v.trim());
  return rows.map(r => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ''])));
}
function readCsv(rel) { return csv(fs.readFileSync(path.join(tablesRoot, rel), 'utf8')); }
function num(v) { const n = Number(v); return Number.isFinite(n) ? n : 0; }
function pct(v) { return num(v); }
function sum(rows, key) { return rows.reduce((a, r) => a + num(r[key]), 0); }
function round(v, n = 3) { return Number(Number(v).toFixed(n)); }

function splitSourceValue(v) {
  const values = [];
  let token = '', quoted = false;
  for (let i = 0; i < v.length; i++) {
    const ch = v[i], next = v[i + 1];
    if (ch === '"' && next === '"' && quoted) { token += '"'; i++; continue; }
    if (ch === '"') { quoted = !quoted; token += ch; continue; }
    if (ch === ',' && !quoted) { values.push(token.trim()); token = ''; continue; }
    token += ch;
  }
  values.push(token.trim());
  return values.map(x => x.replace(/^"|"$/g, ''));
}
function demoRows(table) {
  const text = fs.readFileSync(path.join(modelRoot, `${table}.tmdl`), 'utf8');
  const line = text.split(/\r?\n/).find(x => x.includes('source = let Source = #table')) || '';
  const schemaStart = line.indexOf('], {{');
  const bodyStart = schemaStart + 4;
  const bodyEnd = line.lastIndexOf('}}) in Source');
  if (schemaStart < 0 || bodyEnd < 0) throw new Error(`Cannot parse ${table}`);
  const schema = line.slice(line.indexOf('[', line.indexOf('#table')) + 1, schemaStart);
  const columns = schema.split(',').map(x => x.trim().split('=')[0]);
  const rows = line.slice(bodyStart, bodyEnd + 1).match(/\{[^{}]+\}/g) || [];
  return rows.map(row => {
    const values = splitSourceValue(row.slice(1, -1));
    return Object.fromEntries(columns.map((c, i) => {
      const value = values[i] ?? '';
      if (/^(true|false)$/i.test(value)) return [c, value.toLowerCase() === 'true'];
      if (value !== '' && /^-?\d+(\.\d+)?$/.test(value)) return [c, Number(value)];
      return [c, value];
    }));
  });
}

const monthly = readCsv('mart_marketplace_monthly.csv').map(r => ({
  month: r.purchase_month, gmv: num(r.gmv_proxy), orders: num(r.orders), sellers: num(r.active_sellers),
  aov: num(r.aov), lateRate: num(r.late_delivery_rate), review: num(r.avg_review_score)
}));
const health = readCsv('marketplace_health_extended.csv');
const completeMonths = health.filter(r => /^true$/i.test(r.is_complete_month)).map(r => r.month);
const complete = monthly.filter(r => completeMonths.includes(r.month));
const latest = complete[complete.length - 1];
const previous = complete[complete.length - 2];
const sellerCount = readCsv('seller_segmentation.csv').length;
const totalGmv = sum(monthly, 'gmv');
const totalOrders = sum(monthly, 'orders');
const allDelivery = readCsv('delivery_performance.csv');
const delivered = sum(allDelivery, 'orders');
const lateOrders = num(allDelivery.find(r => r.is_late === '1')?.orders);
const categories = readCsv('mart_category_performance.csv').filter(r => r.purchase_month === latest.month)
  .map(r => ({ name: r.product_category_name_english.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()), value: num(r.gmv_proxy) }))
  .sort((a, b) => b.value - a.value).slice(0, 5);
const states = readCsv('mart_geography_performance.csv').map(r => ({
  state: r.seller_state, sellers: num(r.active_sellers), gmv: num(r.gmv_proxy), share: pct(r.gmv_share)
})).sort((a, b) => b.gmv - a.gmv).slice(0, 5);
const lorenz = readCsv('pareto_seller_curve.csv').map(r => ({ x: pct(r.cumulative_seller_share), y: pct(r.cumulative_gmv_share) }))
  .filter((_, i, a) => i % Math.max(1, Math.floor(a.length / 90)) === 0).slice(0, 90);
const concentration = readCsv('seller_concentration.csv');

const data = {
  source: { label: 'Power BI project source tables', latestCompleteMonth: latest.month },
  pages: {
    overview: {
      months: complete.map(r => ({ label: r.month, gmv: r.gmv / 1000000, orders: r.orders / 1000, sellers: r.sellers, aov: r.aov, lateRate: r.lateRate })),
      kpis: {
        gmv: totalGmv / 1000000, orders: totalOrders / 1000, sellers: sellerCount,
        aov: totalGmv / totalOrders, lateRate: lateOrders / delivered,
        deltas: {
          gmv: previous ? (latest.gmv - previous.gmv) / previous.gmv : null,
          orders: previous ? (latest.orders - previous.orders) / previous.orders : null,
          sellers: previous ? (latest.sellers - previous.sellers) / previous.sellers : null,
          aov: previous ? (latest.aov - previous.aov) / previous.aov : null,
          lateRate: previous ? (latest.lateRate - previous.lateRate) : null
        }
      }, categories, states, lorenz, concentration
    },
    acquisition: { rows: demoRows('DemoAcquisition') },
    activation: { rows: demoRows('DemoActivation') },
    commercial: { rows: demoRows('DemoCommercial') },
    customer: { rows: demoRows('DemoCustomerOps') },
    root: { rows: demoRows('DemoRootCause') },
    decision: { rows: demoRows('DemoDecision') }
  }
};
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, `window.MARKETLENS_DATA = ${JSON.stringify(data)};\n`, 'utf8');
console.log(`Wrote ${out}`);
