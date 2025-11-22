"""
Notification Service
Handles email notifications for various system events
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://safmc-fmp-tracker-frontend.onrender.com')


def send_email(to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
    """Send an email using SMTP"""
    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.warning("Email not configured - skipping notification")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f'"SAFMC FMP Tracker" <{EMAIL_USER}>'
        msg['To'] = to_email

        # Add text part first
        if text_body:
            part1 = MIMEText(text_body, 'plain')
            msg.attach(part1)

        # Add HTML part
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())

        logger.info(f"Email sent to {to_email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_new_comments_notification(admin_email: str, new_comments: list, admin_name: str = "Admin") -> bool:
    """Send notification about new comments to admin users"""
    if not new_comments:
        return False

    count = len(new_comments)
    subject = f"[SAFMC Tracker] {count} New Public Comment{'s' if count != 1 else ''} Received"

    # Build comment summary
    comments_html = ""
    for comment in new_comments[:10]:  # Show first 10
        comments_html += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px; vertical-align: top;">
                <strong>{comment.get('name', 'Anonymous')}</strong><br>
                <span style="color: #6b7280; font-size: 12px;">{comment.get('organization', '')}</span>
            </td>
            <td style="padding: 12px; vertical-align: top;">
                <span style="background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 4px; font-size: 12px;">
                    {comment.get('actionFmp', 'N/A')}
                </span>
            </td>
            <td style="padding: 12px; vertical-align: top; color: #374151; font-size: 13px;">
                {(comment.get('commentText', '')[:150] + '...') if len(comment.get('commentText', '')) > 150 else comment.get('commentText', '')}
            </td>
        </tr>
        """

    remaining = count - 10 if count > 10 else 0

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">New Public Comments</h1>
                <p style="color: #bfdbfe; margin: 8px 0 0 0; font-size: 14px;">SAFMC FMP Tracker</p>
            </div>

            <!-- Content -->
            <div style="padding: 24px;">
                <p style="color: #374151; margin: 0 0 16px 0;">
                    Hi {admin_name},
                </p>
                <p style="color: #374151; margin: 0 0 24px 0;">
                    <strong>{count}</strong> new public comment{'s have' if count != 1 else ' has'} been received since your last notification.
                </p>

                <!-- Comments Table -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
                    <thead>
                        <tr style="background: #f9fafb;">
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #6b7280; border-bottom: 2px solid #e5e7eb;">Commenter</th>
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #6b7280; border-bottom: 2px solid #e5e7eb;">FMP</th>
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #6b7280; border-bottom: 2px solid #e5e7eb;">Comment</th>
                        </tr>
                    </thead>
                    <tbody>
                        {comments_html}
                    </tbody>
                </table>

                {f'<p style="color: #6b7280; font-size: 13px; margin-bottom: 24px;">+ {remaining} more comments</p>' if remaining > 0 else ''}

                <!-- CTA Button -->
                <div style="text-align: center; margin: 24px 0;">
                    <a href="{FRONTEND_URL}/comments" style="display: inline-block; background: #1e40af; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500;">
                        View All Comments
                    </a>
                </div>
            </div>

            <!-- Footer -->
            <div style="background: #f9fafb; padding: 16px 24px; text-align: center; border-top: 1px solid #e5e7eb;">
                <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                    You're receiving this because you have comment notifications enabled.<br>
                    <a href="{FRONTEND_URL}/settings" style="color: #3b82f6;">Manage notification preferences</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    New Public Comments - SAFMC FMP Tracker

    Hi {admin_name},

    {count} new public comment{'s have' if count != 1 else ' has'} been received.

    View all comments: {FRONTEND_URL}/comments

    ---
    You're receiving this because you have comment notifications enabled.
    """

    return send_email(admin_email, subject, html_body, text_body)


def send_weekly_comment_digest(admin_email: str, stats: dict, admin_name: str = "Admin") -> bool:
    """Send weekly digest of comment activity"""
    subject = f"[SAFMC Tracker] Weekly Comment Digest - {stats.get('total', 0)} Comments This Week"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">Weekly Comment Digest</h1>
                <p style="color: #a7f3d0; margin: 8px 0 0 0; font-size: 14px;">Week of {stats.get('week_start', 'N/A')}</p>
            </div>

            <!-- Content -->
            <div style="padding: 24px;">
                <p style="color: #374151; margin: 0 0 24px 0;">Hi {admin_name},</p>

                <!-- Stats Grid -->
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 24px;">
                    <div style="background: #eff6ff; padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 32px; font-weight: bold; color: #1e40af;">{stats.get('total', 0)}</div>
                        <div style="color: #3b82f6; font-size: 12px;">Total Comments</div>
                    </div>
                    <div style="background: #f0fdf4; padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 32px; font-weight: bold; color: #059669;">{stats.get('support', 0)}</div>
                        <div style="color: #10b981; font-size: 12px;">Support</div>
                    </div>
                    <div style="background: #fef2f2; padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 32px; font-weight: bold; color: #dc2626;">{stats.get('oppose', 0)}</div>
                        <div style="color: #ef4444; font-size: 12px;">Oppose</div>
                    </div>
                    <div style="background: #faf5ff; padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 32px; font-weight: bold; color: #7c3aed;">{stats.get('unique_commenters', 0)}</div>
                        <div style="color: #8b5cf6; font-size: 12px;">Unique Commenters</div>
                    </div>
                </div>

                <!-- Top FMPs -->
                <h3 style="color: #374151; font-size: 14px; margin: 0 0 12px 0;">Top FMPs by Comments</h3>
                <div style="margin-bottom: 24px;">
                    {''.join([f'<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb;"><span style="color: #374151;">{fmp}</span><span style="font-weight: 600; color: #1e40af;">{count}</span></div>' for fmp, count in stats.get('top_fmps', {}).items()][:5])}
                </div>

                <!-- CTA -->
                <div style="text-align: center;">
                    <a href="{FRONTEND_URL}/comments" style="display: inline-block; background: #059669; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500;">
                        View Full Report
                    </a>
                </div>
            </div>

            <!-- Footer -->
            <div style="background: #f9fafb; padding: 16px 24px; text-align: center; border-top: 1px solid #e5e7eb;">
                <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                    <a href="{FRONTEND_URL}/settings" style="color: #3b82f6;">Manage notification preferences</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Weekly Comment Digest - SAFMC FMP Tracker
    Week of {stats.get('week_start', 'N/A')}

    Hi {admin_name},

    This week's comment activity:
    - Total Comments: {stats.get('total', 0)}
    - Support: {stats.get('support', 0)}
    - Oppose: {stats.get('oppose', 0)}
    - Unique Commenters: {stats.get('unique_commenters', 0)}

    View full report: {FRONTEND_URL}/comments
    """

    return send_email(admin_email, subject, html_body, text_body)


def notify_admins_of_new_comments(new_comments: list, db_session) -> int:
    """Send new comment notifications to all admin users with notifications enabled"""
    from src.models.user import User

    notified = 0

    try:
        # Get admin users with notifications enabled
        admins = User.query.filter(
            User.role.in_(['admin', 'super_admin']),
            User.email_notifications == True
        ).all()

        for admin in admins:
            if send_new_comments_notification(admin.email, new_comments, admin.name):
                notified += 1

        logger.info(f"Notified {notified} admins of {len(new_comments)} new comments")

    except Exception as e:
        logger.error(f"Error notifying admins: {e}")

    return notified
