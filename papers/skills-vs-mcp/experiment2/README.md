# Skills vs. MCP 비교 실험 (BrowseComp Benchmark)

이 디렉토리는 **BrowseComp** 벤치마크를 사용하여 **Skills**와 **MCP** 서버의 성능을 정량적으로 비교하기 위한 실험 코드를 포함하고 있습니다.

## Task 2) BrowseComp Evaluation

### 개요

BrowseComp는 웹 브라우징 능력을 평가하는 벤치마크입니다. 이 실험에서는:
* **MCP 모드**: Search MCP 서버를 통한 웹 검색
* **Skills 모드**: Anthropic Skills를 통한 웹 검색

두 가지 방식으로 동일한 질문들에 대해 답변하고, 정확도와 성능 메트릭을 비교합니다.

### 실험 결과

실험 결과는 다음 디렉토리에 저장됩니다:
* MCP 모드: `results/mcp/[timestamp]/`
* Skills 모드: `results/skills/[timestamp]/`

각 실행 디렉토리에는 아래 파일들이 저장됩니다:
* `sample_XXX.json`: 각 샘플의 상세 결과 (문제, 정답, 응답, 메타데이터)
* `summary.json`: 전체 평가 요약 (정확도, 평균 실행 시간, 토큰 사용량 등)

### 실험 실행 가이드

#### 1. 환경 준비

```bash
pip install -r requirements.txt
```

`config.json` 파일에서 `YOUR_CLAUDE_API_KEY`, `YOUR_BRAVE_API_KEY`, `YOUR_SERPER_API_KEY` 부분을 실제 API key 로 교체합니다.

#### 2. MCP 모드 실험

MCP 서버만을 사용한 웹 검색 평가:

```bash
python run_browsecomp.py
```

#### 3. Skills 모드 실험

Anthropic Skills를 이용한 웹 검색 평가:

```bash
python run_browsecomp.py --use_skills
```

#### 4. 결과 확인

`results/mcp[skills]/[timestamp]`


## 프로젝트 구조

```
experiment2/
├── README.md                          
├── config.json                       # 실험 설정
├── requirements.txt                  # Python 의존성
├── run_browsecomp.py                 # 메인 실행 스크립트
├── agent_sampler.py                  # Claude Agent 래퍼
├── claude_sampler.py                 # Grader용 Claude 래퍼
├── utils.py                          # 유틸리티 함수
├── browsecomp/                       # BrowseComp 벤치마크
│   ├── browsecomp_eval.py            # 평가 로직
│   ├── common.py                     # 공통 유틸리티
│   └── types.py                      # 타입 정의
├── claude_agent/                     # Claude Agent 구현
│   ├── agent.py                      # Agent 메인 클래스
│   ├── mcp_client.py                 # MCP 클라이언트
│   ├── custom_skills.py              # Skills 관리
│   └── extensions/
│       ├── mcp/search-mcp-server/    # Search MCP 서버
│       └── skills/strategic-search/  # Search Skill
└── results/                          # 실험 결과 저장
    ├── mcp/                          # MCP 모드 결과
    └── skills/                       # Skills 모드 결과
```


## 참고 자료

* [BrowseComp Benchmark Evaluation Code](https://github.com/openai/simple-evals?tab=readme-ov-file)
* [Claude Skills Cookbooks](https://github.com/anthropics/claude-cookbooks)
