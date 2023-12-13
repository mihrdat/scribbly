from django.conf import settings
from django.utils.html import urlencode
from django.contrib.auth.tokens import default_token_generator

from templated_mail.mail import BaseEmailMessage

from .utils import encode_uid


class PasswordResetEmail(BaseEmailMessage):
    template_name = "reset_password.html"

    def get_context_data(self):
        context = super().get_context_data()

        user = context.get("user")
        uid = encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        url = (
            settings.RESET_PASSWORD_CONFIRM_URL
            + "?"
            + urlencode({"uid": uid, "token": token})
        )

        context["username"] = user.username
        context["uid"] = uid
        context["token"] = token
        context["url"] = url

        return context


class ActivationEmail(BaseEmailMessage):
    template_name = "activation.html"

    def get_context_data(self):
        context = super().get_context_data()

        username = context.get("username")
        code = context.get("code")

        context["username"] = username
        context["code"] = code

        return context
