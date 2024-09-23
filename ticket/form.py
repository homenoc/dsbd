from django import forms


class TicketForm(forms.Form):
    ticket_type = forms.fields.ChoiceField(
        label="チケットの種別(User or Group)を選んでください",
        required=True,
    )
    title = forms.CharField(label="タイトル", max_length=250, required=True)
    body = forms.CharField(label="内容", widget=forms.Textarea(attrs={"cols": "80", "rows": "10"}), required=True)

    def __init__(self, groups, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = field.label

        ticket_type_template = [("user", "ユーザチケット")]
        if groups.exists():
            for group in groups:
                ticket_type_template.append(
                    (str(group.id), "グループチケット (Group" + str(group.id) + ": " + group.name + ")")
                )
        self.fields["ticket_type"].choices = ticket_type_template
