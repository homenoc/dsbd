import base64
import time
from io import BytesIO

import pyotp
import qrcode
import stripe
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from custom_auth.form import TwoAuthForm, GroupForm, MyPasswordChangeForm, EmailChangeForm, ProfileEditForm
from custom_auth.models import TOTPDevice, UserGroup
from dsbd import settings


@login_required
def index(request):
    context = {}
    return render(request, "user/profile.html", context)


@login_required
def password_change(request):
    form = MyPasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return render(request, "done.html", {'text': "パスワードの変更を行いました"})
    context = {'form': form}
    return render(request, "user/change_password.html", context)


@login_required
def change_email(request):
    form = EmailChangeForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save(user=request.user)
            return render(request, "done.html", {'text': "メールアドレスの変更を行いました"})
    return render(request, "user/change_email.html", {'form': form})


@login_required
def edit_profile(request):
    form = ProfileEditForm(data=request.POST or None)
    userdata = {
        "username": request.user.username,
        "username_jp": request.user.username_jp,
        "display_name": request.user.display_name,
    }
    if request.method == 'POST':
        if form.is_valid():
            form.save(user=request.user)
            return render(request, "done.html", {'text': "プロフィールの変更を行いました"})
    else:
        form = ProfileEditForm(initial=userdata)

    return render(request, "user/edit_form.html", {'form': form})


@login_required
def add_two_auth(request):
    error = None
    initial_check = TOTPDevice.objects.check_max_totp_device(user=request.user)
    secret = TOTPDevice.objects.generate_secret()
    form = TwoAuthForm()
    buffer = BytesIO()
    qrcode.make(secret.get('url')).save(buffer)
    qr = base64.b64encode(buffer.getvalue()).decode().replace("'", "")
    if request.method == 'POST':
        id = request.POST.get('id', 0)
        if id == 'submit' and initial_check:
            form = TwoAuthForm(request.POST)
            otp_secret = request.POST.get("secret")
            if form.is_valid():
                code = form.cleaned_data['code']
                verify_code = pyotp.TOTP(otp_secret).verify(code)
                if verify_code:
                    TOTPDevice.objects.create_secret(
                        user=request.user,
                        title=form.cleaned_data['title'],
                        otp_secret=otp_secret
                    )
                    return redirect("custom_auth:list_two_auth")
                else:
                    error = "コードが一致しません"
            else:
                error = "request error"
        else:
            error = "request error"

    context = {
        'initial_check': initial_check,
        'secret': secret.get('secret'),
        'url': secret.get('url'),
        'qr': qr,
        'form': form,
        'error': error
    }

    return render(request, "user/two_auth/add.html", context)


@login_required
def list_two_auth(request):
    if request.method == 'POST':
        id = request.POST.get('id', 0)
        device_id = int(request.POST.get('device_id', 0))
        if id == 'delete':
            TOTPDevice.objects.remove(id=device_id, user=request.user)
    context = {'devices': TOTPDevice.objects.list(user=request.user)}
    return render(request, "user/two_auth/list.html", context)


@login_required
def list_groups(request):
    data = []
    for group in request.user.groups.all():
        data.append({
            "group": group,
            "administrator": group.usergroup_set.filter(user=request.user, is_admin=True).exists()
        })

    if request.method == "POST":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        id = request.POST.get("id", "")
        group_id = request.POST.get("group_id", 0)
        group = request.user.groups.get(id=group_id)
        administrator = group.usergroup_set.filter(user=request.user, is_admin=True).exists()
        if administrator and id == "create_stripe_customer":
            name = "[GROUP] %d: %s" % (int(group_id), group.name,)
            if not group.stripe_customer_id:
                cus = stripe.Customer.create(
                    name=name,
                    description="doornoc_service",  # TODO: change description
                    metadata={
                        'id': "doornoc_service",  # TODO: change description
                        'user_id': request.user.id,
                        'group_id': group_id
                    }
                )
                group.stripe_customer_id = cus.id
                group.save()
                redirect_url = "/group/%d/payment" % (int(group_id),)
                return redirect(redirect_url)
        elif administrator and id == "getting_portal":
            if group.stripe_customer_id:
                session = stripe.billing_portal.Session.create(
                    customer=group.stripe_customer_id,
                    return_url=settings.DOMAIN_URL + "/group"
                )
                return redirect(session.url, code=303)

    context = {
        "data": data
    }
    return render(request, "group/index.html", context)


@login_required
def group_add(request):
    error = None
    if request.method == 'POST':
        form = GroupForm(data=request.POST)
        if not request.user.add_group:
            error = "グループの新規登録が申請不可能です"
        elif form.is_valid():
            try:
                form.create_group(user_id=request.user.id)
                return render(request, "group/success.html", {})
            except ValueError as err:
                error = err
    else:
        form = GroupForm()
    context = {
        "form": form,
        "error": error
    }
    return render(request, "group/add.html", context)


@login_required
def group_edit(request, group_id):
    error = None
    administrator = False
    try:
        group = request.user.groups.get(id=group_id)
        group_data = {
            "name": group.name,
            "zipcode": group.zipcode,
            "address": group.address,
            "address_en": group.address_en,
            "email": group.email,
            "phone": group.phone,
            "country": group.country,
        }
        administrator = group.usergroup_set.filter(user=request.user, is_admin=True).exists()
        if request.method == 'POST' and administrator and group.is_active:
            form = GroupForm(data=request.POST)
            if form.is_valid():
                try:
                    form.update_group(group_id=group.id)
                    return render(request, "group/success.html", {})
                except ValueError as err:
                    error = err
        else:
            form = GroupForm(initial=group_data, edit=True, disable=not group.is_active)
    except:
        group = None
        form = None

    context = {
        "form": form,
        "group": group,
        "administrator": administrator,
        "error": error
    }
    return render(request, "group/edit.html", context)


@login_required
def group_permission(request, group_id):
    error = None
    administrator = False
    permission_all = False
    try:
        group = request.user.groups.get(id=group_id)
        permission_all = group.usergroup_set.all()
        administrator = group.usergroup_set.filter(user=request.user, is_admin=True).exists()
        if request.method == 'POST' and administrator and group.is_active:
            id = request.POST.get('id', 0)
            is_exists = False
            for permission_user in permission_all:
                if permission_user.id == int(id):
                    is_exists = True
                    break
            if not is_exists:
                error = "変更権限がありません"
            else:
                try:
                    user_group = UserGroup.objects.get(id=int(id))
                    if "no_admin" in request.POST:
                        user_group.is_admin = False
                        user_group.save()
                    elif "admin" in request.POST:
                        user_group.is_admin = True
                        user_group.save()
                    return redirect('/group/permission/%d' % group_id)
                except:
                    error = "アップデート処理でエラーが発生しました"
    except:
        group = None

    context = {
        "group": group,
        "permission": permission_all,
        "administrator": administrator,
        "error": error
    }
    return render(request, "group/edit_permission.html", context)


@login_required
def group_payment(request, group_id):
    error = None
    administrator = False
    permission_all = False
    data = []
    try:
        group = request.user.groups.get(id=group_id)
        permission_all = group.usergroup_set.all()
        administrator = group.usergroup_set.filter(user=request.user, is_admin=True).exists()

        stripe.api_key = settings.STRIPE_SECRET_KEY
        products = stripe.Product.search(
            query="active:'true' AND metadata['id']:'doornoc_service'",
        )
        if administrator:
            for product in products:
                prices = stripe.Price.search(
                    query="active:'true' AND product:'%s'" % (product.id,),
                )
                tmp_prices = []
                idx_prices = 0
                for price in prices:
                    tmp_price = [{
                        "id": price.id,
                        "interval": price.recurring.interval,
                        "amount": price.unit_amount,
                        "description": price.nickname
                    }]
                    if idx_prices == 0:
                        tmp_prices = tmp_price
                    else:
                        if price.recurring.interval == "year":
                            tmp_prices += tmp_price
                        elif price.recurring.interval == "month":
                            tmp_prices = tmp_price + tmp_prices
                    idx_prices += 1
                data.append({
                    "name": product.name,
                    "prices": tmp_prices,
                    "number": int(product.metadata.tag)
                })
            data.sort(key=lambda x: x['number'])
    except:
        group = None
    if administrator and request.method == "POST":
        id = request.POST.get("price_id", "")
        is_exists = False
        for one_data in data:
            for price in one_data["prices"]:
                if price["id"] == id:
                    is_exists = True
                    break
        url = settings.DOMAIN_URL + "/group"
        if is_exists and group.stripe_customer_id and not group.stripe_subscription_id:
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[
                    {
                        "price": id,
                        "quantity": 1,
                    },
                ],
                customer=group.stripe_customer_id,
                success_url=url,
                cancel_url=url,
                expires_at=int(time.time() + (60 * 30)),
                subscription_data={
                    "metadata": {
                        "type": "doornoc_membership",
                        "group_id": group_id,
                        "log": "[" + str(group.id) + "] " + group.name,
                    }
                }
            )
            return redirect(session.url, code=303)

    context = {
        "data": data,
        "group": group,
        "permission": permission_all,
        "administrator": administrator,
        "error": error
    }
    return render(request, "group/payment.html", context)
