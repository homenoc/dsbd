import time as default_time
from datetime import datetime, time

import stripe
from django.conf import settings
from django.utils import timezone

from custom_auth.models import Group, User

MEMBERSHIP_TAG_TYPE = f"{settings.STRIPE_MEMBERSHIP_TAG_NAME}"
DONATE_TAG_TYPE = f"{settings.STRIPE_DONATE_TAG_NAME}"
DONATE_MEMBERSHIP_TAG_TYPE = f"{settings.STRIPE_DONATE_MEMBERSHIP_TAG_NAME}"


def check_expired(expired_at):
    if not expired_at:
        return True
    return expired_at < timezone.now()


class Payment:
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_customer(self, group_id: int, user_id: int):
        group = Group.objects.get(id=group_id)
        name = f"[GROUP] {group.id}: {group.name}"
        if not group.stripe_customer_id:
            return None
        customer = self.stripe.Customer.create(
            name=name,
            description="doornoc_service",  # TODO: change description
            metadata={
                "id": "doornoc_service",  # TODO: change description
                "user_id": user_id,
                "group_id": group.id,
                "version": 2,
            },
        )
        group.stripe_customer_id = customer.id
        group.save()
        return customer.id

    def get_billing_portal(self, customer_id: str, group_id: int = 0):
        return_url = f"{settings.DOMAIN_URL}/group"
        if group_id != 0:
            return_url += f"/{group_id}/payment"
        session = self.stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)
        return session.url

    def checkout_membership(self, customer_id: str, price_id: str, group: Group, user: User):
        payment_return_url = f"{settings.DOMAIN_URL}/group/{group.id}/payment"
        session = self.stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            customer=customer_id,
            success_url=payment_return_url,
            cancel_url=payment_return_url,
            expires_at=int(default_time.time() + (60 * 30)),
            subscription_data={
                "metadata": {
                    "type": "membership",
                    "user_id": user.id,
                    "group_id": group.id,
                    "log": f"[{group.id}] {group.name}",
                }
            },
        )
        return session.url

    def get_product(self, stripe_type: str):
        products = self.stripe.Product.search(query=f"metadata['service_id']:'{stripe_type}'")
        if not products["data"]:
            raise ValueError("Products not found")
        return products.data[0]

    def get_prices(self, product_id: str):
        prices = self.stripe.Price.list(product=product_id, limit=10)
        return prices.data

    def update_membership_expired(self, group: Group):
        product_id = self.get_product(stripe_type=MEMBERSHIP_TAG_TYPE).id
        subscriptions = self.stripe.Subscription.list(customer=group.stripe_customer_id)
        period_end = None
        for subscription in subscriptions.data:
            if subscription.plan.product != product_id:
                continue
            period_start_date = datetime.fromtimestamp(subscription.current_period_start).date()
            period_end_date = datetime.fromtimestamp(subscription.current_period_end).date()
            period_start = datetime.combine(period_start_date, time(0, 0, 0))
            tmp_period_end = datetime.combine(period_end_date, time(23, 59, 59))
            if period_end is None or period_end < tmp_period_end:
                period_end = tmp_period_end
            group.membership_expired_at = period_end
            group.save()
