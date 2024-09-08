from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.db.models import Q
from django.shortcuts import render

from service.models import Service


@login_required
def index(request):
    group_ids = list(request.user.groups.values_list("id", flat=True))
    q = Q()
    for group_id in group_ids:
        q.add(Q(group=group_id), Q.OR)
    services = Service.objects.filter(is_active=True).filter(q).order_by("id")
    per_page = int(request.GET.get("per_page", "20"))
    page = int(request.GET.get("page", "1"))
    paginator = Paginator(services, per_page)
    try:
        services = paginator.page(page)
    except (EmptyPage, InvalidPage):
        services = paginator.page(paginator.num_pages)

    context = {"services": services}
    return render(request, "service/index.html", context)
