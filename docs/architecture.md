# System Architecture

## Overview
Bitcoin Ticker는 실시간 비트코인 가격 모니터링과 음성 알림을 제공하는 모듈형 데스크톱 애플리케이션입니다.
Core Logic, Services, UI, Utils 계층으로 분리된 클린 아키텍처를 따릅니다.

## Component Diagram

```mermaid
graph TD
    User[User] --> UI[MainWindow (PyQt6)]
    UI --> Settings[SettingsDialog]
    UI --> Clock[ClockWidget]
    
    subgraph "Core Logic"
        PM[PriceMonitor] -- WebSocket --> Binance[Binance API]
        IT[IntervalTracker] -- Signals --> UI
    end
    
    subgraph "Services"
        TTS[TTSService] -- Audio --> Speaker
        Helper[Helper (ONNX Inference)] -- Models --> TTS
        Cache[Audio Cache] <--> TTS
    end
    
    subgraph "Utils"
        SM[SettingsManager] -- JSON --> Storage[settings.json]
        KN[KoreanNumbers] --> TTS
    end
    
    PM -- Price Update --> IT
    PM -- Price Update --> UI
    IT -- Interval Crossed --> UI
    UI -- Trigger TTS --> TTS
    UI -- Load/Save --> SM
    TTS -- Error Signal --> UI
```

## Key Modules

### 1. Entry Point (`src/main.py`)
- Windows DPI 처리 (ctypes.SetProcessDpiAwareness)
- Qt 환경 변수 설정 (QT_SCALE_FACTOR)
- QApplication 초기화

### 2. User Interface (`src/ui/`)
- **`MainWindow`**: 메인 컨트롤러
  - 프레임리스 창, 드래그 지원
  - Vertical/Horizontal 레이아웃 전환
  - TTS 에러 시각적 피드백
  - 가격 변동 인디케이터 (▲/▼)
- **`ClockWidget`**: 플립 클럭 위젯 (시간, AM/PM, 날짜)
- **`SettingsDialog`**: 설정 다이얼로그 (인터벌, 음성, 언어, 레이아웃, Always on Top)

### 3. Core Logic (`src/core/`)
- **`PriceMonitor`**: QThread 기반 WebSocket 워커
  - Binance 실시간 가격 수신
  - 연결 상태 시그널 발행
- **`IntervalTracker`**: 가격 임계값 감지 로직
  - 사용자 정의 인터벌 (예: $50) 크로싱 감지
  - UP/DOWN 방향 판별

### 4. Services (`src/services/`)
- **`TTSService`**: Text-to-Speech 서비스
  - 멀티 스레드 오디오 생성
  - 파일 기반 캐싱
  - 에러 시그널 (tts_error)
- **`helper.py`**: ONNX 추론 엔진
  - Supertonic 모델 로딩
  - 다국어 텍스트 처리 (ko, en, es, pt, fr)
  - 음성 스타일 적용

### 5. Utils (`src/utils/`)
- **`SettingsManager`**: JSON 기반 설정 관리
  - 기본값, 로드, 저장, 업데이트
  - LANG_CODE_MAP 공유 상수
- **`korean_numbers.py`**: 숫자 → 한글 변환
  - TTS 발음 최적화 (95500 → "구만 오천오백")

## Data Flow

1. **Price Update**: `PriceMonitor`가 Binance에서 JSON 수신 → `price_updated(float)` 발행
2. **UI Update**: `MainWindow`가 `price_label` 업데이트, 인디케이터 표시
3. **Logic Check**: `IntervalTracker`가 임계값 크로싱 감지 → `interval_crossed(price, direction)` 발행
4. **Notification**: `MainWindow`가 시그널 수신 → `tts_service.speak()` 호출
5. **Audio Generation**:
   - 캐시 확인: 텍스트+음성 조합의 오디오 존재 시 로드
   - 추론: 없으면 `helper.py` → ONNX Model → Audio Array
   - 저장: 생성된 오디오를 `cache/`에 저장
6. **Playback**: QMediaPlayer로 오디오 재생
7. **Error Handling**: TTS 실패 시 `tts_error` 시그널 → UI에서 빨간 상태 표시

## File Structure

```
bittalker/
├── src/
│   ├── main.py              # Entry point (DPI handling)
│   ├── core/
│   │   ├── price_monitor.py # WebSocket client
│   │   └── interval_logic.py # Threshold detection
│   ├── services/
│   │   ├── tts_service.py   # TTS wrapper
│   │   └── helper.py        # ONNX inference
│   ├── ui/
│   │   ├── main_window.py   # Main UI
│   │   ├── clock_widget.py  # Clock component
│   │   └── settings_dialog.py
│   └── utils/
│       ├── settings_manager.py # Settings persistence
│       └── korean_numbers.py   # Number to Korean
├── assets/                  # ONNX models & voice styles
├── cache/                   # Generated audio cache
├── docs/                    # Documentation
├── tests/                   # Unit tests
├── settings.json            # User settings
└── requirements.txt
```
