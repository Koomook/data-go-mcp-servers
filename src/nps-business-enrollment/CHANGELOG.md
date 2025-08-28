# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-28

### Added
- Initial release of NPS Business Enrollment MCP Server
- `search_business` tool for searching National Pension Service business enrollment data
- Support for searching by:
  - Administrative district codes (시도, 시군구, 읍면동)
  - Business name
  - Business registration number (first 6 digits)
- Pagination support (page_no, num_of_rows)
- Comprehensive error handling
- Full documentation and examples