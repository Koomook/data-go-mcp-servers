#!/bin/bash

echo "🚀 Deploying NPS Business Enrollment MCP Server v0.2.0 to PyPI"
echo "============================================"

# Check if we're in the right directory
if [ ! -f "src/nps-business-enrollment/pyproject.toml" ]; then
    echo "❌ Error: Must run from the root directory of data-go-mcp-servers"
    exit 1
fi

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo "📦 Installing twine..."
    pip install twine
fi

# Check dist files
echo "📋 Checking built packages..."
ls -la dist/data_go_mcp_nps_business_enrollment-0.2.0*

echo ""
echo "📦 Package details:"
echo "- Package: data-go-mcp.nps-business-enrollment"
echo "- Version: 0.2.0"
echo "- Breaking change: API_KEY unified across all servers"
echo ""
echo "⚠️  IMPORTANT: This will publish to PyPI. Make sure you have:"
echo "1. PyPI account credentials configured"
echo "2. Permission to publish to data-go-mcp.nps-business-enrollment"
echo ""
read -p "Do you want to proceed with deployment? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to PyPI..."
    twine upload dist/data_go_mcp_nps_business_enrollment-0.2.0*
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully deployed to PyPI!"
        echo "🔗 View at: https://pypi.org/project/data-go-mcp.nps-business-enrollment/0.2.0/"
        echo ""
        echo "📝 Next steps:"
        echo "1. Test installation: pip install --upgrade data-go-mcp.nps-business-enrollment"
        echo "2. Update GitHub release notes"
        echo "3. Notify users about the breaking change (NPS_API_KEY -> API_KEY)"
    else
        echo "❌ Deployment failed. Please check the error messages above."
        exit 1
    fi
else
    echo "❌ Deployment cancelled."
    exit 1
fi