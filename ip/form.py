from django import forms
from django_countries.fields import CountryField

from ip.models import JPNICUser


class JPNICForm(forms.ModelForm):
    class Meta:
        model = JPNICUser
        fields = (
            "version",
            "handle_type",
            "jpnic_handle",
            "name_jp",
            "name",
            "email",
            "org_jp",
            "org",
            "postcode",
            "address_jp",
            "address",
            "dept_jp",
            "dept",
            "title_jp",
            "title",
            "tel",
            "fax",
            "country",
        )

    def __init__(self, *args, **kwargs):
        self.group_id = kwargs.pop("group_id", None)  # group_id を引数として受け取る
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.help_text if field.help_text else field.label

    def save(self):
        instance = super().save(commit=False)
        instance.group_id = self.group_id
        instance.save()
        return instance


class JPNICAddForm(forms.Form):
    jpnic_handle = forms.CharField(label="JPNIC Handle", required=False)
    name_jp = forms.CharField(label="1. グループ名/名前", required=False)
    name = forms.CharField(label="2. グループ名/名前(English)", required=False)
    email = forms.EmailField(label="3. E-Mail", required=False)
    org_jp = forms.CharField(label="4. 組織名", required=False)
    org = forms.CharField(label="5. 組織名(English)", required=False)
    postcode = forms.CharField(label="6. 郵便番号", required=False)
    address_jp = forms.CharField(label="7. 住所", required=False)
    address = forms.CharField(label="8. 住所(English)", required=False)
    dept_jp = forms.CharField(label="9. 部署", required=False)
    dept = forms.CharField(label="10. 部署(English)", required=False)
    title_jp = forms.CharField(label="11. 役職", required=False)
    title = forms.CharField(label="12. 役職(English)", required=False)
    tel = forms.CharField(label="13. Tel", max_length=30, required=True)
    fax = forms.CharField(label="14. Fax", max_length=30, required=True)
    country = CountryField().formfield(label="15. 居住国", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.help_text if field.help_text else field.label

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data
