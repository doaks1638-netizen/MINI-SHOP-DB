from fastapi import FastAPI
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.settings import settings
from app.schemas import EmailSchema

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USERNAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="doaks",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)
app = FastAPI()


async def send_url(email: EmailSchema, url: str) -> JSONResponse:
    html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ссылка подтверждения</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333333;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); overflow: hidden;">
        <tr>
            <td style="background-color: #4a90e2; padding: 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: bold;">Подтверждение аккаунта</h1>
            </td>
        </tr>
        <tr>
            <td style="padding: 40px 30px; text-align: center;">
                <p style="font-size: 16px; line-height: 1.5; color: #666666; margin-bottom: 30px;">
                    Здравствуйте! Перейдите по ссылке для завершения аутентификации в системе.
                </p>
                
                <a href="{url}" target="_blank" style="display: inline-block; background-color: #4a90e2; color: #ffffff; text-decoration: none; padding: 14px 30px; font-size: 16px; font-weight: bold; border-radius: 6px; box-shadow: 0 2px 5px rgba(74,144,226,0.25);">
                    Подтвердить аккаунт
                </a>

                <p style="font-size: 11px; line-height: 1.5; color: #999999; margin-top: 30px; word-break: break-all;">
                    Если кнопка не работает, скопируйте и вставьте эту ссылку в браузер:<br>
                    <a href="{url}" style="color: #4a90e2;">{url}</a>
                </p>
                <p style="font-size: 12px; line-height: 1.5; color: #999999; margin-top: 30px;">
                    Если вы не запрашивали это письмо, просто проигнорируйте его.
                </p>
            </td>
        </tr>
        <tr>
            <td style="background-color: #fafafa; padding: 20px; text-align: center; border-top: 1px solid #eeeeee;">
                <p style="font-size: 12px; color: #999999; margin: 0;">&copy; 2026 MINI-SHOP-DB. Все права защищены.</p>
            </td>
        </tr>
    </table>
</body>
</html>
    """

    message = MessageSchema(
        subject="Подтверждение регистрации — MINI-SHOP-DB",
        recipients=[email.email],  # Используем прямой доступ к полю Pydantic
        body=html,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})

async def send_code(email: EmailSchema, code: str) -> JSONResponse:
    html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Код подтверждения</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333333;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" width="100%" style="max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); overflow: hidden;">
        <tr>
            <td style="background-color: #4a90e2; padding: 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: bold;">Код подтверждения входа</h1>
            </td>
        </tr>
        <tr>
            <td style="padding: 40px 30px; text-align: center;">
                <p style="font-size: 16px; line-height: 1.5; color: #666666; margin-bottom: 25px;">
                    Здравствуйте! Используйте этот одноразовый код для подтверждения входа в систему.
                </p>
                
                <div style="display: inline-block; background-color: #f4f4f9; border: 1px dashed #4a90e2; padding: 15px 40px; font-size: 32px; font-weight: bold; font-family: 'Courier New', Courier, monospace; color: #4a90e2; letter-spacing: 6px; border-radius: 6px; margin-bottom: 25px;">
                    {code}
                </div>

                <p style="font-size: 13px; line-height: 1.5; color: #999999;">
                    Код действителен в течение 5 минут.<br>
                    Никому не сообщайте этот код.
                </p>
                <p style="font-size: 12px; line-height: 1.5; color: #999999; margin-top: 30px;">
                    Если вы не запрашивали это письмо, просто проигнорируйте его.
                </p>
            </td>
        </tr>
        <tr>
            <td style="background-color: #fafafa; padding: 20px; text-align: center; border-top: 1px solid #eeeeee;">
                <p style="font-size: 12px; color: #999999; margin: 0;">&copy; 2026 MINI-SHOP-DB. Все права защищены.</p>
            </td>
        </tr>
    </table>
</body>
</html>
    """

    message = MessageSchema(
        subject="Код подтверждения входа — MINI-SHOP-DB",
        recipients=[email.email],
        body=html,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "Verification code has been sent"})