# Claude Agent with MCP

Claude API와 Model Context Protocol (MCP)을 사용하여 AI 에이전트를 구현한 프로젝트입니다.

## 개요

이 프로젝트는 Anthropic의 Claude API를 기반으로 하여, MCP 서버들을 통해 다양한 도구들을 연결하고 활용할 수 있는 AI 에이전트 시스템입니다. 파일 시스템, 메모리, 웹 fetch 등의 기능을 Claude 모델과 통합하여 더욱 강력한 AI 어시스턴트를 제공합니다.

## 주요 기능

- **Claude API 통합**: Anthropic의 Claude API를 사용한 응답 생성
- **MCP 서버 지원**: 다양한 MCP 서버와의 연결 및 도구 활용
- **자동 도구 실행**: Claude가 호출한 MCP 도구를 자동으로 실행
- **대화 히스토리 관리**: 컨텍스트를 유지하는 대화 관리

## 파일 구조

```
claude_agent/
├── main.py          # 메인 실행 파일
├── agent.py         # Claude Agent 구현
├── mcp_client.py    # MCP Client 구현
├── config.json      # 설정 파일
└── README.md        # 프로젝트 문서
```

## 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 설정 파일 구성

`config.json` 파일에서 `YOUR_API_KEY` 부분을 Claude API 키로 교체해주세요.

필요에 따라 사용할 MCP 서버를 추가하거나 수정할 수도 있습니다.\
기본 설정에는 아래 세 가지 MCP 서버가 활성화되어 있습니다:

- **filesystem**: 파일 시스템 작업
- **memory**: 지식그래프를 사용한 메모리 관리
- **fetch**: 웹 콘텐츠 가져오기


### 3. 실행

```bash
python main.py
```

프로그램을 실행하면 대화형 인터페이스가 시작됩니다.

```
대화를 시작하세요!
종료하려면 'quit'을 입력하세요.
> (사용자 입력)
```

