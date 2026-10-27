"""CloudOps read-only incident assistant. Default OFFLINE; no API charges."""
from __future__ import annotations
import os, re
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="CloudOps AI Assistant", version="1.0")
SCENARIOS = {
 "healthy": {"label": "정상 운영", "api_status": 200, "db_connected": True, "queue_depth": 2, "logs": ["INFO /health 200", "INFO database connected"]},
 "api": {"label": "API 오류", "api_status": 503, "db_connected": True, "queue_depth": 4, "logs": ["ERROR upstream timeout", "ERROR /health 503"]},
 "database": {"label": "DB 연결 실패", "api_status": 200, "db_connected": False, "queue_depth": 3, "logs": ["ERROR psycopg2 connection timed out", "WARN fallback active"]},
 "queue": {"label": "Redis 큐 적체", "api_status": 200, "db_connected": True, "queue_depth": 248, "logs": ["WARN reservation_queue depth=248 threshold=100"]},
}
RUNBOOKS = {
 "healthy": ("일상 모니터링", ["최근 오류 로그 확인", "모니터링 범위 및 임계값 확인"]),
 "api": ("API 장애 대응", ["오류 시작 시점과 HTTP 상태 확인", "DB·Redis와 연관성 확인", "최근 배포 기록 확인"]),
 "database": ("DB 장애 대응", ["DB 엔드포인트 확인", "RDS 상태와 보안그룹 확인", "연결 실패 시 fallback 확인"]),
 "queue": ("큐 적체 대응", ["Redis 큐 깊이 변화 확인", "Worker 실행 상태 확인", "입력량과 처리량 추세 비교"]),
}
class Analyze(BaseModel):
 scenario: str = "database"
def diagnose(scenario: str) -> dict:
 if scenario not in SCENARIOS: raise ValueError("존재하지 않는 시나리오")
 s = SCENARIOS[scenario]
 if s["db_connected"] is False: code,severity="database","critical"
 elif s["api_status"] >= 500: code,severity="api","high"
 elif s["queue_depth"] >= 100: code,severity="queue","high"
 else: code,severity="healthy","normal"
 name, steps = RUNBOOKS[code]
 evidence = "\n".join(s["logs"])
 base = f"진단: {name} ({severity})\n관측 근거:\n{evidence}\n점검 순서:\n" + "\n".join(f"{i+1}. {v}" for i,v in enumerate(steps))
 output, model, status = base, None, "offline_rules"
 if os.getenv("AI_MODE","offline") == "openai":
  key=os.getenv("OPENAI_API_KEY")
  if not key:
   status="missing_api_key"
  else:
   try:
    from openai import OpenAI
    model=os.getenv("OPENAI_MODEL","gpt-4o-mini")
    response=OpenAI(timeout=12,max_retries=0).responses.create(model=model,
      input=[{"role":"system","content":"클라우드 운영 보조자입니다. 제공된 근거만 사용하고 장애 원인을 확정하지 마세요. 한국어로 답하며 읽기 전용 점검 순서만 제안하세요."},
             {"role":"user","content":base}], max_output_tokens=500)
    candidate=(response.output_text or "").strip()
    if not candidate: raise ValueError("empty response")
    output=candidate
    status="openai_response"
   except Exception:
    status="openai_call_failed"
 return {"source":"fixture","scenario":scenario,"severity":severity,"incident":name,
         "llm_status":status,"llm_model":model,"answer":output,"rule_based_report":base,
         "logs":s["logs"],"metrics":{"api_status":s["api_status"],"db_connected":s["db_connected"],"queue_depth":s["queue_depth"]},
         "runbook":{"title":name,"checks":steps},"warning":"모의 장애 분석 결과이며 실측 성능이 아닙니다."}
@app.get("/api/health")
def health(): return {"status":"ok","ai_mode":os.getenv("AI_MODE","offline")}
@app.get("/api/scenarios")
def scenarios(): return [{"id":k,"label":v["label"]} for k,v in SCENARIOS.items()]
@app.post("/api/analyze")
def analyze(req: Analyze):
 try: return diagnose(req.scenario)
 except ValueError as err: raise HTTPException(400,str(err))
@app.get("/", response_class=HTMLResponse)
def dashboard(): return (Path(__file__).parent/"index.html").read_text(encoding="utf-8")
@app.get("/dashboard.js", include_in_schema=False)
def dashboard_script(): return FileResponse(Path(__file__).parent/"dashboard.js", media_type="text/javascript")
