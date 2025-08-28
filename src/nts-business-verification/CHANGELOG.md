# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-28

### Changed
- **BREAKING CHANGE**: Unified API key environment variable from `NTS_BUSINESS_VERIFICATION_API_KEY` to `API_KEY`
- All data.go.kr MCP servers now use a single `API_KEY` environment variable
- Updated documentation to reflect the unified API key approach

### Migration Guide
If you're upgrading from v0.1.0:
1. Change your environment variable from `NTS_BUSINESS_VERIFICATION_API_KEY` to `API_KEY`
2. Update your Claude Desktop configuration to use `API_KEY` instead of `NTS_BUSINESS_VERIFICATION_API_KEY`

## [0.1.0] - 2025-01-28

### Added
- Initial release of NTS Business Verification MCP server
- Business registration verification (validate_business)
- Business status check (check_business_status)
- Batch validation (batch_validate_businesses)