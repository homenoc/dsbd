from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ip.form import JPNICForm
from ip.models import JPNICUser


@login_required
def jpnic_add(request, group_id):
    is_administrator = request.user.usergroup_set.filter(group_id=group_id, user=request.user, is_admin=True).exists()
    if not is_administrator:
        return render(request, "error.html", {"text": "権限がありません"})
    if not request.user.groups.get(id=group_id).allow_jpnic_add:
        return render(request, "error.html", {"error": "JPNIC情報の新規申請が許可されていません"})
    if request.method == "POST":
        form = JPNICForm(request.POST, group_id=group_id)
        if form.is_valid():
            form.save()  # フォームからモデルインスタンスを保存
            return render(request, "done.html", {"text": "登録・変更が完了しました"})  # 保存後にリダイレクト
    else:
        form = JPNICForm()

    context = {"form": form}
    return render(request, "ip/jpnic_add.html", context)


def jpnic_edit(request, group_id, jpnic_id):
    is_administrator = request.user.usergroup_set.filter(group_id=group_id, user=request.user, is_admin=True).exists()
    if not is_administrator:
        return render(request, "error.html", {"text": "権限がありません"})
    jpnic_user = get_object_or_404(JPNICUser, pk=jpnic_id)
    if not jpnic_user.is_pass:
        return render(request, "error.html", {"text": "未審査のため変更できません"})
    if request.method == "POST":
        # フォームにPOSTされたデータを与える
        form = JPNICForm(request.POST, instance=jpnic_user)
        if form.is_valid():
            # データベースを更新
            form.save(group_id=group_id)
            return redirect("jpnic_index")  # 編集完了後、リダイレクト
    else:
        # フォームに現在のデータを与えて表示する
        form = JPNICForm(instance=jpnic_user)

    context = {
        "form": form,
    }
    return render(request, "ip/jpnic_edit.html", context)


@login_required
def jpnic_index(request, group_id):
    is_administrator = request.user.usergroup_set.filter(group_id=group_id, user=request.user, is_admin=True).exists()
    if not is_administrator:
        return render(request, "error.html", {"text": "権限がありません"})
    jpnic_users = JPNICUser.objects.filter(group=group_id).select_related("group").order_by("id")
    context = {"jpnic_users": jpnic_users}
    return render(request, "ip/jpnic_index.html", context)
