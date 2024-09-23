from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.db.models import Q
from django.shortcuts import render

from ip.models import IP
from service.form import ConnectionAddForm, ServiceAddForm
from service.models import Service


@login_required
def service_add(request, group_id: int):
    is_administrator = request.user.usergroup_set.filter(group_id=group_id, user=request.user, is_admin=True).exists()
    if not is_administrator:
        return render(request, "error.html", {"error": "権限がありません"})
    if not request.user.groups.get(id=group_id).allow_service_add:
        return render(request, "error.html", {"error": "サービスの新規申請が許可されていません"})
    form = ServiceAddForm(data=request.POST or None, group_id=group_id)
    # if not request.user.allow_group_add:
    # error = "グループの新規登録が申請不可能です"
    if request.method == "POST":
        # print(form.errors)
        if "update_jpnic_users" in request.POST:
            print("update jpnic users")
        elif form.is_valid():
            form.save()
            return render(request, "done.html", {"text": "登録・変更が完了しました"})
    context = {"form": form, "group_id": group_id}
    return render(request, "service/add.html", context)


@login_required
def service_index(request, group_id=None):
    # TODO: 修正必要あり(dsbd/views.pyを参照)
    user_group_ids = list(request.user.groups.values_list("id", flat=True))
    q = Q()
    for user_group_id in user_group_ids:
        q.add(Q(group=user_group_id), Q.OR)
    services = Service.objects.filter(is_active=True).filter(q).order_by("id")
    per_page = int(request.GET.get("per_page", "20"))
    page = int(request.GET.get("page", "1"))
    paginator = Paginator(services, per_page)
    try:
        services = paginator.page(page)
    except (EmptyPage, InvalidPage):
        services = paginator.page(paginator.num_pages)

    context = {"services": services, "group_id": group_id}
    return render(request, "service/index.html", context)


@login_required
def connection_add(request, group_id: int, service_id: int):
    is_administrator = request.user.usergroup_set.filter(group_id=group_id, user=request.user, is_admin=True).exists()
    if not is_administrator:
        return render(request, "error.html", {"error": "権限がありません"})
    service = Service.objects.get(id=service_id)
    if not service.allow_connection_add:  # 接続情報の新規申請許可チェック
        return render(request, "error.html", {"error": "接続情報の新規申請が許可されていません"})
    if not service.is_pass:  # サービスが審査済みであるかチェック
        return render(request, "error.html", {"error": "サービス側の審査が終わっていません"})
    service_code = service.__str__()
    # BGP接続があるかどうかチェック
    is_ipv4_bgp = False
    is_ipv6_bgp = False
    for ip in IP.objects.filter(service=service, is_pass=True):
        match ip.version:
            case 4:
                is_ipv4_bgp = True
            case 6:
                is_ipv6_bgp = True
    form = ConnectionAddForm(
        data=request.POST or None,
        group_id=group_id,
        service_id=service_id,
        is_ipv4_bgp=is_ipv4_bgp,
        is_ipv6_bgp=is_ipv6_bgp,
    )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return render(request, "done.html", {"text": "登録・変更が完了しました"})
    context = {
        "form": form,
        "group_id": group_id,
        "service_code": f"{service_code}",
        "is_ipv4_bgp": is_ipv4_bgp,
        "is_ipv6_bgp": is_ipv6_bgp,
    }
    return render(request, "connection/add.html", context)
