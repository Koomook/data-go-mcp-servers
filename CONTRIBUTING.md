# Contributing to Korea Data.go.kr MCP Servers

이 문서는 새로운 공공 데이터 API를 MCP 서버로 추가하는 방법을 안내합니다.

## 목차

- [Contributing to Korea Data.go.kr MCP Servers](#contributing-to-korea-datagokr-mcp-servers)
  - [목차](#목차)
  - [시작하기 전에](#시작하기-전에)
  - [새 MCP 서버 추가하기](#새-mcp-서버-추가하기)
    - [1. 디렉토리 구조 생성](#1-디렉토리-구조-생성)
    - [2. pyproject.toml 작성](#2-pyprojecttoml-작성)
    - [3. 서버 코드 구현](#3-서버-코드-구현)
    - [4. README 작성](#4-readme-작성)
    - [5. 테스트 작성](#5-테스트-작성)
    - [6. 루트 README 업데이트](#6-루트-readme-업데이트)
  - [코드 스타일 가이드](#코드-스타일-가이드)
  - [커밋 메시지 규칙](#커밋-메시지-규칙)
  - [Pull Request 프로세스](#pull-request-프로세스)
  - [API 키 관리](#api-키-관리)
  - [문서화 가이드](#문서화-가이드)
  - [도움이 필요하신가요?](#도움이-필요하신가요)

## 시작하기 전에

1. **API 키 발급**: [data.go.kr](https://www.data.go.kr)에서 사용하려는 API의 키를 발급받으세요.
2. **API 문서 검토**: API의 공식 문서를 숙지하세요.
3. **개발 환경 설정**:
   ```bash
   # UV 설치 (아직 없다면)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # 레포지토리 클론
   git clone https://github.com/Koomook/data-go-mcp-servers.git
   cd data-go-mcp-servers
   
   # 개발 의존성 설치
   uv sync --dev
   ```

## 새 MCP 서버 추가하기

### 1. 디렉토리 구조 생성

```bash
mkdir -p src/your-api-name/data_go_mcp/your_api_name
mkdir -p src/your-api-name/tests
```

예시:
```bash
mkdir -p src/weather-forecast/data_go_mcp/weather_forecast
mkdir -p src/weather-forecast/tests
```

### 2. pyproject.toml 작성

`src/your-api-name/pyproject.toml`:

```toml
[project]
name = "data-go-mcp-your-api-name"
version = "0.1.0"
description = "MCP server for [API 이름] from data.go.kr"
readme = "README.md"
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
requires-python = ">=3.10"
license = {text = "Apache-2.0"}
keywords = ["mcp", "korea", "data.go.kr", "your-api-keywords"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
dependencies = [
    "httpx>=0.28.1",
    "mcp[cli]>=1.13.0",
    "pydantic>=2.11.7",
    "python-dotenv>=1.1.1",
]

[project.urls]
Homepage = "https://github.com/Koomook/data-go-mcp-servers"
Repository = "https://github.com/Koomook/data-go-mcp-servers"
Documentation = "https://github.com/Koomook/data-go-mcp-servers#your-api-name"
"Bug Tracker" = "https://github.com/Koomook/data-go-mcp-servers/issues"

[project.scripts]
data-go-mcp-your-api-name = "data_go_mcp.your_api_name.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["data_go_mcp"]
```

### 3. 서버 코드 구현

#### models.py - 데이터 모델 정의

`src/your-api-name/data_go_mcp/your_api_name/models.py`:

```python
"""Data models for Your API."""

from typing import Optional, List
from pydantic import BaseModel, Field


class YourDataModel(BaseModel):
    """Your data model."""
    
    field1: str = Field(..., description="필드 설명")
    field2: Optional[int] = Field(None, description="선택적 필드")
    # ... 더 많은 필드


class SearchResponse(BaseModel):
    """API 응답 모델."""
    
    items: List[YourDataModel]
    page_no: int
    num_of_rows: int
    total_count: int
```

#### api_client.py - API 클라이언트

`src/your-api-name/data_go_mcp/your_api_name/api_client.py`:

```python
"""API client for Your API."""

import os
from typing import Optional, Dict, Any
import httpx
from urllib.parse import urlencode
import xml.etree.ElementTree as ET  # XML 응답인 경우
# import json  # JSON 응답인 경우


class YourAPIClient:
    """Client for Your API."""
    
    BASE_URL = "https://api.data.go.kr/your-api-endpoint"
    
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError(
                "API_KEY environment variable is required. "
                "Get your API key from https://www.data.go.kr"
            )
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def search(
        self,
        param1: Optional[str] = None,
        param2: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 100
    ) -> Dict[str, Any]:
        """Search data from API."""
        
        params = {
            "serviceKey": self.api_key,
            "pageNo": str(page_no),
            "numOfRows": str(num_of_rows),
        }
        
        if param1:
            params["param1"] = param1
        if param2:
            params["param2"] = param2
        
        # URL 인코딩 처리
        query_string = urlencode(params, safe="", quote_via=quote)
        url = f"{self.BASE_URL}?{query_string}"
        
        response = await self.client.get(url)
        response.raise_for_status()
        
        # XML 파싱 예시
        root = ET.fromstring(response.text)
        # ... 파싱 로직
        
        return {
            "items": items,
            "page_no": page_no,
            "num_of_rows": num_of_rows,
            "total_count": total_count
        }
```

#### server.py - MCP 서버

`src/your-api-name/data_go_mcp/your_api_name/server.py`:

```python
"""MCP server for Your API."""

import os
import asyncio
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from .api_client import YourAPIClient

# 환경변수 로드
load_dotenv()

# MCP 서버 인스턴스 생성
mcp = FastMCP("Your API Name")


@mcp.tool()
async def search_data(
    param1: Optional[str] = None,
    param2: Optional[str] = None,
    page_no: int = 1,
    num_of_rows: int = 100
) -> Dict[str, Any]:
    """
    데이터를 검색합니다.
    
    Search data from Your API.
    
    Args:
        param1: 파라미터 1 설명
        param2: 파라미터 2 설명
        page_no: 페이지 번호 (기본값: 1)
        num_of_rows: 한 페이지 결과 수 (기본값: 100)
    
    Returns:
        Dictionary containing:
        - items: List of data
        - page_no: Current page number
        - num_of_rows: Number of rows per page
        - total_count: Total number of results
    """
    async with YourAPIClient() as client:
        try:
            result = await client.search(
                param1=param1,
                param2=param2,
                page_no=page_no,
                num_of_rows=num_of_rows
            )
            return result
        except Exception as e:
            return {
                "error": str(e),
                "items": [],
                "page_no": page_no,
                "num_of_rows": num_of_rows,
                "total_count": 0
            }


def main():
    """Main entry point."""
    import sys
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

### 4. README 작성

`src/your-api-name/README.md`:

```markdown
# Your API Name MCP Server

[API 이름]을 위한 MCP 서버입니다.

## 설치

```bash
pip install data-go-mcp-your-api-name
# 또는
uv pip install data-go-mcp-your-api-name
```

## 환경 변수 설정

```bash
export API_KEY="your-api-key-here"
```

## 사용 가능한 도구

### search_data

데이터를 검색합니다.

**파라미터:**
- `param1`: 파라미터 1 설명
- `param2`: 파라미터 2 설명
- `page_no`: 페이지 번호 (기본값: 1)
- `num_of_rows`: 한 페이지 결과 수 (기본값: 100)

**예시:**
```
"param1으로 데이터 검색해줘"
```

## Claude Desktop 설정

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "your-api-name": {
      "command": "uvx",
      "args": ["data-go-mcp-your-api-name"],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## API 문서

공식 API 문서: [링크]
```

### 5. 테스트 작성

`src/your-api-name/tests/test_api.py`:

```python
"""Tests for Your API MCP server."""

import pytest
import os
from unittest.mock import patch, AsyncMock
from data_go_mcp.your_api_name.api_client import YourAPIClient


@pytest.mark.asyncio
async def test_search_without_api_key():
    """Test that client raises error without API key."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="API_KEY"):
            YourAPIClient()


@pytest.mark.asyncio
async def test_search_with_mock_response():
    """Test search with mocked API response."""
    with patch.dict(os.environ, {"API_KEY": "test-key"}):
        async with YourAPIClient() as client:
            # Mock the HTTP client
            mock_response = AsyncMock()
            mock_response.text = "<xml>...</xml>"  # Mock response
            mock_response.raise_for_status = AsyncMock()
            
            client.client.get = AsyncMock(return_value=mock_response)
            
            result = await client.search(param1="test")
            
            assert "items" in result
            assert result["page_no"] == 1
```

### 6. 루트 README 업데이트

루트 `README.md`의 "사용 가능한 MCP 서버" 섹션에 새 서버를 추가하세요.

## 코드 스타일 가이드

- **Python 버전**: 3.10 이상 지원
- **포맷터**: Ruff 사용 (`uv run ruff format`)
- **린터**: Ruff 사용 (`uv run ruff check`)
- **타입 힌트**: 모든 함수에 타입 힌트 사용
- **Docstring**: Google 스타일 사용
- **비동기**: 모든 API 호출은 비동기로 구현

## 커밋 메시지 규칙

```
type(scope): description

[optional body]

[optional footer]
```

**타입:**
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 스타일 변경
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드 프로세스나 보조 도구 변경

**예시:**
```
feat(weather): add weather forecast MCP server

- Implement weather API client
- Add search_forecast tool
- Add comprehensive tests
```

## Pull Request 프로세스

1. 포크 및 브랜치 생성
2. 코드 작성 및 테스트
3. 린트 및 포맷 체크:
   ```bash
   uv run ruff format
   uv run ruff check
   uv run pytest src/your-api-name/tests/
   ```
4. Pull Request 생성
5. 코드 리뷰 및 피드백 반영
6. 머지

## API 키 관리

- **절대로** API 키를 코드에 하드코딩하지 마세요
- 환경 변수로만 API 키를 관리하세요
- `.env` 파일은 `.gitignore`에 포함되어야 합니다
- README에는 환경 변수 설정 예시만 포함하세요

## 문서화 가이드

각 MCP 서버는 다음 문서를 포함해야 합니다:

1. **README.md**: 설치, 설정, 사용법
2. **CHANGELOG.md**: 버전별 변경사항
3. **Docstring**: 모든 public 함수와 클래스
4. **사용 예시**: AI 도구에서 사용하는 예시 프롬프트

## 도움이 필요하신가요?

- [Issues](https://github.com/Koomook/data-go-mcp-servers/issues)에서 질문하세요
- [Discussions](https://github.com/Koomook/data-go-mcp-servers/discussions)에서 아이디어를 공유하세요
- 기존 MCP 서버 코드를 참조하세요