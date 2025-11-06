# Email Configuration Setup for SAFMC FMP Tracker

## Current Issue
The application is in "DEV MODE - Email not configured" because the EMAIL_USER and EMAIL_PASSWORD environment variables are not set on Render.

## Solution

### 1. Get Gmail App Password

If you're using the same Gmail account as the interview system, you can reuse the same app password.

Otherwise, create a new Gmail App Password:
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name it "SAFMC FMP Tracker"
4. Copy the generated 16-character password

### 2. Set Environment Variables on Render

Go to your SAFMC FMP Tracker service on Render:
1. Navigate to "Environment" tab
2. Add these environment variables:

```
EMAIL_USER=your-gmail@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx  (the 16-character app password)
```

**Important:** Use the same values as your interview system's `GMAIL_USER` and `GMAIL_APP_PASSWORD`.

### 3. Restart Service

After adding the environment variables, Render will automatically redeploy.

## How It Works

The auth system in `/src/routes/auth_routes.py`:
- Uses Gmail SMTP (`smtp.gmail.com:465`)
- Sends HTML-formatted magic link emails
- Falls back to DEV MODE if EMAIL_USER or EMAIL_PASSWORD are missing
- In DEV MODE, the magic link is returned in the API response and logged

## Testing

After configuration:
1. Go to login page
2. Enter your email
3. You should receive an email (not see "DEV MODE" message)
4. Click the link in the email to log in

## Verification

Check Render logs to confirm:
- You should see: `Magic link email sent to [email]`
- You should NOT see: `Email not configured, logging magic link instead`
