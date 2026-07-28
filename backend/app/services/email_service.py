"""Outbound email helper (fastapi-mail when SMTP configured)."""

from __future__ import annotations

import logging

from app.core.config import settings

logger = logging.getLogger("studyos.email")


def smtp_configured() -> bool:
    return bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD and settings.SMTP_FROM_EMAIL)


async def send_email(*, to: str, subject: str, html_body: str, text_body: str | None = None) -> bool:
    """Send email. Returns True on success. Never raises to callers for auth flows."""
    if not smtp_configured():
        logger.warning("SMTP not configured — email skipped to=%s subject=%s", to, subject)
        return False
    try:
        from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

        conf = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USERNAME,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.SMTP_FROM_EMAIL,
            MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )
        message = MessageSchema(
            subject=subject,
            recipients=[to],
            body=html_body,
            subtype=MessageType.html,
        )
        await FastMail(conf).send_message(message)
        logger.info("Email sent to=%s subject=%s", to, subject)
        return True
    except Exception:
        logger.exception("Email send failed to=%s subject=%s", to, subject)
        return False


async def send_password_reset_email(*, to: str, reset_url: str) -> bool:
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto">
      <h2>StudyOS — Şifre sıfırlama</h2>
      <p>Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın.
         Bağlantı {settings.PASSWORD_RESET_EXPIRE_MINUTES} dakika geçerlidir.</p>
      <p><a href="{reset_url}" style="display:inline-block;padding:12px 20px;
         background:#2563eb;color:#fff;border-radius:8px;text-decoration:none">
         Şifreyi sıfırla</a></p>
      <p style="color:#64748b;font-size:13px">Bu isteği siz yapmadıysanız bu e-postayı yok sayın.</p>
      <p style="color:#94a3b8;font-size:12px;word-break:break-all">{reset_url}</p>
    </div>
    """
    return await send_email(
        to=to,
        subject="StudyOS şifre sıfırlama",
        html_body=html,
        text_body=f"Şifre sıfırlama bağlantısı: {reset_url}",
    )
