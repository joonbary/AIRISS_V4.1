# MCP (Model Context Protocol) Servers Configuration

이 파일은 Claude Desktop에서 사용하는 MCP 서버들의 설정을 포함하고 있습니다.

## 설정된 MCP 서버들

### 1. Filesystem Server
- **명령어**: `npx @modelcontextprotocol/server-filesystem`
- **경로**: `C:\Users\apro`
- **기능**: 파일 시스템 접근 및 조작

### 2. Sequential Thinking Server
- **명령어**: `npx -y @modelcontextprotocol/server-sequential-thinking`
- **기능**: 순차적 사고 및 추론 지원

### 3. GitHub Server
- **명령어**: `npx -y @modelcontextprotocol/server-github`
- **환경 변수**: 
  - `GITHUB_PERSONAL_ACCESS_TOKEN`: 설정됨
- **기능**: GitHub 저장소 접근 및 작업

### 4. YouTube Server
- **명령어**: `npx -y @anaisbetts/mcp-youtube`
- **기능**: YouTube 콘텐츠 분석 및 접근

### 5. PyHub MCPTools
- **실행 파일**: `C:\Users\apro\Downloads\pyhub.mcptools-windows-v0.9.8\pyhub.mcptools\pyhub.mcptools.exe`
- **인자**: `run stdio`
- **기능**: Python 관련 도구 및 유틸리티

### 6. Shrimp Task Manager
- **명령어**: `npx -y mcp-shrimp-task-manager`
- **환경 변수**:
  - `DATA_DIR`: `C:\Users\apro\ShrimpData`
  - `TEMPLATES_USE`: `en`
  - `ENABLE_GUI`: `false`
- **기능**: 작업 관리 및 추적

## 사용 방법

1. 이 설정을 사용하려면 `claude_desktop_config.json` 파일을 다음 위치에 복사하세요:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. 필요한 npm 패키지들을 설치하세요:
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   npm install -g @modelcontextprotocol/server-sequential-thinking
   npm install -g @modelcontextprotocol/server-github
   npm install -g @anaisbetts/mcp-youtube
   npm install -g mcp-shrimp-task-manager
   ```

3. PyHub MCPTools는 별도로 다운로드해야 합니다.

4. Claude Desktop을 재시작하면 설정이 적용됩니다.

## 주의사항

- GitHub Personal Access Token이 포함되어 있으므로 이 파일을 공유하거나 공개 저장소에 업로드하지 마세요.
- 경로들이 사용자 특정적이므로 다른 환경에서 사용할 때는 수정이 필요할 수 있습니다.