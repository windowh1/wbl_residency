# Skills vs MCP

Skills는 **재사용 가능한 워크플로우 패키징 메커니즘**이고, MCP는 **외부 시스템 통합을 위한 표준 프로토콜**입니다.  

| 구분 | **Skills** | **MCP** |
| - | - | - |
| **목적** | 특정 작업에 대한 지침과 워크플로우 제공 | 외부 데이터 소스 및 도구와의 연결 |
| **벤더** | Claude 전용 | 벤더 독립적 표준 프로토콜 |
| **주요 구성** | 폴더 (`SKILL.md`, Scripts, Resources) | Client-Server (Tools, Resources, Prompts) |
| **적절한 사용 사례** | 반복적이고 표준화된 작업을 Claude를 사용하여 자동화 | 외부 시스템과 연동이 필요한 벤더 독립적 솔루션 구현 |


---

## Table of Contents

[1. Skills](#1-skills)\
[2. MCP (Model Context Protocol)](#2-mcp-model-context-protocol)\
[3. Skills vs MCP](#3-skills-vs-mcp)\
[3.1. Task 1: PPTX](#31-task-1-pptx)\
[4. References](#4-references)


---

## 1. Skills

### 1.1. 핵심 개념

* **폴더 기반 패키지**: `SKILL.md` 및 **추가 가이드 문서**, **스크립트(실행 코드)**, **리소스(템플릿, 데이터)** 등을 묶어서 배포합니다.

    ```
    my_skill/
    ├── SKILL.md           # Required: Instructions for Claude
    ├── *.md               # Optional: Any additional guide materials
    ├── scripts/           # Optional: Python/JS code
    │   └── processor.py
    └── resources/         # Optional: Templates, data
        └── template.xlsx
    ```

    * **`SKILL.md`**: 상단의 **YAML frontmatter**(`name`, `description`)와 **Markdown 지침**으로 구성됩니다.

        ```md
        ---
        name: pdf-processing
        description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
        ---
        
        # PDF Processing

        ## Quick start

        Use pdfplumber to extract text from PDFs:

        ```python
        import pdfplumber

        with pdfplumber.open("document.pdf") as pdf:
            text = pdf.pages[0].extract_text()
        ```

* **Progressive Disclosure 메커니즘**: 

  모든 사용 가능한 skill의 **YAML frontmatter를 스캔**하여 현재 작업과의 관련성을 평가한 후, **관련된 skill의 자료를 선택적으로 로드**합니다. \
  이는 프롬프트 길이가 과도하게 늘어나는 것을 방지하는 효과가 있습니다.

  1. 각 skill의 `SKILL.md` **YAML frontmatter**만 시스템 프롬프트에 선주입.
  2. 현재 작업과 관련된 skill의 `SKILL.md` **Markdown 지침**을 컨텍스트에 주입.
  3. 추가적인 자료(스크립트, 리소스 등)는 필요할 경우에만 **선택적으로** 접근.


### 1.2. API 사용

API에서 Skills를 사용할 때는 skill 리스트를 포함하는 `container`를 지정합니다. \
각 skill은 `type`, `skill_id`, `version`을 가지며, 코드 실행이 필요한 경우가 대다수이므로 code execution tool을 함께 활성화합니다.

```python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    # Skills 지정
    container={
        "skills": [
            {
                "type": "anthropic", # or "custom"
                "skill_id": "pptx",
                "version": "latest"
            }
        ]
    },
    messages=[{
        "role": "user",
        "content": "Create a presentation about renewable energy"
    }],
    # Code execution tool 활성화
    tools=[{
        "type": "code_execution_20250825",
        "name": "code_execution"
    }]
)

```


### 1.3. 사용 가능 Skills

공식에서 배포된 Anthropic Skills를 사용하거나, 직접 커스텀하여 사용하는 두 가지 방법이 있습니다. 

| 구분 | **Anthropic Skills** | **Custom Skills** |
| - | - | - |
| **Type 값** | `anthropic` | `custom` |
| **Skill ID 형식** | 짧은 이름 (e.g., `pptx`, `xlsx`, `docx`, `pdf`) | 자동 생성 (e.g., `skill_01AbCdEfGhIjKlMnOpQrStUv`) |
| **Version 형식** | 날짜 기반 (e.g., `20251013` or `latest`) | epoch 기반 (e.g., `1759178010641129` or `latest`) |
| **Management** | Anthropic이 사전 구축 및 유지 보수 | 사용자가 [Skills API](https://docs.claude.com/en/api/skills/create-skill)로 업로드 및 관리 |
| **Availability** | 모든 사용자에게 제공 | 워크스페이스 전용 (비공개) |

#### Anthropic Skills
* [GitHub 리포지토리](https://github.com/anthropics/skills)
* 사용 가능한 skill 예시:
  * `pptx` (PowerPoint)
  * `xlsx` (Excel)
  * `docx` (Word)
  * `pdf`  (PDF 처리)

#### Custom Skills
* [GitHub 리포지토리](https://github.com/anthropics/claude-cookbooks/tree/main/skills) (예제 및 쿡북) 
* 생성 방법
  * **필수**: `SKILL.md` 상단에 **YAML frontmatter**(`name`, `description`), 본문에 **지침**(워크플로우, 규칙, 예시 등)을 작성합니다.
  * **선택**: 동일한 폴더에 스크립트 파일, 템플릿 등을 작성합니다.


---

## 2. MCP (Model Context Protocol)

* **오픈 프로토콜**: MCP는 LLM 애플리케이션과 외부 시스템을 연결하는 표준화된 방식을 제공합니다.

* **아키텍처**: MCP는 **클라이언트-서버 구조**를 따릅니다. 하나의 MCP 호스트는 클라이언트를 통해 여러 MCP 서버와 연결할 수 있습니다.
  * **MCP 호스트**: 여러 MCP 클라이언트를 관리하고 조정하는 AI 애플리케이션.
  * **MCP 클라이언트**: MCP 서버와의 연결을 유지하며, 서버로부터 컨텍스트 정보를 수집하는 구성 요소.
  * **MCP 서버**: MCP 클라이언트에 컨텍스트를 제공하는 프로그램.

  ![mcp-architecture](images/mcp-architecture.png)

* **핵심 Primitive**: MCP 서버는 다음과 같은 **세 가지 주요 기능**을 제공합니다.
  * **Tools**: LLM이 직접 호출할 수 있는 실행 가능한 함수.
  * **Resources**: AI 애플리케이션에 맥락 정보를 제공하는 데이터 소스.
  * **Prompts**: 반복적으로 재사용 가능한 프롬프트 템플릿.

* **전송 방식**: MCP는 두 가지 통신 방식을 지원합니다.
  * **Stdio Transport**: 동일한 머신 내의 프로세스 간에 표준 입출력 스트림(stdio)을 사용하여 직접 통신.
  * **Streamable HTTP Transport**: HTTP POST를 사용하여 클라이언트에서 서버로 메시지를 전송하고, Server-Sent Events를 통해 스트리밍 기능을 제공.


---

## 3. Skills vs MCP

동일한 태스크에 대해 **Claude Skills**와 **MCP (Model Context Protocol)** 의 작동 방식 및 성능을 비교한 결과입니다.  
실험용 코드와 상세 결과물은 [`experiments`](./experiments) 디렉터리에서 확인할 수 있습니다.


### 3.1. Task 1: PPTX

#### 실험 세팅

* **Skills**: `{"type": "anthropic", "skill_id": "pptx", "version": "20251013"}`
* **MCP**: [Office-PowerPoint-MCP-Server](https://github.com/GongRzhe/Office-PowerPoint-MCP-Server)
* 공통 설정:
  * 사용 모델: `claude-sonnet-4-5-20250929`
  * 사용자 프롬프트: *"Create a PowerPoint presentation about AI prompting techniques."*
  * Temperature: 0.5
  * 반복 횟수: 10회 시도 후 평균값 계산

#### 실험 결과

* **정량 평가**

  | Metric | Skills | MCP |
  | - | - | - |
  | **Duration (sec)** | 432.34 | 101.91 |
  | **Input Tokens** | 1,471,175 | 218,070 |
  | **Output Tokens** | 16,592 | 5,561 |
  | **Tool Calls** | 49 | 28 |
  | **Success Ratio** | 40% | 100% |

  * **Skills**는 Progressive Disclosure 전략을 사용하여 context 사이즈를 줄이려 시도했으나,  
    보다 세밀한 작업이 이루어지면서 MCP에 비해 **duration(처리 시간), input/output token 수, tool call 횟수가 크게 증가**함.  
  * 실제 결과물(.pptx) 저장 여부를 기준으로 판단한 **success ratio**의 경우, **MCP**는 100% 로 안정적이었던 반면 **Skills**는 **max token limit** 문제 등으로 작업이 중단되는 경우가 있어 40% 수준에 머무름.

* **정성 평가**
  * **Skills**는 비교적 일관된 슬라이드 구조와 디자인 품질을 유지하며, 시각적으로 완성도가 높은 결과물을 생성함 ([실험 결과물 예시](experiments/skills/test_pptx)).

    ![task1-skills](images/task1-skills.png)

  * **MCP**는 일부 슬라이드에서 빈 페이지, 작은 글씨, 비일관적 레이아웃 등 시각적 완성도가 다소 낮은 경향을 보임 ([실험 결과물 예시](experiments/mcp/test_pptx)).

    ![task1-mcp](images/task1-mcp.png)


---

## 4. References

* https://www.anthropic.com/news/skills
* https://docs.claude.com/en/docs/agents-and-tools/agent-skills
* https://docs.claude.com/en/api/skills-guide
* https://github.com/anthropics/skills
* https://github.com/anthropics/claude-cookbooks/tree/main/skills
* https://modelcontextprotocol.io/docs