# Korea Data.go.kr MCP Servers

한국 공공 데이터 포털(data.go.kr) API를 Model Context Protocol (MCP) 서버로 제공하는 프로젝트입니다.

[![GitHub](https://img.shields.io/badge/github-data--go--mcp--servers-blue.svg?style=flat&logo=github)](https://github.com/yourusername/data-go-mcp-servers)
[![PyPI](https://img.shields.io/pypi/v/data-go-mcp.nps-business-enrollment)](https://pypi.org/project/data-go-mcp.nps-business-enrollment/)
[![License](https://img.shields.io/badge/license-Apache--2.0-brightgreen)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

## 목차

- [Korea Data.go.kr MCP Servers](#korea-datagokr-mcp-servers)
  - [목차](#목차)
  - [MCP (Model Context Protocol)란?](#mcp-model-context-protocol란)
  - [왜 한국 공공 데이터 MCP 서버인가?](#왜-한국-공공-데이터-mcp-서버인가)
  - [사용 가능한 MCP 서버](#사용-가능한-mcp-서버)
  - [설치 및 설정](#설치-및-설정)
    - [UV를 사용한 설치](#uv를-사용한-설치)
    - [pip을 사용한 설치](#pip을-사용한-설치)
    - [Claude Desktop 설정](#claude-desktop-설정)
    - [Cline 설정](#cline-설정)
  - [각 서버별 사용법](#각-서버별-사용법)
    - [국민연금공단 사업장 가입 내역 (NPS Business Enrollment)](#국민연금공단-사업장-가입-내역-nps-business-enrollment)
  - [개발자 가이드](#개발자-가이드)
  - [기여하기](#기여하기)
  - [라이센스](#라이센스)

## MCP (Model Context Protocol)란?

Model Context Protocol (MCP)은 LLM 애플리케이션과 외부 데이터 소스 및 도구 간의 원활한 통합을 가능하게 하는 개방형 프로토콜입니다. AI 기반 IDE를 구축하든, 채팅 인터페이스를 향상시키든, 사용자 정의 AI 워크플로우를 만들든, MCP는 LLM이 필요한 컨텍스트와 연결하는 표준화된 방법을 제공합니다.

MCP 서버는 Model Context Protocol을 통해 특정 기능을 노출하는 경량 프로그램입니다. Claude Desktop, Cline, Cursor, Windsurf 등의 AI 도구들이 MCP 클라이언트로서 이러한 서버와 통신할 수 있습니다.

## 왜 한국 공공 데이터 MCP 서버인가?

한국 정부의 공공 데이터 포털(data.go.kr)은 다양한 공공 기관의 데이터를 API로 제공합니다. 이 프로젝트는 이러한 API들을 MCP 서버로 래핑하여, AI 도구들이 한국 공공 데이터에 쉽게 접근하고 활용할 수 있도록 합니다.

주요 이점:
- **표준화된 접근**: 다양한 공공 API를 통일된 MCP 인터페이스로 사용
- **AI 도구 통합**: Claude, Cline 등 AI 도구에서 직접 공공 데이터 활용
- **간편한 설치**: pip 또는 uv로 쉽게 설치 가능
- **타입 안정성**: Pydantic을 사용한 강력한 타입 검증

## 사용 가능한 MCP 서버

### 🏢 비즈니스 정보
| 서버 | 설명 | 패키지 | PyPI |
|------|------|--------|------|
| **NPS Business Enrollment** | 국민연금공단 사업장 가입 정보 조회 | `data-go-mcp.nps-business-enrollment` | [![PyPI](https://img.shields.io/pypi/v/data-go-mcp.nps-business-enrollment)](https://pypi.org/project/data-go-mcp.nps-business-enrollment/) |

## 설치 및 설정

### UV를 사용한 설치

```bash
# NPS Business Enrollment 서버 설치
uv pip install data-go-mcp.nps-business-enrollment
```

### pip을 사용한 설치

```bash
# NPS Business Enrollment 서버 설치
pip install data-go-mcp.nps-business-enrollment
```

### Claude Desktop 설정

Claude Desktop의 설정 파일에 MCP 서버를 추가합니다:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "data-go-mcp.nps-business-enrollment": {
      "command": "uvx",
      "args": ["data-go-mcp.nps-business-enrollment"],
      "env": {
        "NPS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Cline 설정

VS Code의 Cline 확장에서 MCP 서버를 설정합니다:

`.vscode/cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "data-go-mcp.nps-business-enrollment": {
      "command": "python",
      "args": ["-m", "data_go_mcp.nps_business_enrollment.server"],
      "env": {
        "NPS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 각 서버별 사용법

### 국민연금공단 사업장 가입 내역 (NPS Business Enrollment)

국민연금에 가입된 사업장 정보를 조회할 수 있습니다.

#### 환경 변수 설정

```bash
export NPS_API_KEY="your-api-key-here"  # data.go.kr에서 발급받은 API 키
```

#### 사용 가능한 도구

**`search_business`**: 사업장 정보 검색
- 파라미터:
  - `ldong_addr_mgpl_dg_cd`: 법정동주소 광역시도 코드 (2자리)
  - `ldong_addr_mgpl_sggu_cd`: 법정동주소 시군구 코드 (5자리)
  - `ldong_addr_mgpl_sggu_emd_cd`: 법정동주소 읍면동 코드 (8자리)
  - `wkpl_nm`: 사업장명
  - `bzowr_rgst_no`: 사업자등록번호 (앞 6자리)
  - `page_no`: 페이지 번호 (기본값: 1)
  - `num_of_rows`: 한 페이지 결과 수 (기본값: 100, 최대: 100)

#### 사용 예시

AI 도구에서 다음과 같이 요청할 수 있습니다:

```
"서울특별시 강남구에 있는 사업장을 검색해줘"
"삼성전자 사업장 정보를 찾아줘"
"사업자등록번호 123456으로 시작하는 사업장을 조회해줘"
```

## 개발자 가이드

### 개발 환경 설정

```bash
# 레포지토리 클론
git clone https://github.com/yourusername/data-go-mcp-servers.git
cd data-go-mcp-servers

# UV 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 개발 의존성 설치
uv sync --dev
```

### 🚀 새로운 MCP 서버 빠르게 만들기

#### 자동화 스크립트 사용 (권장)

가장 빠른 방법은 제공된 템플릿 생성 스크립트를 사용하는 것입니다:

```bash
# 대화형 스크립트 실행
uv run python scripts/create_mcp_server.py
```

스크립트가 필요한 정보를 단계별로 안내하며, 몇 분 안에 새로운 MCP 서버를 생성합니다.

#### 수동으로 템플릿 사용

```bash
# Cookiecutter 설치 (필요시)
uv pip install cookiecutter

# 템플릿으로 새 서버 생성
uv run cookiecutter template/ -o src/
```

자세한 템플릿 사용법은 [TEMPLATE_USAGE.md](TEMPLATE_USAGE.md)를 참조하세요.
전체 개발 가이드는 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

### 테스트 실행

```bash
# 모든 테스트 실행
uv run pytest

# 특정 서버 테스트
uv run pytest src/nps-business-enrollment/tests/
```

## 기여하기

이 프로젝트에 기여하고 싶으시다면:

1. 이 레포지토리를 포크하세요
2. 새로운 기능 브랜치를 만드세요 (`git checkout -b feature/new-api-server`)
3. 변경사항을 커밋하세요 (`git commit -am 'Add new API server'`)
4. 브랜치에 푸시하세요 (`git push origin feature/new-api-server`)
5. Pull Request를 열어주세요

자세한 가이드는 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 라이센스

이 프로젝트는 Apache License 2.0 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

**참고**: 이 프로젝트는 한국 정부나 data.go.kr와 공식적으로 연관되어 있지 않습니다. 공공 데이터 사용 시 각 데이터의 이용약관을 확인하시기 바랍니다.