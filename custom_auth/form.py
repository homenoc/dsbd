from django import forms

from custom_auth.models import User, UserGroup, Group


class GroupForm(forms.Form):
    name = forms.CharField(label="グループ名", max_length=150, required=True)
    zipcode = forms.CharField(label="郵便番号", max_length=10, required=True)
    address = forms.CharField(label="住所", max_length=250, required=True)
    address_en = forms.CharField(label="住所(English)", max_length=250, required=True)
    email = forms.EmailField(label="email", max_length=250, required=True)
    phone = forms.CharField(label="phone", max_length=30, required=True)
    country = forms.CharField(label="居住国", max_length=30, initial="Japan", required=True)

    def __init__(self, edit=False, disable=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if edit:
            self.fields['name'].widget.attrs['readonly'] = True
            if disable:
                self.fields['zipcode'].widget.attrs['disabled'] = True
                self.fields['address'].widget.attrs['disabled'] = True
                self.fields['address_en'].widget.attrs['disabled'] = True
                self.fields['email'].widget.attrs['disabled'] = True
                self.fields['phone'].widget.attrs['disabled'] = True
                self.fields['country'].widget.attrs['disabled'] = True
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['zipcode'].widget.attrs['class'] = 'form-control p-postal-code'
        self.fields['address'].widget.attrs[
            'class'] = 'form-control p-region p-locality p-street-address p-extended-address'
        self.fields['address_en'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['phone'].widget.attrs['class'] = 'form-control'
        self.fields['country'].widget.attrs['class'] = 'form-control p-country-name'

        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label

    def create_group(self, user_id):
        try:
            group = Group.objects.create_group(
                name=self.cleaned_data["name"],
                zipcode=self.cleaned_data["zipcode"],
                address=self.cleaned_data["address"],
                address_en=self.cleaned_data["address_en"],
                email=self.cleaned_data["email"],
                phone=self.cleaned_data["phone"],
                country=self.cleaned_data["country"]
            )
        except:
            raise ValueError("グループの登録に失敗しました(名前が被っている可能性があります。)")

        try:
            user = User.objects.get(id=user_id)
            user.group_add = False
            user.save()
        except:
            raise ValueError("ユーザ情報の変更に失敗しました")

        try:
            UserGroup.objects.create(user=user, group=group, is_admin=True)
        except:
            raise ValueError("ユーザとグループの紐づけに失敗しました")

    def update_group(self, group_id):
        try:
            group = Group.objects.get(id=group_id)
            group.zipcode = self.cleaned_data["zipcode"]
            group.address = self.cleaned_data["address"]
            group.address_en = self.cleaned_data["address_en"]
            group.email = self.cleaned_data["email"]
            group.phone = self.cleaned_data["phone"]
            group.country = self.cleaned_data["country"]
            group.save()
        except:
            raise ValueError("グループの更新に失敗しました")


class TwoAuthForm(forms.Form):
    title = forms.CharField(label="名前", max_length=100, required=True)
    code = forms.CharField(label="code", max_length=6, min_length=6, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
