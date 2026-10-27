# CloudOps AI Assistant

FastAPI 기반 클라우드 장애 분석 학습용 MVP입니다.

## 구현 기능

- 정상, API 오류, DB 연결 실패, Redis 큐 적체 시나리오
- 규칙 기반 진단과 점검 순서
- OpenAI 모델의 선택적 설명 생성
- FastAPI 및 pytest 테스트
- /docs 의 API 테스트 인터페이스
- / 에서 시나리오별 진단 결과·로그·상태 지표를 확인하는 웹 화면

## 로컬 실행

Python 3.10 이상을 사용합니다.

1. Install: python -m pip install -r requirements.txt
2. Start: python -m uvicorn main:app --port 8501
3. Open: http://127.0.0.1:8501/ (웹 데모) 또는 /docs (API 명세)
4. Test: POST /api/analyze with scenario database, api, queue, or healthy
5. Tests: python -m pytest -q

## 실행 범위 및 비용

기본 로컬 규칙 기반 진단은 무료입니다. 유료 API 호출 없이 동작합니다. 선택적으로 OpenAI API를 호출하려면 별도 설정과 사용량에 따른 비용이 발생할 수 있습니다. AWS 환경은 이 버전에서 프로비저닝하지 않습니다.

장애 시나리오는 가상 데이터로 구성되어 있으며, 실제 클라우드 시스템에 접속하거나 장애를 자동 복구하지 않습니다.
