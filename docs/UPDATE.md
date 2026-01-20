# Bitcoin Ticker - Update Log

## v1.2.0 (2026-01-18)

### 🗑️ Removed Features

#### Vertical Mode 제거
- 세로 모드 레이아웃 완전 제거
- 가로 모드만 지원 (고정)
- 설정 다이얼로그에서 "Layout Mode" 옵션 제거

### 🔧 Code Changes

- `settings_dialog.py`:
  - `layout_mode` 매개변수 제거
  - Layout Mode 콤보박스 제거
  - 다이얼로그 높이 축소 (260 → 220)
- `main_window.py`:
  - `update_layout_mode()` → `setup_layout()` 변경
  - 세로 모드 관련 코드 전체 제거
  - `layout_mode` 변수 제거
- `settings_manager.py`:
  - `DEFAULT_SETTINGS`에서 `layout_mode` 제거

---

## v1.1.0 (2026-01-18)

### 🆕 New Features

#### Mute Button
- **Interval 라벨 제거**: 기존 "Interval: $50" 라벨 삭제
- **Mute 버튼 추가**: 🔊 / 🔇 아이콘으로 TTS 음소거 토글
- **설정 저장**: Mute 상태가 `settings.json`에 저장됨

### 🔧 Changes

#### UI 변경
| 기존 | 변경 |
|------|------|
| `[Connected] [Interval: $50] [⚙️] [✕]` | `[Connected] [🔊] [⚙️] [✕]` |

#### 코드 변경
- `main_window.py`:
  - `interval_label` 제거
  - `mute_btn` 추가 (QPushButton)
  - `toggle_mute()` 메서드 추가
  - `on_interval_crossed()`에 mute 체크 추가
- `settings_manager.py`:
  - `DEFAULT_SETTINGS`에 `"muted": False` 추가

---

## v1.0.0 (2026-01-17)

### 🎉 Initial Release

#### Core Features
- 실시간 비트코인 가격 모니터링 (Binance WebSocket)
- TTS 음성 알림 (Supertonic AI, 5개국어)
- 가격 변동 인디케이터 (▲/▼)

#### UI Features
- 다크 테마, 프레임리스 창
- 가로 모드 레이아웃 (520×110px)
- 플립 클럭 위젯 (시간, AM/PM, 날짜)
- Always on Top 토글

#### Settings
- 인터벌 설정 (가격 변동 임계값)
- 음성 선택 (F1-F5, M1-M5)
- 언어 선택 (Korean, English, Spanish, Portuguese, French)
- JSON 기반 설정 저장

#### Technical
- Windows DPI 스케일링 지원
- 한글 숫자 변환 (TTS 발음 최적화)
- TTS 에러 시각적 피드백
- 오디오 캐싱

---

## Roadmap (Future)

- [ ] 시스템 트레이 지원
- [ ] 다중 암호화폐 지원 (ETH, etc.)
- [ ] 알림 히스토리
- [ ] 커스텀 알림 메시지 템플릿
