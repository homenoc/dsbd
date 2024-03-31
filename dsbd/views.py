import time
from datetime import datetime
import stripe
from django.conf import settings
from django.contrib.auth import logout as user_logout, login as user_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from custom_auth.models import UserActivateToken, User, Group, UserEmailVerify, TOTPDevice
from dsbd import settings
from dsbd.form import LoginForm, OTPForm, SignUpForm, ForgetForm, NewSetPasswordForm

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from dsbd.notify import notice_payment
from notice.models import Notice


def sign_in(request):
    if request.user.is_authenticated:
        request.session.clear()
    auth_type = 'auth'
    invalid_code = False
    if request.method == 'POST':
        auth_type = request.POST.get("id", "auth")
        if auth_type == 'auth':
            form = LoginForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                if user:
                    request.session["user"] = user.id
                    auth_type = 'otp'
        elif auth_type == 'otp':
            form = OTPForm()
            auth_type = request.POST.get("otp_id", "auth_otp_email")
            print(request.session.get('user'))
            if auth_type == "auth_otp_email":
                user = User.objects.get(id=int(request.session.get('user')))
                UserEmailVerify.objects.create_token(user=user)
            elif auth_type == 'auth_totp':
                user = User.objects.get(id=int(request.session.get('user')))
                if not TOTPDevice.objects.filter(user=user, is_active=True).exists():
                    invalid_code = 'TOTPデバイスが登録されていません。'

        elif auth_type == 'auth_otp_email':
            form = OTPForm(request.POST)
            if form.is_valid():
                user = User.objects.get(id=int(request.session.get('user')))
                is_exists = UserEmailVerify.objects.check_token(user_id=user.id, token=form.cleaned_data["token"])
                if is_exists:
                    user_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect("/")
            form = OTPForm()
            invalid_code = True
        elif auth_type == 'auth_totp':
            form = OTPForm(request.POST)
            if form.is_valid():
                user = User.objects.get(id=int(request.session.get('user')))
                is_exists = TOTPDevice.objects.check_totp(user=user, code=form.cleaned_data["token"])
                if is_exists:
                    user_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect("/")
            form = OTPForm()
            invalid_code = True
        else:
            form = LoginForm()
            request.session.clear()

    else:
        form = LoginForm()
        request.session.clear()
    context = {'type': auth_type, 'form': form, }
    if invalid_code:
        context['invalid_code'] = '認証コードが一致しません'
    return render(request, "sign_in.html", context)


@login_required
def sign_out(request):
    user_logout(request)
    context = {}
    return render(request, "sign_out.html", context)


def sign_up(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.create_user()
            return redirect("sign_up_done")
    context = {'form': form, }

    return render(request, "sign_up.html", context)


def sign_up_done(request):
    return render(request, "sign_up_success.html", {})


class PasswordReset(PasswordResetView):
    subject_template_name = 'mail/password_reset/subject.txt'
    email_template_name = 'mail/password_reset/message.txt'
    template_name = 'forget.html'
    form_class = ForgetForm
    success_url = reverse_lazy('password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    template_name = 'forget_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = NewSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'forget_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'forget_complete.html'


def activate_user(request, activate_token):
    message = 'ユーザーのアクティベーションが完了しました'
    try:
        UserActivateToken.objects.activate_user_by_token(activate_token)
    except ValueError as error:
        message = error
    except:
        message = 'エラーが発生しました。管理者に問い合わせてください'
    return render(request, "activate.html", {"message": message})


@login_required
def index(request):
    notice_objects = Notice.objects.get_notice()
    # ticket_objects = Ticket.objects.get_ticket(user=request.user).filter(is_solved=False)

    notice_paginator = Paginator(notice_objects, int(request.GET.get("notice_per_page", "3")))
    notice_page = int(request.GET.get("notice_page", "1"))
    try:
        notices = notice_paginator.page(notice_page)
    except (EmptyPage, InvalidPage):
        notices = notice_paginator.page(notice_paginator.num_pages)

    # ticket_paginator = Paginator(ticket_objects, int(request.GET.get("ticket_per_page", "3")))
    # ticket_page = int(request.GET.get("ticket_page", "1"))
    # try:
    #     tickets = ticket_paginator.page(ticket_page)
    # except (EmptyPage, InvalidPage):
    #     tickets = ticket_paginator.page(ticket_paginator.num_pages)

    services = None

    # group_filter = request.user.groups.filter(is_active=True)
    # if group_filter.exists():
    #     service_objects = Service.objects.get_service(groups=group_filter.all()).filter(is_active=True)
    #     service_paginator = Paginator(service_objects, int(request.GET.get("ticket_per_page", "3")))
    #     service_page = int(request.GET.get("ticket_page", "1"))
    #     try:
    #         services = service_paginator.page(service_page)
    #     except (EmptyPage, InvalidPage):
    #         services = service_paginator.page(service_paginator.num_pages)

    if request.method == "POST":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        id = request.POST.get("id", "")
        if id == "create_stripe_customer":
            if not request.user.stripe_customer_id:
                cus = stripe.Customer.create(
                    name="[USER] %d: %s" % (request.user.id, request.user.username,),
                    description="dashboard_user",
                    metadata={
                        'id': "dashboard_user",
                        'user_id': request.user.id
                    }
                )
                request.user.stripe_customer_id = cus.id
                request.user.save()
                return redirect('/payment')
        elif id == "getting_portal":
            if request.user.stripe_customer_id:
                session = stripe.billing_portal.Session.create(
                    customer=request.user.stripe_customer_id,
                    return_url=settings.DOMAIN_URL
                )
                return redirect(session.url, code=303)

    context = {
        "notices": notices,
        # "tickets": tickets,
        "services": services
    }
    return render(request, "home.html", context)


@login_required
def menu(request):
    return render(request, "menu.html", {})


@login_required
def payment(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    products = stripe.Product.search(
        query="active:'true' AND metadata['id']:'corporate'",
    )
    prices = stripe.Price.search(
        query="active:'true' AND product:'" + products.data[0].id + "'",
    )
    data = {"name": products.data[0].name, "prices": []}
    index = 0
    for price in prices:
        tmp = [{
            "id": price.id,
            "interval": price.recurring.interval,
            "amount": price.unit_amount,
            "description": price.nickname
        }]
        if index == 0:
            data["prices"] = tmp
        else:
            if price.recurring.interval == "year":
                data["prices"] += tmp
            elif price.recurring.interval == "month":
                data["prices"] = tmp + data["prices"]
        index += 1
    # print(prices)
    if request.method == "POST":
        id = request.POST.get("price_id", "")
        is_exists = False
        for price in data["prices"]:
            if price["id"] == id:
                is_exists = True
                break
        if is_exists and request.user.stripe_customer_id and not request.user.stripe_subscription_id:
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[
                    {
                        "price": id,
                        "quantity": 1,
                    },
                ],
                customer=request.user.stripe_customer_id,
                success_url=settings.DOMAIN_URL,
                cancel_url=settings.DOMAIN_URL,
                expires_at=int(time.time() + (60 * 30)),
                subscription_data={
                    "metadata": {
                        "type": "user_membership",
                        "user_id": request.user.id,
                        "log": "[" + str(request.user.id) + "] " + request.user.username,
                    }
                }
            )
            return redirect(session.url, code=303)

    context = {"data": data}
    return render(request, "payment.html", context)


@require_POST
@csrf_exempt
def stripe_webhook(request):
    # サーバーのイベントログからの出力ステートメント
    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET_KEY)
    except ValueError as e:
        # 有効でないpayload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # 有効でない署名
        return HttpResponse(status=400)
    if "customer.subscription" in event["type"]:
        obj = event['data']['object']
        metadata_type = obj['metadata']['type']
        if metadata_type == 'user_membership' or metadata_type == 'doornoc_membership':
            id = obj['id']
            customer_id = obj['customer']
            plan = obj['plan']
            plan_id = plan['id']
            amount = plan['amount']
            interval = plan['interval']
            period_start = datetime.fromtimestamp(obj['current_period_start'])
            period_end = datetime.fromtimestamp(obj['current_period_end'])
            status = obj['status']
            data = {
                "sub_id": id,
                "plan_amount": amount,
                "plan_interval": interval,
                "start": period_start.strftime('%Y/%m/%d %H:%M:%S'),
                "end": period_start.strftime('%Y/%m/%d %H:%M:%S'),
                "status": status,
            }
            if event["type"] == "customer.subscription.created":
                if metadata_type == 'user_membership':
                    user = User.objects.filter(stripe_customer_id=customer_id)
                    if user.exists():
                        data['id'] = user[0].id
                        data['name'] = user[0].username
                        user = User.objects.get(id=user[0].id)
                        user.stripe_subscription_id = id
                        user.expired_at = period_end
                        user.save()
                elif metadata_type == 'doornoc_membership':
                    group = Group.objects.filter(stripe_customer_id=customer_id)
                    if group.exists():
                        data['id'] = group[0].id
                        data['name'] = group[0].name
                        group = Group.objects.get(id=group[0].id)
                        group.stripe_subscription_id = id
                        group.expired_at = period_end
                        group.save()
                notice_payment(metadata_type, event_type=event["type"], data=data)
            elif event["type"] == "customer.subscription.updated":
                if metadata_type == 'user_membership':
                    user = User.objects.filter(stripe_customer_id=customer_id)
                    if user.exists():
                        data['id'] = user[0].id
                        data['name'] = user[0].username
                        user = User.objects.get(id=user[0].id)
                        user.stripe_subscription_id = id
                        user.expired_at = period_end
                        user.save()
                elif metadata_type == 'doornoc_membership':
                    group = Group.objects.filter(stripe_customer_id=customer_id)
                    if group.exists():
                        data['id'] = group[0].id
                        data['name'] = group[0].name
                        group = Group.objects.get(id=group[0].id)
                        group.stripe_subscription_id = id
                        group.expired_at = period_end
                        group.save()
                notice_payment(metadata_type, event_type=event["type"], data=data)
            elif event["type"] == "customer.subscription.deleted":
                if metadata_type == 'user_membership':
                    user = User.objects.filter(stripe_customer_id=customer_id)
                    if user.exists():
                        data['id'] = user[0].id
                        data['name'] = user[0].username
                        user = User.objects.get(id=user[0].id)
                        user.stripe_subscription_id = None
                        user.expired_at = None
                        user.save()
                elif metadata_type == 'doornoc_membership':
                    group = Group.objects.filter(stripe_customer_id=customer_id)
                    if group.exists():
                        data['id'] = group[0].id
                        data['name'] = group[0].name
                        group = Group.objects.get(id=group[0].id)
                        group.stripe_subscription_id = None
                        group.expired_at = None
                        group.save()
                notice_payment(metadata_type, event_type=event["type"], data=data)
    return HttpResponse(status=200)


@login_required
def admin_sign_in(request):
    return redirect("sign_in")


@login_required
def feedback(request):
    return render(request, "feedback.html", {})
