async function diagnose(scenario) {
  const buttons = [...document.querySelectorAll('[data-scenario]')];
  const status = document.querySelector('#status');
  const report = document.querySelector('#report');
  const logs = document.querySelector('#logs');
  const metrics = document.querySelector('#metrics');
  buttons.forEach(button => {
    button.disabled = true;
    button.setAttribute('aria-pressed', String(button.dataset.scenario === scenario));
  });
  status.textContent = '분석 중...';
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({scenario})
    });
    if (!response.ok) throw new Error('분석 API 오류 (' + response.status + ')');
    const result = await response.json();
    status.textContent = result.incident + ' · ' + result.severity + ' · ' + result.llm_status;
    report.textContent = result.answer;
    logs.textContent = result.logs.join('\n');
    metrics.textContent = [
      'HTTP 상태: ' + result.metrics.api_status,
      'DB 연결: ' + (result.metrics.db_connected ? '정상' : '실패'),
      '큐 대기: ' + result.metrics.queue_depth
    ].join('\n');
  } catch (error) {
    status.textContent = '분석 요청에 실패했습니다.';
    report.textContent = error.message;
    logs.textContent = '-';
    metrics.textContent = '-';
  } finally {
    buttons.forEach(button => { button.disabled = false; });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-scenario]').forEach(button => {
    button.addEventListener('click', () => diagnose(button.dataset.scenario));
  });
});
