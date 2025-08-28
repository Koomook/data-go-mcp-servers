#!/usr/bin/env python
"""MCP server runner script."""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the server
from data_go_mcp.nts_business_verification.server import main
main()