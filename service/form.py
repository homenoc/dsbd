from datetime import date, timedelta

from django import forms
from django.db import transaction

from custom_auth.models import Group
from ip.models import (
    IP,
    JPNIC_USER_TYPE_ADMIN,
    JPNIC_USER_TYPE_TECH_1,
    JPNIC_USER_TYPE_TECH_2,
    JPNIC_USER_TYPE_TECH_3,
    OWNER_TYPE_FROM_OUR,
    IPJPNICUser,
    JPNICUser,
)
from service.check import PlanCheck, ip_address_split, validate_ip_addresses
from service.models import (
    CONNECTION_TYPE_CHOICES,
    HOPE_LOCATION_CHOICES,
    NTT_CHOICES,
    ROUTE_CHOICES,
    SERVICE_L2,
    SERVICE_L3_BGP,
    SERVICE_L3_STATIC,
    SERVICE_TRANSIT,
    Connection,
    Service,
)

IPV4_SUBNET_CHOICES = (
    (None, "なし"),
    (30, "/30"),
    (29, "/29"),
    (28, "/28"),
    (27, "/27"),
)
IPV6_SUBNET_CHOICES = (
    (None, "なし"),
    (64, "/64"),
    (60, "/60"),
    (56, "/56"),
    (48, "/48"),
)

INPUT_SERVICE_CHOICES = (
    (SERVICE_L2, "L2"),
    (SERVICE_L3_STATIC, "L3 Static"),
    (SERVICE_L3_BGP, "L3 BGP"),
    (SERVICE_TRANSIT, "トランジット提供"),
)


class ServiceAddForm(forms.Form):
    service_type = forms.ChoiceField(label="1.1. サービス名", required=True, choices=INPUT_SERVICE_CHOICES)
    service_type_comment = forms.CharField(label="1.1.1. サービス(その他要望)", required=False)
    asn = forms.IntegerField(label="1.2. ASN", help_text="例) 59105", required=False)
    ipv4_address = forms.GenericIPAddressField(
        label="1.3.1. 広報するIPv4",
        required=False,
        help_text="例) xx.xx.xx.xx/23,xx.xx.xx.xx/24",
    )
    ipv6_address = forms.GenericIPAddressField(
        label="1.3.2. 広報するIPv6",
        required=False,
        help_text="例) xxxx:xxx1::1/56,xxxx:xxx2::1/56",
    )
    assign_v4_subnet = forms.ChoiceField(label="1.2.1. IPv4サブネット", choices=IPV4_SUBNET_CHOICES, required=False)
    assign_v6_subnet = forms.ChoiceField(label="1.2.2. IPv6サブネット", choices=IPV6_SUBNET_CHOICES, required=False)
    ipv4_plan = forms.CharField(
        label="1.3. IPv4アドレス利用プラン", min_length=10, required=False, widget=forms.Textarea()
    )
    ipv4_jpnic_admin = forms.ModelChoiceField(
        label="[IPv4] 管理者連絡窓口", queryset=JPNICUser.objects.none(), required=False
    )
    ipv4_jpnic_tech1 = forms.ModelChoiceField(
        label="[IPv4] 技術連絡担当者1", queryset=JPNICUser.objects.none(), required=False
    )
    ipv4_jpnic_tech2 = forms.ModelChoiceField(
        label="[IPv4] 技術連絡担当者2", queryset=JPNICUser.objects.none(), required=False
    )
    ipv4_jpnic_tech3 = forms.ModelChoiceField(
        label="[IPv4] 技術連絡担当者3", queryset=JPNICUser.objects.none(), required=False
    )
    ipv6_jpnic_admin = forms.ModelChoiceField(
        label="[IPv6] 管理者連絡窓口", queryset=JPNICUser.objects.none(), required=False
    )
    ipv6_jpnic_tech1 = forms.ModelChoiceField(
        label="[IPv6] 技術連絡担当者1", queryset=JPNICUser.objects.none(), required=False
    )
    ipv6_jpnic_tech2 = forms.ModelChoiceField(
        label="[IPv6] 技術連絡担当者2", queryset=JPNICUser.objects.none(), required=False
    )
    ipv6_jpnic_tech3 = forms.ModelChoiceField(
        label="[IPv6] 技術連絡担当者3", queryset=JPNICUser.objects.none(), required=False
    )

    start_date = forms.DateField(
        label="利用開始日",
        widget=forms.DateTimeInput(
            attrs={"type": "date", "min": (date.today() + timedelta(weeks=1)).strftime("%Y-%m-%d")}
        ),
        error_messages={"required": "このフィールドは必須です。日付を入力してください。"},
        required=True,
    )
    end_date = forms.DateField(
        label="利用終了日",
        widget=forms.DateTimeInput(
            attrs={"type": "date", "min": (date.today() + timedelta(weeks=1)).strftime("%Y-%m-%d")}
        ),
        required=False,
    )
    no_end_date = forms.BooleanField(
        label="終了日未定",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"type": "checkbox"}),
    )
    ave_upstream = forms.IntegerField(
        label="3.1. 平均アップロード帯域幅(Mbps)",
        help_text="例) 10Mbps",
        required=True,
    )
    max_upstream = forms.IntegerField(
        label="3.2. 最大アップロード帯域幅(Mbps)",
        help_text="例) 20Mbps",
        required=True,
    )
    ave_downstream = forms.IntegerField(
        label="3.3. 平均ダウンロード帯域幅(Mbps)",
        help_text="例) 10Mbps",
        required=True,
    )
    max_downstream = forms.IntegerField(
        label="3.4. 最大ダウンロード帯域幅(Mbps)",
        help_text="例) 20Mbps",
        required=True,
    )
    max_bandwidth_as = forms.CharField(
        label="3.5. 特定のASに対する大量の通信があるか教えてください(ない場合は記入不要です)",
        help_text="複数のAS番号を記載する場合は,で区切ってください",
        required=False,
    )
    comment = forms.CharField(
        label="4. その他コメントはこちら",
        help_text="この申請で補足などがあればこちらに記載してください",
        required=False,
        widget=forms.Textarea(),
    )

    def __init__(self, *args, **kwargs):
        self.group_id = kwargs.pop("group_id", None)  # group_id を引数として受け取る
        super().__init__(*args, **kwargs)
        self.fields["ipv4_jpnic_admin"].queryset = JPNICUser.objects.filter(group_id=self.group_id, version=4)
        self.fields["ipv4_jpnic_tech1"].queryset = JPNICUser.objects.filter(group_id=self.group_id, version=4)
        self.fields["ipv4_jpnic_tech2"].queryset = JPNICUser.objects.filter(group_id=self.group_id, version=4)
        self.fields["ipv4_jpnic_tech3"].queryset = JPNICUser.objects.filter(group_id=self.group_id, version=4)
        self.fields["ipv6_jpnic_admin"].queryset = JPNICUser.objects.filter(group_id=self.group_id, version=6)
        self.fields["ipv6_jpnic_tech1"].queryset = JPNICUser.objects.filter(group_id=self.group_id, version=6)
        self.fields["ipv6_jpnic_tech2"].queryset = JPNICUser.objects.filter(group_id=self.group_id, version=6)
        self.fields["ipv6_jpnic_tech3"].queryset = JPNICUser.objects.filter(group_id=self.group_id, version=6)

        for field in self.fields.values():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.help_text if field.help_text else field.label

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["addresses"] = []
        # service_typeのチェック
        service_type = cleaned_data.get("service_type")
        service_type_comment = cleaned_data.get("service_type_comment")
        if service_type == "ET00" and not service_type_comment:
            self.add_error("service_type_comment", "This field is required when ETC is selected.")
        # HomeNOC割当IPチェック
        if service_type != "IP3B":
            if not cleaned_data.get("assign_v4_subnet") and not cleaned_data.get("assign_v6_subnet"):
                self.add_error("assign_v4_subnet", "IPv4 or IPv6 Assign field is required when L2/L3/ETC is selected.")
                self.add_error("assign_v6_subnet", "IPv4 or IPv6 Assign field is required when L2/L3/ETC is selected.")
            # IPv4 Planチェック機構
            if cleaned_data.get("assign_v4_subnet"):
                ipv4_plan = cleaned_data.get("ipv4_plan")
                if not ipv4_plan:
                    self.add_error("ipv4_plan", "This field is required when IPv4 Assign is selected.")
                # csvチェック
                check_ipv4 = PlanCheck(
                    is_ipv4=True, subnet=cleaned_data.get("assign_v4_subnet"), plan=ipv4_plan
                ).check()
                if check_ipv4:
                    self.add_error("ipv4_plan", check_ipv4)
                cleaned_data["addresses"].append(
                    {
                        "version": 4,
                        "address": None,
                        "subnet": int(cleaned_data.get("assign_v4_subnet").split("/")[0]),
                        "owner": OWNER_TYPE_FROM_OUR,
                    }
                )
                self.check_jpnic(cleaned_data, version=4)
            # IPv6
            if cleaned_data.get("assign_v6_subnet"):
                cleaned_data["addresses"].append(
                    {
                        "version": 6,
                        "address": None,
                        "subnet": int(cleaned_data.get("assign_v6_subnet").split("/")[0]),
                        "owner": OWNER_TYPE_FROM_OUR,
                    }
                )
                self.check_jpnic(cleaned_data, version=6)

        # Transitユーザチェック
        if service_type == "IP3B":
            if not cleaned_data.get("asn"):
                self.add_error("asn", "This field is required when IP Transit is selected.")
            ipv4_address = cleaned_data.get("ipv4_address")
            ipv6_address = cleaned_data.get("ipv6_address")
            if not ipv4_address and not ipv6_address:
                self.add_error(
                    "ipv4_address",
                    "IPv4 or IPv6 Address field is required when IP Transit is selected.",
                )
            if ipv4_address:
                error = validate_ip_addresses(ipv4_address, 4)
                if error:
                    self.add_error("ipv4_address", "Invalid IPv4 Address.")
                cleaned_data["addresses"].extend(ip_address_split(ipv4_address, 4))
            if ipv6_address:
                error = validate_ip_addresses(ipv4_address, 6)
                if error:
                    self.add_error("ipv6_address", "Invalid IPv6 Address.")
                cleaned_data["addresses"].extend(ip_address_split(ipv6_address, 6))

        # 開始日のチェック
        start_date = cleaned_data.get("start_date")
        if start_date < date.today() + timedelta(weeks=1):
            self.add_error("start_date", "You cannot select a date in the past.")
        # 終了日のチェック
        end_date = cleaned_data.get("end_date")
        no_end_date = cleaned_data.get("no_end_date")
        if no_end_date:
            cleaned_data["end_date"] = None
        if not no_end_date and not end_date:
            raise forms.ValidationError("終了日が未定でない場合、終了日を入力してください。")
        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError("終了日は開始日以降でなければなりません。")

        return cleaned_data

    def check_jpnic(self, cleaned_data, version: int = 4):
        # JPNIC情報チェック(管理者連絡窓口)
        if not cleaned_data.get(f"ipv{version}_jpnic_admin"):
            self.add_error(f"ipv{version}_jpnic_admin", "ユーザを選択してください。")
        # JPNIC情報チェック(技術連絡担当者)
        if not cleaned_data.get(f"ipv{version}_jpnic_tech1"):
            self.add_error(f"ipv{version}_jpnic_tech1", "技術連絡担当者1の入力は必須です")
        if cleaned_data.get(f"ipv{version}_jpnic_tech1"):
            if cleaned_data.get(f"ipv{version}_jpnic_tech1") == cleaned_data.get(f"ipv{version}_jpnic_tech2"):
                self.add_error(f"ipv{version}_jpnic_tech2", "技術連絡担当者1と技術連絡担当者2のユーザが同じです")
            if cleaned_data.get(f"ipv{version}_jpnic_tech1") == cleaned_data.get(f"ipv{version}_jpnic_tech3"):
                self.add_error(f"ipv{version}_jpnic_tech3", "技術連絡担当者1と技術連絡担当者3のユーザが同じです")
        if cleaned_data.get(f"ipv{version}_jpnic_tech2") and (
            cleaned_data.get(f"ipv{version}_jpnic_tech2") == cleaned_data.get(f"ipv{version}_jpnic_tech3")
        ):
            self.add_error(f"ipv{version}_jpnic_tech3", "技術連絡担当者2と技術連絡担当者3のユーザが同じです")
        # Groupに所属しているかチェック
        if (
            cleaned_data.get(f"ipv{version}_jpnic_admin")
            and cleaned_data.get(f"ipv{version}_jpnic_admin").group_id != self.group_id
        ):
            self.add_error(f"ipv{version}_jpnic_admin", "This user does not belong to any group.")
        if (
            cleaned_data.get(f"ipv{version}_jpnic_tech1")
            and cleaned_data.get(f"ipv{version}_jpnic_tech1").group_id != self.group_id
        ):
            self.add_error(f"ipv{version}_jpnic_tech1", "This user does not belong to any group.")
        if (
            cleaned_data.get(f"ipv{version}_jpnic_tech2")
            and cleaned_data.get(f"ipv{version}_jpnic_tech2").group_id != self.group_id
        ):
            self.add_error(f"ipv{version}_jpnic_tech2", "This user does not belong to any group.")
        if (
            cleaned_data.get(f"ipv{version}_jpnic_tech3")
            and cleaned_data.get(f"ipv{version}_jpnic_tech3").group_id != self.group_id
        ):
            self.add_error(f"ipv{version}_jpnic_tech3", "This user does not belong to any group.")

    def save(self):
        cleaned_data = self.clean()
        try:
            with transaction.atomic():
                service_instance = Service.objects.create(
                    group_id=self.group_id,
                    service_type=cleaned_data["service_type"],
                    service_number=Service.objects.get_new_number(self.group_id),
                    service_comment=cleaned_data.get("service_type_comment", None),
                    asn=cleaned_data.get("asn", None),
                    start_at=cleaned_data["start_date"],
                    end_at=cleaned_data.get("end_date", None),
                    ave_upstream=cleaned_data["ave_upstream"],
                    max_upstream=cleaned_data["max_upstream"],
                    ave_downstream=cleaned_data["ave_downstream"],
                    max_downstream=cleaned_data["max_downstream"],
                    max_bandwidth_as=cleaned_data.get("max_bandwidth_as", None),
                    user_comment=cleaned_data.get("comment", None),
                )
                service_id = service_instance.id
                ip_instances = []
                # IPアドレスの保存
                ip_data = {
                    "service": service_instance,
                    "start_at": cleaned_data["start_date"],
                    "end_at": cleaned_data["end_date"],
                }
                for address in cleaned_data["addresses"]:
                    if cleaned_data["service_type"] != "IP3B" and address["version"] == 4:
                        # HomeNOC側の割当IPかつIPv4の場合はPlanを必須とする
                        ip_data["ipv4_plan"] = cleaned_data["ipv4_plan"]
                    ip_data["version"] = address["version"]
                    ip_data["ip_address"] = address["address"]
                    ip_data["subnet"] = address["subnet"]
                    ip_data["owner"] = address["owner"]
                    ip_instances.append(IP.objects.create(**ip_data))

                # IP3B以外の場合、IPとJPNICの紐づけを行う
                if cleaned_data["service_type"] != "IP3B":
                    for ip in ip_instances:
                        IPJPNICUser.objects.create(
                            ip_id=ip.id,
                            jpnic_user=cleaned_data[f"ipv{ip.version}_jpnic_admin"],
                            user_type=JPNIC_USER_TYPE_ADMIN,
                        )
                        IPJPNICUser.objects.create(
                            ip_id=ip.id,
                            jpnic_user=cleaned_data[f"ipv{ip.version}_jpnic_tech1"],
                            user_type=JPNIC_USER_TYPE_TECH_1,
                        )
                        if cleaned_data[f"ipv{ip.version}_jpnic_tech2"]:
                            IPJPNICUser.objects.create(
                                ip_id=ip.id,
                                jpnic_user=cleaned_data[f"ipv{ip.version}_jpnic_tech2"],
                                user_type=JPNIC_USER_TYPE_TECH_2,
                            )
                        if cleaned_data[f"ipv{ip.version}_jpnic_tech3"]:
                            IPJPNICUser.objects.create(
                                ip_id=ip.id,
                                jpnic_user=cleaned_data[f"ipv{ip.version}_jpnic_tech3"],
                                user_type=JPNIC_USER_TYPE_TECH_3,
                            )

                group = Group.objects.get(id=self.group_id)
                group.allow_service_add = False
                group.allow_jpnic_add = False
                group.save()
        except Exception as e:
            # エラーログの出力や追加処理
            print(f"エラーが発生しました: {e}")
            raise  # 必要に応じて例外を再度発生させる


class ConnectionAddForm(forms.Form):
    connection_type = forms.ChoiceField(label="1. 接続方式", required=True, choices=CONNECTION_TYPE_CHOICES)
    connection_comment = forms.CharField(label="1.1. 接続情報コメント", required=False)
    ipv4_route = forms.ChoiceField(label="1.2.1. IPv4 BGP広報経路", required=False, choices=ROUTE_CHOICES)
    ipv4_route_comment = forms.CharField(label="1.2.1.1. IPv4 BGP広報経路(その他コメント)", required=False)
    ipv6_route = forms.ChoiceField(label="1.2.2. IPv6 BGP広報経路", required=False, choices=ROUTE_CHOICES)
    ipv6_route_comment = forms.CharField(label="1.2.2.1. IPv6 BGP広報経路(その他コメント)", required=False)
    hope_location = forms.ChoiceField(label="2.1. 接続希望場所", choices=HOPE_LOCATION_CHOICES, required=True)
    term_location = forms.CharField(label="2.2. 終端先ユーザの市町村", required=True)
    term_ip = forms.GenericIPAddressField(label="2.3. 終端IPアドレス", required=False, help_text="例) xxxx:xxx1::1")
    ntt_type = forms.ChoiceField(
        label="2.4. 接続終端場所にNTTフレッツ光が利用可能かをお知らせください",
        required=False,
        choices=NTT_CHOICES,
    )
    ntt_comment = forms.CharField(label="2.4.1. 接続終端場所のコメント", required=False)
    start_date = forms.DateField(
        label="3.1.利用開始日",
        widget=forms.DateTimeInput(
            attrs={"type": "date", "min": (date.today() + timedelta(weeks=1)).strftime("%Y-%m-%d")}
        ),
        error_messages={"required": "このフィールドは必須です。日付を入力してください。"},
        required=True,
    )
    end_date = forms.DateField(
        label="3.2.利用終了日",
        widget=forms.DateTimeInput(
            attrs={"type": "date", "min": (date.today() + timedelta(weeks=1)).strftime("%Y-%m-%d")}
        ),
        required=False,
    )
    no_end_date = forms.BooleanField(
        label="終了日未定",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"type": "checkbox"}),
    )
    is_monitor = forms.BooleanField(
        label="4. 監視の有無",
        help_text="当団体によるネットワーク監視をご希望の場合はチェックを入れて下さい",
        required=False,
    )
    comment = forms.CharField(
        label="5. その他コメントはこちら",
        help_text="この申請で補足などがあればこちらに記載してください",
        required=False,
        widget=forms.Textarea(),
    )

    def __init__(self, *args, **kwargs):
        self.group_id = kwargs.pop("group_id", None)
        self.service_id = kwargs.pop("service_id", None)
        self.is_ipv4_bgp = kwargs.pop("is_ipv4_bgp", None)
        self.is_ipv6_bgp = kwargs.pop("is_ipv6_bgp", None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.help_text if field.help_text else field.label

    def clean(self):
        cleaned_data = super().clean()
        connection_type = cleaned_data.get("connection_type")

        if connection_type == "ETC" and not cleaned_data.get("connection_comment"):
            self.add_error("connection_type", "This field is required when ETC is selected.")
        if connection_type != "CC0":
            if not cleaned_data.get("term_ip"):
                self.add_error("term_ip", "This field is required.")
            if not cleaned_data.get("ntt_type"):
                self.add_error("ntt_type", "This field is required.")

        if self.is_ipv4_bgp:
            if not cleaned_data.get("ipv4_route"):
                self.add_error("ipv4_route", "This field is required when IPv4 BGP is selected.")
            if cleaned_data.get("ipv4_route") == "ETC" and not cleaned_data.get("ipv4_route_comment"):
                self.add_error("ipv4_route_comment", "This field is required when ETC is selected.")
        if self.is_ipv6_bgp:
            if not cleaned_data.get("ipv6_route"):
                self.add_error("ipv6_route", "This field is required when IPv6 BGP is selected.")
            if cleaned_data.get("ipv6_route") == "ETC" and not cleaned_data.get("ipv6_route_comment"):
                self.add_error("ipv6_route_comment", "This field is required when ETC is selected.")

        # 開始日のチェック
        start_date = cleaned_data.get("start_date")
        if start_date < date.today() + timedelta(weeks=1):
            self.add_error("start_date", "You cannot select a date in the past.")
        # 終了日のチェック
        end_date = cleaned_data.get("end_date")
        no_end_date = cleaned_data.get("no_end_date")
        if no_end_date:
            cleaned_data["end_date"] = None
        if not no_end_date and not end_date:
            raise forms.ValidationError("終了日が未定でない場合、終了日を入力してください。")
        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError("終了日は開始日以降でなければなりません。")

        return cleaned_data

    def save(self):
        cleaned_data = self.clean()
        try:
            with transaction.atomic():
                Connection.objects.create(
                    service_id=self.service_id,
                    connection_type=cleaned_data["connection_type"],
                    connection_number=Connection.objects.get_new_number(self.service_id),
                    connection_comment=cleaned_data.get("connection_comment", None),
                    ipv4_route=cleaned_data.get("ipv4_route", None),
                    ipv4_route_comment=cleaned_data.get("ipv4_route_comment", None),
                    ipv6_route=cleaned_data.get("ipv6_route", None),
                    ipv6_route_comment=cleaned_data.get("ipv6_route_comment", None),
                    tunnel_ip=cleaned_data.get("asn", None),
                    hope_location=cleaned_data.get("hope_location", None),
                    term_location=cleaned_data.get("term_location", None),
                    ntt_type=cleaned_data.get("ntt_type", None),
                    ntt_comment=cleaned_data.get("ntt_comment", None),
                    start_at=cleaned_data["start_date"],
                    end_at=cleaned_data.get("end_date", None),
                    is_monitor=cleaned_data.get("is_monitor", False),
                    user_comment=cleaned_data.get("comment", None),
                )

                service = Service.objects.get(id=self.service_id)
                service.allow_connection_add = False
                service.save()
        except Exception as e:
            # エラーログの出力や追加処理
            print(f"エラーが発生しました: {e}")
            raise  # 必要に応じて例外を再度発生させる
