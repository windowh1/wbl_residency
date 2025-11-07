# Skills vs. MCP 비교 실험

이 디렉토리는 동일한 태스크(*e.g., AI prompting techniques에 대한 PPT 생성*)에 대한 **Skills**와 **MCP**의 작동 방식 및 성능을 비교하기 위한 실험 코드를 포함하고 있습니다.

## Task 1) PPTX

### 실험 결과
* [실험 결과 요약](../README.md#31-task-1-pptx)
* 상세 결과물: 
  * [MCP 실험 결과물](mcp/test_pptx)
  * [Skills 실험 결과물](skills/test_pptx)


### 실험 실행 가이드

직접 실험을 재현하고 싶다면 아래 단계를 따라 진행하세요.

#### 1. 환경 준비
현재 디렉토리에서 필요한 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```
`config.json` 파일에서 `YOUR_API_KEY` 부분을 Claude API 키로 교체합니다. \
필요 시 해당 파일에서 실험 세팅을 조정할 수 있습니다.


#### 2. MCP 실험
로컬 MCP 서버([Office-PowerPoint-MCP-Server](https://github.com/GongRzhe/Office-PowerPoint-MCP-Server))를 이용해 PPTX를 생성합니다:

  ```bash
  cd mcp
  mkdir -p mcp_library
  cd mcp_library
  git clone https://github.com/GongRzhe/Office-PowerPoint-MCP-Server.git
  cd Office-PowerPoint-MCP-Server
  pip install -r requirements.txt
  chmod +x ppt_mcp_server.py
  cd ../..
  python test_pptx.py
  ```

#### 3. Skills 실험
Anthropic Skills(`pptx`)을 이용해 PPTX를 생성합니다:

```bash
cd skills
python test_pptx.py
```
