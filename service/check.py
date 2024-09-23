import csv
import ipaddress

from ip.models import OWNER_TYPE_FROM_YOUR


class PlanCheck:
    def __init__(self, is_ipv4: bool, subnet: str, plan: str):
        self.is_ipv4: bool = is_ipv4
        self.subnet: int = int(subnet.split("/")[-1])
        self.plan: str = plan

    def check(self):
        if self.is_ipv4:
            return self.check_ipv4()
        else:
            return self.check_ipv6()

    def check_ipv4(self):
        address_count = pow(2, 32 - self.subnet)
        enable_address = address_count - 2
        sum_after = 0
        sum_after_half_year = 0
        sum_after_year = 0
        error = ""
        for plan in self.read_csv():
            server_name = plan[0]
            after = int(plan[1])  # 25%以上
            after_half_year = int(plan[2])  # 50%以上
            after_year = int(plan[3])  # 75%以上
            etc = None
            if len(plan) == 5:
                etc = plan[4]
            sum_after += after
            sum_after_half_year += after_half_year
            sum_after_year += after_year
        if sum_after > enable_address:
            error += "直後: 有効アドレス数を超えています,"
        if sum_after_half_year > enable_address:
            error += "半年後: 有効アドレス数を超えています,"
        if sum_after_year > enable_address:
            error += "1年後: 有効アドレス数を超えています,"
        if sum_after <= int(enable_address * 0.25):
            error += "直後: 25%以上のアドレスが必要です,"
        if sum_after_half_year <= int(enable_address * 0.5):
            error += "半年後: 50%以上のアドレスが必要です,"
        if sum_after_year <= int(enable_address * 0.75):
            error += "1年後: 75%以上のアドレスが必要です,"

        if error == "":
            return None

        return error

    def check_ipv6(self):
        pass

    def read_csv(self):
        return csv.reader(self.plan.split("\n"))


def validate_ip_addresses(ip_address_str: str, version: int) -> str or None:
    error = None
    ip_array = ip_address_str.split(",")
    for ip in ip_array:
        ip = ip.strip()  # スペースを取り除く
        if "/" not in ip:
            error = "Invalid IP Address."
        else:
            try:
                if version == 4:
                    ipaddress.IPv4Address(ip)
                elif version == 6:
                    ipaddress.IPv6Address(ip)
            except ipaddress.AddressValueError:
                error = "Invalid IP Address."
    return error


def ip_address_split(ip_addresses_str: str, ip_version: int) -> list:
    ip_addresses = ip_addresses_str.split(",")
    addresses = []
    for ip_address in ip_addresses:
        ip, mask = ip_address.split("/")
        addresses.append({"version": ip_version, "address": ip, "subnet": int(mask), "owner": OWNER_TYPE_FROM_YOUR})

    return addresses
