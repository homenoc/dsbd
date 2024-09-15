from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django_countries.fields import CountryField

from custom_auth.models import Group, User, UserGroup


class GroupAddForm(forms.Form):
    agree = forms.ChoiceField(
        label="1.1. 各規約に同意する", required=True, choices=((False, "同意しない"), (True, "同意する"))
    )
    question1 = forms.CharField(
        label="1.2.1. どこで当団体のことを知りましたか？", min_length=10, required=True, widget=forms.Textarea()
    )
    question2 = forms.CharField(
        label="1.2.2. どのような用途で当団体のネットワークに接続しますか？",
        min_length=10,
        required=True,
        widget=forms.Textarea(),
    )
    question3 = forms.CharField(
        label="1.2.3. アドレスを当団体から割り当てる必要はありますか？",
        min_length=10,
        required=True,
        widget=forms.Textarea(),
    )
    question4 = forms.CharField(
        label="1.2.4. 情報発信しているSNS(Twitter,Facebook)やWebサイト、GitHub、成果物などがありましたら教えてください",
        min_length=10,
        required=True,
        widget=forms.Textarea(),
    )
    name = forms.CharField(label="2.1. グループ名", max_length=150, required=True)
    name_jp = forms.CharField(label="2.2.グループ名(Japanese)", max_length=150, required=True)
    postcode = forms.CharField(label="2.3.郵便番号", max_length=10, required=True)
    address = forms.CharField(label="2.4. 住所", max_length=250, required=True)
    address_jp = forms.CharField(label="2.5. 住所(Japanese)", max_length=250, required=True)
    phone = forms.CharField(label="2.6. phone", max_length=30, required=True)
    country = CountryField().formfield(label="2.7. 居住国", required=True)
    contract = forms.ChoiceField(
        label="3. 契約書",
        required=True,
        choices=(("E-Mail", "電子交付を希望する"), ("AirMail", "書面の郵送を希望する")),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = field.label

    def clean(self):
        agree = self.cleaned_data.get("agree")
        if not agree:
            raise forms.ValidationError("規約に同意されていません")

    def create_group(self, user_id):
        question1 = self.cleaned_data.get("question1")
        question2 = self.cleaned_data.get("question2")
        question3 = self.cleaned_data.get("question3")
        question4 = self.cleaned_data.get("question4")
        question = (
            f"1. どこで当団体のことを知りましたか？\n{question1}\n\n"
            f"2. どのような用途で当団体のネットワークに接続しますか？\n{question2}\n\n"
            f"3. アドレスを当団体から割り当てる必要はありますか？\n{question3}\n\n"
            f"4. 情報発信しているSNS(Twitter,Facebook)やWebサイト、GitHub、成果物などがありましたら教えてください\n"
            f"{question4}"
        )
        try:
            group = Group.objects.create_group(
                question=question,
                name=self.cleaned_data["name"],
                name_jp=self.cleaned_data["name_jp"],
                postcode=self.cleaned_data["postcode"],
                address=self.cleaned_data["address"],
                address_jp=self.cleaned_data["address_jp"],
                phone=self.cleaned_data["phone"],
                country=self.cleaned_data["country"],
                contract_type=self.cleaned_data["contract"],
            )
        except Exception:
            raise ValueError("グループの登録に失敗しました(名前が被っている可能性があります)")

        try:
            user = User.objects.get(id=user_id)
            user.allow_group_add = False
            user.save()
        except Exception:
            raise ValueError("ユーザ情報の変更に失敗しました")

        try:
            UserGroup.objects.create(user=user, group=group, is_admin=True)
        except Exception:
            raise ValueError("ユーザとグループの紐づけに失敗しました")


class StudentEditForm(forms.Form):
    membership_expired_at = forms.DateField(
        label="有効期限",
        required=True,
    )
    file = forms.FileField(
        label="学生証明",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = field.label

    def create_group(self, user_id):
        try:
            group = Group.objects.create_group(
                name=self.cleaned_data["name"],
                postcode=self.cleaned_data["postcode"],
                address=self.cleaned_data["address"],
                address_en=self.cleaned_data["address_en"],
                email=self.cleaned_data["email"],
                phone=self.cleaned_data["phone"],
                country=self.cleaned_data["country"],
            )
        except Exception:
            raise ValueError("グループの登録に失敗しました(名前が被っている可能性があります。)")

        try:
            user = User.objects.get(id=user_id)
            user.group_add = False
            user.save()
        except Exception:
            raise ValueError("ユーザ情報の変更に失敗しました")

        try:
            UserGroup.objects.create(user=user, group=group, is_admin=True)
        except Exception:
            raise ValueError("ユーザとグループの紐づけに失敗しました")


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("postcode", "address_jp", "address", "phone", "country")
        labels = {
            "postcode": "郵便番号",
            "address_jp": "住所",
            "address": "住所(English)",
            "phone": "phone",
            "country": "居住国",
        }

    def __init__(self, *args, **kwargs):
        editable = kwargs.pop("editable", False)  # group_id を引数として受け取る
        super().__init__(*args, **kwargs)
        if editable:
            self.fields["postcode"].widget.attrs["disabled"] = True
            self.fields["address_jp"].widget.attrs["disabled"] = True
            self.fields["address"].widget.attrs["disabled"] = True
            self.fields["phone"].widget.attrs["disabled"] = True
            self.fields["country"].widget.attrs["disabled"] = True
        self.fields["postcode"].widget.attrs["class"] = "form-control p-postal-code"
        self.fields["address_jp"].widget.attrs["class"] = (
            "form-control p-region p-locality p-street-address p-extended-address"
        )
        self.fields["address"].widget.attrs["class"] = "form-control"
        self.fields["phone"].widget.attrs["class"] = "form-control"
        self.fields["country"].widget.attrs["class"] = "form-control p-country-name"

        for field in self.fields.values():
            field.widget.attrs["placeholder"] = field.label


class TwoAuthForm(forms.Form):
    title = forms.CharField(label="名前", max_length=100, required=True)
    code = forms.CharField(label="code", max_length=6, min_length=6, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = field.label


class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs["class"] = "form-control"
        self.fields["new_password1"].widget.attrs["class"] = "form-control"
        self.fields["new_password2"].widget.attrs["class"] = "form-control"
        self.fields["new_password1"].widget.attrs["placeholder"] = "半角英数字８文字以上"
        self.fields["new_password2"].widget.attrs["placeholder"] = "パスワード確認用"


class EmailChangeForm(forms.Form):
    email = forms.EmailField(label="メールアドレス", max_length=100, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = field.label

    def save(self, user):
        try:
            User.objects.change_email(user=user, email=self.cleaned_data["email"])
        except Exception:
            raise ValueError("更新に失敗しました")


class ProfileEditForm(forms.Form):
    username = forms.CharField(label="名前(english)", max_length=100, required=True)
    username_jp = forms.CharField(label="名前(japanese)", max_length=100, required=True)
    display_name = forms.CharField(label="display_name", max_length=150, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = field.label

    def save(self, user):
        try:
            User.objects.update_user(
                user=user,
                name=self.cleaned_data["username"],
                name_jp=self.cleaned_data["username_jp"],
                display_name=self.cleaned_data["display_name"],
            )
        except Exception:
            raise ValueError("更新に失敗しました")
