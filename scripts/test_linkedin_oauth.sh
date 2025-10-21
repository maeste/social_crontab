#!/bin/bash
# LinkedIn OAuth Diagnostic Script
# Tests LinkedIn OAuth configuration and identifies issues

set -e

echo "================================"
echo "LinkedIn OAuth Diagnostic Tool"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Read config
CONFIG_FILE="$HOME/.socialcli/config.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}✗ Config file not found: $CONFIG_FILE${NC}"
    echo "  Please create it first with your LinkedIn credentials"
    exit 1
fi

echo -e "${GREEN}✓ Config file found${NC}"
echo ""

# Extract client_id from config
CLIENT_ID=$(grep -A5 "linkedin:" "$CONFIG_FILE" | grep "client_id:" | awk '{print $2}' | tr -d '"' | tr -d "'")

if [ -z "$CLIENT_ID" ]; then
    echo -e "${RED}✗ Client ID not found in config${NC}"
    echo "  Please add client_id to $CONFIG_FILE"
    exit 1
fi

echo -e "${GREEN}✓ Client ID found: $CLIENT_ID${NC}"
echo ""

# Test 1: Basic OAuth URL
echo "Test 1: Testing OAuth endpoint..."
OAUTH_URL="https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${CLIENT_ID}&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback&scope=openid+profile+email"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$OAUTH_URL")

if [ "$HTTP_CODE" = "500" ]; then
    echo -e "${RED}✗ HTTP 500 Error - LinkedIn server error${NC}"
    echo ""
    echo "Possible causes:"
    echo "  1. App deleted or suspended"
    echo "  2. Redirect URI not registered in app settings"
    echo "  3. Required API products not enabled"
    echo "  4. Temporary LinkedIn API issue"
    echo ""
    echo "NEXT STEPS:"
    echo "  → Go to: https://www.linkedin.com/developers/apps"
    echo "  → Verify your app exists (client_id: $CLIENT_ID)"
    echo "  → Check Auth tab → Redirect URLs → Add: http://localhost:8080/callback"
    echo "  → Check Products tab → Request 'Sign In with LinkedIn using OpenID Connect'"
    echo ""
elif [ "$HTTP_CODE" = "303" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ OAuth endpoint responding (HTTP $HTTP_CODE - redirect to login)${NC}"
    echo -e "${GREEN}  Your LinkedIn app configuration is working correctly!${NC}"
    echo ""
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "${RED}✗ HTTP 404 - Invalid client_id or endpoint${NC}"
    echo "  Double-check your client_id in the config"
    echo ""
else
    echo -e "${YELLOW}⚠ Unexpected HTTP code: $HTTP_CODE${NC}"
    echo ""
fi

# Test 2: Check if socialcli command exists
echo "Test 2: Checking socialcli installation..."
if command -v socialcli &> /dev/null; then
    echo -e "${GREEN}✓ socialcli command found${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠ socialcli command not found${NC}"
    echo "  Make sure you've activated your virtual environment and installed the package"
    echo "  Run: source .venv/bin/activate && uv pip install -e ."
    echo ""
fi

# Test 3: Config structure
echo "Test 3: Validating config structure..."
if grep -q "redirect_uri:" "$CONFIG_FILE"; then
    REDIRECT_URI=$(grep "redirect_uri:" "$CONFIG_FILE" | awk '{print $2}' | tr -d '"' | tr -d "'")
    echo -e "${GREEN}✓ Redirect URI in config: $REDIRECT_URI${NC}"
else
    echo -e "${YELLOW}⚠ No redirect_uri in config (will use default)${NC}"
fi

if grep -q "client_secret:" "$CONFIG_FILE"; then
    echo -e "${GREEN}✓ Client secret present${NC}"
else
    echo -e "${RED}✗ Client secret missing${NC}"
fi

echo ""

# Summary and next steps
echo "================================"
echo "Summary"
echo "================================"
echo ""

if [ "$HTTP_CODE" = "500" ]; then
    echo -e "${RED}STATUS: Configuration issue detected${NC}"
    echo ""
    echo "Action required:"
    echo "1. Visit https://www.linkedin.com/developers/apps"
    echo "2. Verify your app (client_id: $CLIENT_ID)"
    echo "3. Follow the checklist in docs/QUICK_FIX.md"
    echo ""
    echo "Or create a new app if this one is deleted/suspended"
elif [ "$HTTP_CODE" = "303" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}STATUS: ✅ Everything is configured correctly!${NC}"
    echo ""
    echo -e "${GREEN}You're ready to authenticate!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Make sure you're logged into LinkedIn with the app creator account"
    echo "  2. Run: socialcli login --provider linkedin"
    echo "  3. Authorize the app in your browser"
    echo ""
    echo "Or test the OAuth flow in browser:"
    echo "  $OAUTH_URL"
else
    echo -e "${YELLOW}STATUS: Needs investigation${NC}"
    echo ""
    echo "Unexpected response from LinkedIn (HTTP $HTTP_CODE)"
    echo "See docs/QUICK_FIX.md for troubleshooting"
fi

echo "================================"
echo ""
echo "For detailed help, see:"
echo "  - docs/QUICK_FIX.md (troubleshooting)"
echo "  - docs/LINKEDIN_SETUP.md (complete setup guide)"
echo ""
