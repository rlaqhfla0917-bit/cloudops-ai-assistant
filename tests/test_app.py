from fastapi.testclient import TestClient
from main import app, diagnose
c=TestClient(app)

def test_health(): assert c.get("/api/health").json()["status"]=="ok"
def test_dashboard(): assert c.get("/").status_code==200
def test_dashboard_controls():
 html=c.get("/").text
 for scenario in ("healthy","api","database","queue"):
  assert 'data-scenario="'+scenario+'"' in html
 assert 'id="report"' in html and 'id="metrics"' in html
 script=c.get("/dashboard.js")
 assert script.status_code==200
 assert "javascript" in script.headers["content-type"]
def test_api(): assert c.post("/api/analyze",json={"scenario":"api"}).json()["severity"]=="high"
def test_database(): assert diagnose("database")["severity"]=="critical"
def test_queue(): assert "248" in str(diagnose("queue")["metrics"])
def test_healthy(): assert diagnose("healthy")["severity"]=="normal"
def test_bad_input(): assert c.post("/api/analyze",json={"scenario":"fake"}).status_code==400
def test_offline_is_not_ai(monkeypatch):
 monkeypatch.delenv("AI_MODE",raising=False)
 assert diagnose("database")["llm_status"]=="offline_rules"
def test_missing_key(monkeypatch):
 monkeypatch.setenv("AI_MODE","openai")
 monkeypatch.delenv("OPENAI_API_KEY",raising=False)
 assert diagnose("api")["llm_status"]=="missing_api_key"
