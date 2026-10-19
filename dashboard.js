async function diagnose(scenario) {
  const response = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({scenario})});
  const result = await response.json();
  document.querySelector('#status').textContent = result.incident + ' · ' + result.severity + ' · ' + result.llm_status;
  document.querySelector('#report').textContent = result.answer;
  document.querySelector('#logs').textContent = result.logs.join('\n');
}