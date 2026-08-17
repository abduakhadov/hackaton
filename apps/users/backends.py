from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class PhoneOrUsernameAuthBackend(ModelBackend):
    """
    Telefon raqami (har xil formatda: +998..., 998...)
    yoki admin foydalanuvchisi uchun login backend.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        username_str = str(username).strip()
        # Turli formatlarni sinab ko'ramiz
        candidates = [username_str]
        if username_str.startswith('+'):
            candidates.append(username_str[1:])
        else:
            candidates.append('+' + username_str)

        # Agar "admin" deb yozilsa, superuser larni qidirish
        if username_str.lower() in ('admin', 'superuser'):
            for superuser in UserModel.objects.filter(is_superuser=True):
                if superuser.check_password(password) and self.user_can_authenticate(superuser):
                    return superuser

        for candidate in candidates:
            try:
                user = UserModel.objects.get(phone_number=candidate)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except UserModel.DoesNotExist:
                continue
            except UserModel.MultipleObjectsReturned:
                user = UserModel.objects.filter(phone_number=candidate).first()
                if user and user.check_password(password) and self.user_can_authenticate(user):
                    return user

        return None
