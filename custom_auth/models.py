import uuid

import pyotp
from django.apps import apps
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

from custom_auth.tool import random_string
from dsbd.models import MediumTextField


class GroupManager(models.Manager):
    def active_filter(self):
        return self.filter(is_active=True)

    def create_group(
        self, question, name, name_jp, postcode, address, address_jp, phone, country, contract_type, **extra_fields
    ):
        extra_fields.setdefault("is_pass", False)
        return self.create(
            agree=True,
            question=question,
            name=name,
            name_jp=name_jp,
            postcode=postcode,
            address=address,
            address_jp=address_jp,
            phone=phone,
            country=country,
            contract_type=contract_type,
            **extra_fields,
        )

    def update_group(self, group_id, postcode, address, address_en, email, phone, country):
        group = Group.objects.get(id=group_id)
        group.postcode = postcode
        group.address = address
        group.address_en = address_en
        group.email = email
        group.phone = phone
        group.country = country
        group.save()


GROUP_STATUS_CHOICES = (
    (1, "有効"),
    (10, "ユーザより廃止"),
    (11, "運営委員より廃止"),
    (12, "審査落ち"),
)

# Membership
# 1-49 一般支払い
# 70-89 特別枠(無料)
# 90-99 特別枠(運営)
MEMBERSHIP_TYPE_CHOICES = (
    (1, "一般会員"),
    (40, "運営委員(優勝)"),
    (70, "学生委員"),
    (90, "運営委員(無償)"),
    (99, "その他"),
)

CONTRACT_TYPE_CHOICES = (
    ("E-Mail", "E-Mail"),
    ("AirMail", "AirMail)"),
)


class Group(models.Model):  # noqa: F811
    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    name = models.CharField("name", max_length=150, unique=True)
    name_jp = models.CharField("name(japanese)", max_length=150, unique=True)
    comment = models.CharField("comment", max_length=250, default="", blank=True)
    status = models.IntegerField("ステータス", default=1, choices=GROUP_STATUS_CHOICES)
    allow_service_add = models.BooleanField("サービス追加許可", default=False)
    membership_type = models.IntegerField("会員種別", default=1, choices=MEMBERSHIP_TYPE_CHOICES)
    membership_expired_at = models.DateTimeField("有効期限", blank=True, null=True)

    # question
    agree = models.BooleanField("規約確認済み", default=False)
    question = MediumTextField(verbose_name="質問内容", default="")
    is_pass = models.BooleanField("審査OK", default=False)

    # stripe
    stripe_customer_id = models.CharField("Stripe(CusID)", max_length=200, blank=True, null=True)
    stripe_subscription_id = models.CharField("Stripe(SubID)", max_length=200, blank=True, null=True)

    # group personal info
    postcode = models.CharField("郵便番号", max_length=20, default="")
    address = models.CharField("住所", max_length=250, default="")
    address_jp = models.CharField("住所(Japanese)", max_length=250, default="")
    phone = models.CharField("phone", max_length=30, default="")
    country = models.CharField("居住国", max_length=100, default="Japan")
    contract_type = models.CharField("契約種別", max_length=100, default="E-Mail", choices=CONTRACT_TYPE_CHOICES)
    users = models.ManyToManyField(
        "User",
        blank=True,
        through="UserGroup",
        through_fields=("group", "user"),
        related_name="group_users_set",
    )

    objects = GroupManager()

    class Meta:
        verbose_name = "グループ"
        verbose_name_plural = "グループ"

    def __str__(self):
        return "%s: %s" % (self.id, self.name)


class UserManager(BaseUserManager):
    def _create_user(self, username, username_jp, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, username_jp=username_jp, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username, username_jp, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", False)
        user = self._create_user(username, username_jp, email, password, **extra_fields)
        user_activate_token = UserActivateToken.objects.create(user=user)
        subject = "Please Activate Your Account"
        message = (
            f"URLにアクセスしてアカウントを有効化してください。\n "
            f"{settings.DOMAIN_URL}/activate/{user_activate_token.token}/"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [
            user.email,
        ]
        send_mail(subject, message, from_email, recipient_list)

        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self._create_user(username, email, password, **extra_fields)

    def change_email(self, user=None, email=""):
        if not user:
            raise ValueError("user_id is not found......")
        if not email:
            raise ValueError("email is not found......")
        user.email = email
        user.is_active = False
        user_activate_token = UserActivateToken.objects.create(user=user)
        subject = "Please Activate Your Changed Email"
        message = (
            f"メールアドレスが変更されたので、URLにアクセスしてアカウントを有効化してください。\n"
            f" {settings.DOMAIN_URL}/activate/{user_activate_token.token}/"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [
            email,
        ]
        send_mail(subject, message, from_email, recipient_list)

        user.save()

    def update_user(self, user=None, name="", name_jp="", display_name=""):
        if not user:
            raise ValueError("user_id is not found......")
        if not name:
            raise ValueError("name is not found......")
        if not name_jp:
            raise ValueError("name_jp is not found......")
        if not display_name:
            raise ValueError("display_name is not found......")
        user.name = name
        user.name_jp = name_jp
        user.display_name = display_name
        user.save()


class User(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()

    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    display_name = models.CharField("display_name", max_length=150, default="", blank=True)
    username = models.CharField("username", max_length=150, validators=[username_validator], unique=True)
    username_jp = models.CharField("username(japanese)", max_length=150, validators=[username_validator], unique=True)
    email = models.EmailField("email", unique=True)
    is_staff = models.BooleanField("管理者ステータス", default=False)
    is_active = models.BooleanField("有効", default=False)
    allow_group_add = models.BooleanField("グループ追加許可", default=True)
    groups = models.ManyToManyField(
        "Group",
        blank=True,
        through="UserGroup",
        through_fields=("user", "group"),
        related_name="user_set",
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "ユーザ"
        verbose_name_plural = "ユーザ"

    def __str__(self):
        return "%s: %s" % (self.id, self.username)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_display_name(self):
        if self.display_name == "":
            return self.username
        return self.display_name

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_staff:
            return True

        return False

    def has_module_perms(self, app_label):
        if self.is_active and self.is_staff:
            return True

        return False


def user_activate_expire_date():
    return timezone.now() + timezone.timedelta(hours=settings.USER_LOGIN_VERIFY_EMAIL_EXPIRED_HOURS)


def email_verify_expire_date():
    return timezone.now() + timezone.timedelta(hours=settings.USER_LOGIN_VERIFY_EMAIL_EXPIRED_MINUTES)


class UserActivateTokensManager(models.Manager):
    def activate_user_by_token(self, activate_token):
        if not self.filter(token=activate_token, expired_at__gt=timezone.now()).exists():
            raise ValueError("Token is not found......")
        user_activate_token = self.filter(token=activate_token, expired_at__gt=timezone.now()).first()
        if user_activate_token.is_used:
            raise ValueError("this token was used...")
        if user_activate_token.user.is_active:
            raise ValueError("アカウントはすでに有効済みです")
        if hasattr(user_activate_token, "user"):
            user = user_activate_token.user
            user.is_active = True
            user.save()
            user_activate_token.is_used = True
            user_activate_token.save()


class UserActivateToken(models.Model):
    created_at = models.DateTimeField("作成日", default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField("Active token", default=uuid.uuid4)
    expired_at = models.DateTimeField("有効期限", default=user_activate_expire_date)
    is_used = models.BooleanField("使用済み", default=False)

    objects = UserActivateTokensManager()

    class Meta:
        verbose_name = "Activate用のToken"
        verbose_name_plural = "Activate用のToken"

    def __str__(self):
        return "%d[%s]: %s" % (self.id, self.user.username, self.token)


def sign_up_key_expire_date():
    return timezone.now() + timezone.timedelta(days=settings.SIGN_UP_EXPIRED_DAYS)


class UserGroup(models.Model):
    created_at = models.DateTimeField("作成日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_admin = models.BooleanField("管理者", default=False)

    class Meta:
        verbose_name = "ユーザ・グループ"
        verbose_name_plural = "ユーザ・グループ"
        unique_together = ("user", "group")

    def __str__(self):
        return "%s-%s" % (self.user.username, self.group.name)


class UserEmailVerifyManager(models.Manager):
    def create_token(self, user=None):
        if not user:
            raise ValueError("user_id is not found......")
        code = random_string(10)
        self.create(user_id=user.id, token=code)
        subject = "認証コード"
        message = render_to_string(
            "mail/account/two_auth.txt",
            {"code": code, "expired_time": settings.USER_LOGIN_VERIFY_EMAIL_EXPIRED_MINUTES},
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

    def check_token(self, user_id=None, token=""):
        if not user_id:
            raise ValueError("user_id is not found......")
        try:
            sign_up_key = self.filter(token=token, expired_at__gt=timezone.now(), is_used=False).first()
        except Exception:
            return False
        # keyがない時
        if not sign_up_key:
            return False
        sign_up_key.delete()
        return True


class UserEmailVerify(models.Model):
    created_at = models.DateTimeField("作成日", default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField("token", max_length=100)
    expired_at = models.DateTimeField("有効期限", default=email_verify_expire_date)
    is_used = models.BooleanField("使用済み", default=False)

    objects = UserEmailVerifyManager()

    class Meta:
        verbose_name = "E-Mail用のVerify"
        verbose_name_plural = "E-Mail用のVerify"

    def __str__(self):
        return "%d[%s]" % (
            self.id,
            self.user.username,
        )


class TOTPDeviceManager(models.Manager):
    def check_max_totp_device(self, user=None):
        if not user:
            raise ValueError("user_id is not found......")
        return self.filter(user=user).count() <= 5

    def generate_secret(self, email=""):
        otp_secret = pyotp.random_base32()
        return {
            "secret": otp_secret,
            "url": pyotp.totp.TOTP(otp_secret).provisioning_uri(name=email, issuer_name=settings.APP_NAME),
        }

    def create_secret(self, user=None, title="", otp_secret=""):
        if not user:
            raise ValueError("user_id is not found......")
        self.create(title=title, user=user, secret=otp_secret, is_active=True)

    def check_totp(self, user=None, code=""):
        if not user:
            raise ValueError("user_id is not found......")
        totp_array = self.filter(user=user)
        verify_code = False
        for totp_array_one in totp_array:
            totp = pyotp.TOTP(totp_array_one.secret)
            verify_code = totp.verify(code)
            if verify_code:
                break
        return verify_code

    def list(self, user=None):
        if not user:
            raise ValueError("user_id is not found......")
        return self.filter(user=user)

    def remove(self, user=None, id=None):
        if not user:
            raise ValueError("user_id is not found......")
        self.filter(user=user, id=id).delete()


class TOTPDevice(models.Model):
    created_at = models.DateTimeField("作成日", default=timezone.now)
    title = models.CharField("title", max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret = models.CharField("secret", max_length=100)
    is_active = models.BooleanField("有効", default=False)

    objects = TOTPDeviceManager()

    class Meta:
        verbose_name = "TOTP Device"
        verbose_name_plural = "TOTP Device"

    def __str__(self):
        return "%d[%s]" % (self.id, self.user.username)
