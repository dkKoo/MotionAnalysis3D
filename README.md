# SarcoCoach — 시니어 근감소증 홈 재활 AI 코치 설계서

> **버전**: 1.1 (개정) | **최종 수정**: 2026-02-08  \
> **용도**: AI Agent가 바로 개발을 시작할 수 있는 실행형 설계서  \
> **프로젝트 코드명**: `SarcoCoach`

---

## 변경 요약 (1.1)
- **목적 정렬**: 임상 안전(낙상 위험)과 운영 안정성(오프라인 우선)을 설계 최상위 원칙으로 승격.
- **아키텍처 단순화**: MVP는 MediaPipe 중심으로 시작하고, 고정밀 추정은 **옵션 모듈**로 단계적 통합.
- **데이터 설계 강화**: 개인정보 최소화 + 이벤트/세션 분리로 장기 분석과 리포트 생성 안정화.
- **운영 확장성**: 비디오/리포트 저장은 **S3 호환(MinIO)** 기반으로 명시.

---

## 1. 시스템 개요

### 1.1 목적
단일 웹캠/스마트폰 카메라를 사용해 실시간 3D 포즈를 추정하고, AWGS 2025 기준의 근감소증 선별·재활 코칭·낙상 위험 예측·가족/보호자 모니터링을 통합 제공하는 **홈 재활 AI 코치**를 구축한다.

### 1.2 핵심 가치
- **안전 최우선**: 낙상 감지에서 false negative보다 false positive를 허용.
- **오프라인 우선**: 네트워크 없이도 세션 진행 가능, 알림은 온라인 복구 시 전송.
- **한국어 기본**: 모든 피드백·리포트·UI는 한국어 우선.

### 1.3 타겟 사용자
- **Primary**: 50세 이상 근감소증 위험군 (홈 재활)
- **Secondary**: 가족/보호자 (대시보드 모니터링)
- **Tertiary**: 의료진/복지관 담당자 (PDF 리포트 활용)

---

## 2. 기술 스택

### 2.1 Backend
- **Python 3.11+**, **FastAPI**, **SQLAlchemy 2.0 + Alembic**
- **PostgreSQL 16+**, **Redis 7+**, **Celery + Redis**
- 인증: **JWT + OAuth2**

### 2.2 AI / Pose Estimation
- **MediaPipe Pose (MVP)**
- **MotionAGFormer** (Phase 2, 2D→3D lifting)
- **RTMPose** (2D fallback, occlusion 보강)
- **One-Euro Filter**, **ROM/Balance/Gait 분석기**

### 2.3 Frontend
- **Streamlit (MVP)**
- **Next.js 15 + React 19 (Phase 2 Dashboard)**
- **Flutter (Phase 3 Mobile)**

### 2.4 Infra
- Docker + docker-compose
- MinIO (S3 호환 스토리지)
- Firebase Cloud Messaging (알림)

---

## 3. 프로젝트 구조 (MVP 기준)

```
sarcocoach/
├── backend/
│   ├── api/               # REST API
│   ├── core/              # Security/Permissions
│   ├── models/            # ORM
│   ├── schemas/           # Pydantic
│   ├── services/          # 비즈니스 로직
│   ├── db/                # DB session/base
│   └── tasks/             # Celery tasks
├── pose_engine/
│   ├── estimators/
│   ├── analyzers/
│   ├── predictors/
│   ├── filters/
│   └── pipeline.py
├── protocol_engine/       # AWGS 2025 로직
├── report_generator/      # PDF 생성
├── notification/          # FCM/WebSocket
├── streamlit_app/         # MVP UI
└── dashboard/             # Next.js (Phase 2)
```

---

## 4. 아키텍처 설계

### 4.1 전체 구조
- **클라이언트**(Streamlit/Next.js/Flutter) → **FastAPI Gateway**
- FastAPI가 **Pose Engine**과 **서비스 레이어**를 호출
- **Redis + Celery**로 비동기 처리 (PDF, 비디오 분석)
- **MinIO**에 리포트·영상 저장

### 4.2 포즈 파이프라인
1. **MediaPipe Pose**로 3D 추정
2. 신뢰도 < 0.6 시 **RTMPose → MotionAGFormer**로 2D→3D 보강
3. One-Euro Filter 스무딩
4. ROM/Balance/Gait/Chair Stand 분석
5. 낙상 위험 예측 → 알림

---

## 5. 데이터 모델 (요약)

### 핵심 엔티티
- **User** (환자/보호자/의료진)
- **PatientProfile** (신체 정보 + AWGS 평가 데이터)
- **RehabSession** (세션 메트릭)
- **PoseFrame** (샘플링 3D 포즈)
- **FallRiskEvent** (낙상 이벤트)
- **Assessment** (AWGS 평가 결과)
- **Report** (PDF 리포트)

### 데이터 설계 원칙
- **PII 최소화**: 불필요한 개인정보 저장 금지
- **세션 요약/이벤트 분리**: 분석과 알림 성능 분리

---

## 6. 모듈별 상세 명세 (요약)

### 6.1 Pose Engine
- **Estimator**: MediaPipeEstimator (MVP), MotionAGFormerEstimator (Phase 2)
- **Analyzers**: ROMAnalyzer, BalanceAnalyzer, ChairStandAnalyzer, GaitAnalyzer
- **Predictor**: FallRiskPredictor (CoM 기반 위험 점수)
- **Pipeline**: Frame 단위 추정/분석/피드백 생성

### 6.2 Protocol Engine
- **AWGS2025Screener**: 50+ 확장, 근력 기준 필수

### 6.3 Notification
- WebSocket 실시간 메시지
- FCM 푸시 알림

### 6.4 Report Generator
- HTML → PDF (WeasyPrint)
- 세션 리포트 + 임상 리포트

---

## 7. REST API (요약)

### 인증
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/fcm-token`

### 세션
- `POST /api/v1/sessions`
- `PUT /api/v1/sessions/{id}`
- `POST /api/v1/sessions/{id}/complete`

### 평가
- `POST /api/v1/assessments`
- `GET /api/v1/assessments/latest`

### 리포트
- `POST /api/v1/reports/generate`
- `GET /api/v1/reports/{id}/download`

---

## 8. Phase별 구현 로드맵

### Phase 1 (MVP Core)
- MediaPipe 기반 추정 + ROM/Balance 분석
- AWGS 2025 스크리너
- Streamlit UI
- 기본 PDF 리포트

### Phase 2 (가족/보호자 연동)
- Next.js 대시보드
- WebSocket/FCM 알림
- MotionAGFormer 통합

### Phase 3 (고도화)
- Gait 분석 강화
- 모바일 앱(Flutter)
- 임상 파일럿 데이터 연동

---

## 9. AI Agent 구현 가이드

- 타입 힌트 필수, PEP8 + Black
- API/모듈부터 기능 단위로 점진 구현
- 안전성 최우선 (낙상 경고 과다 허용)

---

## 10. 부록: AWGS 2025 핵심 기준 (요약)

| 항목 | 남성 (65+) | 여성 (65+) | 남성 (50-64) | 여성 (50-64) |
|------|-----------|-----------|-------------|-------------|
| 종아리 둘레 | < 34cm | < 33cm | 연구 중 | 연구 중 |
| 악력 | < 28kg | < 18kg | < 28kg | < 18kg |
| 보행 속도* | < 1.0 m/s | < 1.0 m/s | - | - |
| 5-CST* | ≥ 12초 | ≥ 12초 | - | - |
| SPPB* | ≤ 9점 | ≤ 9점 | - | - |

*Outcome measure로 활용 (진단 기준 아님)
