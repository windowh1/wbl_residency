# Extended Agent

이 프로젝트는 다음과 같은 기능을 가진 유연한 Claude 에이전트를 구현합니다:
- 확장된 기능을 위한 다중 MCP 서버 연결
- Anthropic Skills API 통합
- Code execution 환경에서 MCP 도구 접근

## 프로젝트 구조

```
extended_agent/
├── main.py                     # 에이전트 실행 메인 스크립트
├── skill_creation_agg.py       # 여러 세션 통합하여 스킬 생성
├── config.json                 # 설정 파일 (API 키, MCP 서버 등)
├── requirements.txt            # Python 의존성
├── claude_agent/               # 핵심 에이전트 구현
│   ├── agent.py                  # 메인 ClaudeAgent 클래스
│   ├── custom_skills.py          # 커스텀 스킬 관리
│   ├── code_execution.py         # Code execution 환경
│   ├── file_download.py          # 파일 다운로드 유틸리티
│   └── prompts.py                # 프롬프트 템플릿
├── mcp_server/                 # MCP 클라이언트 및 프록시
│   ├── client.py                 # MCP 클라이언트 구현
│   ├── http_proxy.py             # Code execution용 HTTP 프록시
│   └── wrapper.py                # MCP 도구 래퍼 생성기
├── extensions/                 # 확장 기능 및 통합
│   ├── mcp/                      # MCP 서버 구현
│   ├── skills/                   # 커스텀 스킬 정의
│   └── wrapped_mcp/              # Code execution용 MCP 래퍼
├── results/                    # 에이전트 실행 결과
└── workspaces/                 # Code execution 워크스페이스
```

## 주요 기능

### 1. MCP 서버 통합
- stdio 및 SSE 기반 MCP 서버 지원
- Code execution 모드를 위한 HTTP 프록시
- 사용 중인 서버:
  - `mcp-server-search`: 웹 검색 (DuckDuckGo/Brave/Serper)
  - `mcp-server-fetch`: URL 콘텐츠 가져오기
  - `desktop-commander`: 파일 시스템 및 프로세스 관리

### 2. Skills API 지원
- 로컬 폴더의 커스텀 스킬 등록
- Anthropic 내장 스킬 사용
- 대화 기록으로부터 자동 스킬 생성

### 3. Code execution
- 독립 프로세스에서 Python 코드 실행
- Code execution 환경에서 MCP 도구 접근
- 세션별 워크스페이스 격리

---

## 설치 및 설정

### 설치

```bash
# 가상환경 생성 및 활성화
uv venv
source .venv/bin/activate

# 의존성 설치
uv pip install -r requirements.txt
```

### 설정

`config.json` 파일을 편집하여 다음 항목을 설정:

**API Keys:**
- `claude.api_key`: Anthropic API 키 (필수)
- `BRAVE_API_KEY`: Brave Search API 키 (선택)
- `SERPER_API_KEY`: Serper API 키 (선택)

**Code Execution:**
- `code_execution.enabled`: Code execution 모드 활성화 여부
- `code_execution.host`: HTTP 프록시 호스트 (default: "localhost")
- `code_execution.port`: HTTP 프록시 포트 (default: 8082)

**Skills & MCP:**
- `create_new_skill`: 대화 후 자동 스킬 생성 여부
- `mcp_servers`: 사용할 MCP 서버 목록
- `skills`: 사용할 Skills 목록

---

## 사용 방법

### 기본 실행

```bash
python main.py
```

에이전트는 다음 작업을 수행합니다:
1. 설정 로드 및 MCP 서버 연결
2. 커스텀 스킬 등록
3. 사용자 프롬프트 실행
4. 결과를 `results/{timestamp}/`에 저장
5. 생성된 파일 자동 다운로드

---

### Code execution 모드 사용

Code execution 모드로  에이전트를 실행하려면, 먼저 MCP 도구를 Python 함수로 래핑해야 합니다:

```bash
# mcp-server-search 래핑
python mcp_server/wrapper.py \
    --server-name mcp-server-search \
    --transport stdio \
    --command python \
    --args '["extensions/mcp/mcp-server-search/search.py"]'

# mcp-server-fetch 래핑
python mcp_server/wrapper.py \
    --server-name mcp-server-fetch \
    --transport stdio \
    --command uvx \
    --args '["mcp-server-fetch"]'

# desktop-commander 래핑
python mcp_server/wrapper.py \
    --server-name desktop-commander \
    --transport stdio \
    --command npx \
    --args '["-y", "@wonderwhy-er/desktop-commander@latest"]'
```

래핑 완료 후 에이전트를 실행합니다.

---

### 여러 세션 통합하여 스킬 생성

```bash
python skill_creation_agg.py \
    --session-ids '["20251114_151727", "20251114_151329"]'
```

여러 대화 세션을 분석하여 공통 패턴을 추출하고 새로운 스킬을 생성합니다.

---

### Code execution 모드 테스트

직접 MCP 도구 호출 방식과 코드 실행을 통한 간접 호출 방식을 비교 테스트합니다:

```bash
python code_execution_test.py
```

---

## Code Execution with MCP 구현 상세

### 동작 흐름

#### **모드 1: Code execution 비활성화 (MCP 직접 연결)**

```
Claude Agent ──(MCP Protocol)──> MCP Server
```

- 메인 프로세스가 MCP 서버와 직접 stdio/SSE 통신
- Claude가 생성한 `tool_use` 블록을 Agent가 직접 실행

#### **모드 2: Code execution 활성화**

```
Claude Agent ──(생성)──> Python Script ──(subprocess)──> 실행
                                              │
                                              └──(HTTP)──> HTTP Proxy
                                                              │
                                                              └──(stdio)──> MCP Server
```

1. **스크립트 생성**: Claude가 Python 코드 블록 생성
2. **스크립트 실행**: [`claude_agent/code_execution.py`](claude_agent/code_execution.py)의 `subprocess.run()`으로 실행
3. **HTTP 호출**: 스크립트가 `httpx`로 프록시 서버 호출
4. **프록시 중계**: HTTP 프록시가 stdio MCP 서버로 요청 전달
5. **결과 반환**: MCP Server → Proxy → Script → Claude Agent 순으로 결과 전달

**왜 HTTP 프록시가 필요한가?**

Code execution 모드의 Python 스크립트는 **격리된 subprocess**로 동작하며, stdio 기반 MCP 서버에 직접 접근할 수 없습니다. HTTP 프록시가 메인 프로세스와 MCP 서버 간 연결을 유지하면서 격리된 스크립트의 요청을 중계합니다.

---

### MCP 도구 래퍼

[`mcp_server/wrapper.py`](mcp_server/wrapper.py)는 각 MCP 도구를 **Python 함수로 자동 변환**합니다. 에이전트가 생성하는 코드에서 이 함수를 import하여 사용할 수 있습니다.

**자동 생성된 래퍼 예시:**

```python
async def web_search(params: Dict[str, Any]) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{PROXY_URL}/mcp/{SERVER_NAME}/call_tool",
                params={"tool_name": TOOL_NAME},
                json=params
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result.get("result", "")
            else:
                raise RuntimeError(f"Tool call failed: {result}")
                
        except httpx.TimeoutException:
            raise RuntimeError(f"Timeout calling {TOOL_NAME}")
        except httpx.HTTPError as e:
            raise RuntimeError(f"HTTP error calling {TOOL_NAME}: {e}")
```

**에이전트 사용 예시:**

```python
# Claude가 생성하는 코드
import asyncio
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    results = await web_search({
        "query": "Python async programming",
        "max_results": 10
    })
    print(results)

asyncio.run(main())
```

**래퍼 생성 및 사용 흐름:**

```
1. 래퍼 생성: python mcp_server/wrapper.py --server-name ...
2. 저장: extensions/wrapped_mcp/{server_name}/
3. 복사: 각 워크스페이스로 자동 복사
```

---

### 보안 관련 사항

[`claude_agent/code_execution.py`](claude_agent/code_execution.py)는 단순한 `subprocess.run()`을 사용합니다:

```python
result = subprocess.run(
    ["python", str(script_path)],
    capture_output=True,
    text=True,
    timeout=timeout,        # 기본 20초
    cwd=str(workspace_dir), # 작업 디렉토리만 격리
    check=False
)
```

이는 **작업 디렉토리 분리와 실행 시간 제한만** 제공하며, 파일 시스템 접근, 네트워크 통신, 프로세스 생성 등을 제한하지 않습니다.

따라서 현재 구현은 **신뢰할 수 있는 환경에서 Claude가 생성한 코드를 실행하는 개발/프로토타이핑 용도**로만 적합하며, 프로덕션 환경 등에서는 반드시 더 강력한 격리 메커니즘을 추가해야 합니다.
