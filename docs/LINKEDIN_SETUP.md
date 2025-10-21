# LinkedIn OAuth Setup Guide

## Overview

This guide helps you set up LinkedIn OAuth authentication for SocialCLI.

## Prerequisites

1. A LinkedIn Developer account
2. A registered LinkedIn application

## Step 1: Create a LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click "Create app"
3. Fill in the required information:
   - **App name**: Your application name (e.g., "SocialCLI")
   - **LinkedIn Page**: Select or create a LinkedIn Page
   - **App logo**: Upload a logo (optional but recommended)
   - **Legal agreement**: Accept the terms

## Step 2: Configure OAuth Settings

1. In your app's settings, go to the **Auth** tab
2. Under **OAuth 2.0 settings**, add the redirect URL:
   ```
   http://localhost:8080/callback
   ```
3. Click **Update**

## Step 3: Get Your Credentials

1. In the **Auth** tab, find:
   - **Client ID** (also called "Application ID")
   - **Client Secret** (click "Show" to reveal it)
2. Copy these values

## Step 4: Configure SocialCLI

1. Update your `~/.socialcli/config.yaml` file:
   ```yaml
   providers:
     linkedin:
       client_id: YOUR_CLIENT_ID_HERE
       client_secret: YOUR_CLIENT_SECRET_HERE
   ```

## Step 5: Request API Products

LinkedIn requires you to request access to specific API products:

1. Go to the **Products** tab in your app
2. Request access to:
   - **Sign In with LinkedIn using OpenID Connect** (usually auto-approved)
   - **Share on LinkedIn** (may require verification for production use)

### Development vs Production

- **Development Mode**: Apps work with limited scopes during development
  - Required scopes: `openid`, `profile`, `email`, `w_member_social`
  - Works with the creator's LinkedIn account and test accounts
  - No app verification needed

- **Production Mode**: Requires app verification
  - Same scopes as development
  - Works with any LinkedIn user
  - Requires LinkedIn to verify your app

## OAuth Scopes Used by SocialCLI

The following scopes are requested during authentication:

- `openid` - Required for OpenID Connect authentication
- `profile` - Access to basic profile information
- `email` - Access to email address
- `w_member_social` - Permission to post on behalf of the user

## Troubleshooting

### Issue: "App Verification Required" Page

**Symptom**: Redirected to `https://www.linkedin.com/developers/apps/verification/...`

**Solution**:
1. During development, you can test with your own LinkedIn account
2. Make sure you're logged into LinkedIn with the same account that created the app
3. For production use with other users, you need to submit your app for verification:
   - Go to app settings → **Settings** tab
   - Click "Verify app"
   - Fill out the verification form
   - Wait for LinkedIn approval (typically 1-2 weeks)

### Issue: "Invalid Redirect URI"

**Cause**: The redirect URI in the request doesn't match what's registered

**Solution**:
1. Check that `http://localhost:8080/callback` is added in your app's Auth settings
2. Make sure there are no typos or extra spaces
3. The URI must match exactly (including `http://` and port)

### Issue: "Invalid Scope" Error

**Cause**: Requesting scopes not granted to your app

**Solution**:
1. Verify you have "Sign In with LinkedIn using OpenID Connect" product access
2. For posting, verify you have "Share on LinkedIn" product access
3. Check the Products tab in your LinkedIn app

### Issue: Token Expired

**Cause**: Access tokens expire after 60 days

**Solution**:
1. Run `socialcli login` to re-authenticate
2. The tool will automatically use the refresh token if available

## Testing Your Setup

1. Clear any existing tokens:
   ```bash
   rm ~/.socialcli/config.yaml
   ```

2. Run the login command:
   ```bash
   socialcli login --provider linkedin
   ```

3. Your browser should open with LinkedIn's OAuth consent page
4. After authorizing, you should see: "✓ Successfully authenticated with linkedin"

## Development Tips

### Using Your Own Account for Testing

During development, you can test with your own LinkedIn account without app verification:

1. Log into LinkedIn with the account that created the app
2. Run `socialcli login`
3. The OAuth flow will work for the app creator without verification

### Adding Test Users

To test with other accounts during development:

1. Go to your app's **Settings** tab
2. Add test users under "Test users" section
3. These users can authenticate without app verification

## Production Checklist

Before using your app in production:

- [ ] App verified by LinkedIn
- [ ] Redirect URI registered: `http://localhost:8080/callback`
- [ ] Products approved: "Sign In with LinkedIn", "Share on LinkedIn"
- [ ] Privacy policy URL added to app settings
- [ ] Terms of service URL added to app settings
- [ ] App logo uploaded
- [ ] App description accurate and complete

## Resources

- [LinkedIn OAuth 2.0 Documentation](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [LinkedIn API Products](https://www.linkedin.com/developers/apps)
- [App Verification Guide](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/compliance)
