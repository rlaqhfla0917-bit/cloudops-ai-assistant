const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function loadDashboard(fetchImpl) {
  const nodes = Object.fromEntries(['#status', '#report', '#logs', '#metrics'].map(id => [id, {textContent: ''}]));
  const buttons = ['healthy', 'api', 'database', 'queue'].map(scenario => ({
    dataset: {scenario}, disabled: false, pressed: 'false',
    setAttribute(name, value) { if (name === 'aria-pressed') this.pressed = value; },
    addEventListener() {}
  }));
  const document = {
    querySelector(selector) { return nodes[selector]; },
    querySelectorAll() { return buttons; },
    addEventListener() {}
  };
  const context = vm.createContext({document, fetch: fetchImpl});
  const source = fs.readFileSync(path.join(__dirname, '..', 'dashboard.js'), 'utf8');
  vm.runInContext(source, context);
  return {diagnose: context.diagnose, nodes, buttons};
}

test('diagnosis displays grounded status, report, logs and metrics', async () => {
  const dashboard = loadDashboard(async () => ({
    ok: true, json: async () => ({
      incident: 'API 장애 대응', severity: 'high', llm_status: 'offline_rules',
      answer: '점검 순서', logs: ['ERROR timeout'], metrics: {api_status: 503, db_connected: true, queue_depth: 4}
    })
  }));
  await dashboard.diagnose('api');
  assert.match(dashboard.nodes['#status'].textContent, /API 장애 대응/);
  assert.equal(dashboard.nodes['#report'].textContent, '점검 순서');
  assert.equal(dashboard.nodes['#logs'].textContent, 'ERROR timeout');
  assert.match(dashboard.nodes['#metrics'].textContent, /HTTP 상태: 503/);
  assert.equal(dashboard.buttons.find(b => b.dataset.scenario === 'api').pressed, 'true');
  assert(dashboard.buttons.every(b => !b.disabled));
});

test('API errors are visible and controls recover', async () => {
  const dashboard = loadDashboard(async () => ({ok: false, status: 503}));
  await dashboard.diagnose('database');
  assert.match(dashboard.nodes['#status'].textContent, /실패/);
  assert.match(dashboard.nodes['#report'].textContent, /503/);
  assert(dashboard.buttons.every(b => !b.disabled));
});
