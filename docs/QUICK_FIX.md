# Quick Fix: LinkedIn OAuth 500 Error

## Current Problem: HTTP 500 Error

**Status**: LinkedIn OAuth endpoint is returning `HTTP 500` (Internal Server Error)

```bash
curl -v "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=77tzg8go6ddkpa&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback&scope=openid+profile+email+w_member_social" 2>&1 | grep "< HTTP"
# Returns: < HTTP/2 500
```

This indicates a **LinkedIn server-side issue**, NOT a code problem. The OAuth URL is correctly formatted.

## Root Causes (Likely)

1. **Invalid/Deleted App**: Client ID `77tzg8go6ddkpa` may be from a deleted or suspended app
2. **Missing Redirect URI**: `http://localhost:8080/callback` not registered in app settings
3. **Missing API Products**: Required LinkedIn products not enabled/approved
4. **LinkedIn API Issue**: Temporary LinkedIn service outage

## What Changed?

Updated the OAuth scopes in `socialcli/providers/linkedin/auth.py:51`:

**Before:**
```python
scope = "w_member_social r_liteprofile"
```

**After:**
```python
scope = "openid profile email w_member_social"
```

## Step-by-Step Fix

### Step 1: Verify LinkedIn App Exists

1. **Go to**: https://www.linkedin.com/developers/apps
2. **Check**: Does your app with client_id `77tzg8go6ddkpa` exist?
   - ✅ **Yes, app exists**: Continue to Step 2
   - ❌ **No, app missing/deleted**: Go to Step 5 (Create New App)

### Step 2: Check Redirect URI Configuration

1. **Open your app** in LinkedIn Developer Portal
2. **Go to**: **Auth** tab
3. **Find**: "Redirect URLs" section
4. **Verify**: `http://localhost:8080/callback` is listed
   - ✅ **Already there**: Continue to Step 3
   - ❌ **Missing**: Click "Add redirect URL", paste `http://localhost:8080/callback`, click "Update"

### Step 3: Verify API Products

1. **Go to**: **Products** tab
2. **Check these products**:
   - ✅ **Sign In with LinkedIn using OpenID Connect** - Must be "Approved"
   - ✅ **Share on LinkedIn** - Must be "Approved" or "Requested"
3. **If not requested**:
   - Click "Select" on each product
   - Click "Request access"
   - Wait for approval (usually instant for "Sign In")

### Step 4: Test in Browser

1. **Open this URL** in your browser (replace YOUR_CLIENT_ID):
   ```
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback&scope=openid+profile+email
   ```

2. **Expected Results**:
   - ✅ **OAuth consent page appears**: SUCCESS! Go to Step 6
   - ❌ **HTTP 500 error**: Continue to Step 5
   - ⚠️ **"Verification required" page**: Normal for dev mode, continue to Step 6

### Step 5: Create New LinkedIn App (If Needed)

If your app is missing or HTTP 500 persists:

1. **Go to**: https://www.linkedin.com/developers/apps
2. **Click**: "Create app"
3. **Fill in**:
   - App name: "SocialCLI" (or your choice)
   - LinkedIn Page: Select or create a page
   - App logo: Optional
   - Accept terms
4. **After creation**:
   - Go to **Auth** tab → Add redirect URL: `http://localhost:8080/callback`
   - Go to **Products** tab → Request "Sign In with LinkedIn using OpenID Connect"
   - Copy new **Client ID** and **Client Secret**
5. **Update config**:
   ```bash
   nano ~/.socialcli/config.yaml
   # Update client_id and client_secret with new values
   ```

### Step 6: Test Authentication

#### Option A: Use Your Own Account (Easiest)

If you created the LinkedIn app, you can test immediately:

1. **Make sure you're logged into LinkedIn** with the account that created the app
2. Run the login command:
   ```bash
   socialcli login --provider linkedin
   ```
3. Authorize the app when prompted
4. Done! You can now post to LinkedIn

#### Option B: Add Test Users

To test with other accounts during development:

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Select your app
3. Go to **Settings** tab
4. Add test users under "Test users" section
5. Those users can now authenticate without app verification

#### Option C: Request App Verification (For Production)

If you want to use this with any LinkedIn user:

1. Go to your app in [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click **Settings** tab
3. Click "Verify app"
4. Fill out the verification form (includes privacy policy, terms of service, etc.)
5. Wait for LinkedIn approval (typically 1-2 weeks)

## Verify Your App Settings

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Select your app (client_id: `77tzg8go6ddkpa`)
3. Go to **Auth** tab
4. Verify redirect URL is set to: `http://localhost:8080/callback`
5. Go to **Products** tab
6. Verify you have access to:
   - ✅ Sign In with LinkedIn using OpenID Connect (should be auto-approved)
   - ✅ Share on LinkedIn (may require verification)

## Test the Fix

Try logging in now:

```bash
socialcli login --provider linkedin
```

Expected behavior:
- Browser opens to LinkedIn OAuth page
- You see a consent screen asking for permissions
- After approval, you're redirected to success page
- Terminal shows: "✓ Successfully authenticated with linkedin"

## Diagnostic Commands

### Quick HTTP 500 Test
```bash
# Test OAuth endpoint - should return 200 or 302, NOT 500
curl -s -o /dev/null -w "%{http_code}\n" "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback&scope=openid+profile"
```

### Check Current Config
```bash
cat ~/.socialcli/config.yaml
```

### Test Login
```bash
socialcli login --provider linkedin
```

## Still Having Issues?

### Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| **HTTP 500** | App deleted/suspended or redirect URI not registered | Create new app or add redirect URI |
| **Invalid redirect URI** | Redirect URL not in Auth tab | Add `http://localhost:8080/callback` in Auth settings |
| **Invalid scope** | Products not approved | Request "Sign In with LinkedIn" product |
| **Verification required** | Dev mode restriction | Use app creator account or add test users |
| **Invalid client_id** | Wrong credentials in config | Copy correct values from Auth tab |

### Debug Checklist

- [ ] App exists in https://www.linkedin.com/developers/apps
- [ ] Client ID matches config file
- [ ] Client Secret is correct
- [ ] Redirect URI `http://localhost:8080/callback` is registered
- [ ] "Sign In with LinkedIn using OpenID Connect" product is approved
- [ ] Browser test shows OAuth page (not 500 error)
- [ ] Logged into LinkedIn with app creator account

### Get More Help

- **Detailed Setup Guide**: See `docs/LINKEDIN_SETUP.md`
- **LinkedIn Developer Forums**: https://www.linkedin.com/help/linkedin/forums
- **API Documentation**: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication
- **API Status**: https://www.linkedin-apistatus.com/

## Security Reminder

⚠️ **Never commit secrets to Git**:
- Client Secret is sensitive
- Access tokens are very sensitive
- Add `.socialcli/` to `.gitignore`
