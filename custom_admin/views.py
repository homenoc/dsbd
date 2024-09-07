from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.shortcuts import redirect, render

from ticket.models import Ticket


@login_required
@staff_member_required
def index(request):
    context = {"tickets": Ticket.objects.all()}
    return render(request, "custom_admin/index.html", context)


@login_required
@staff_member_required
def ticket_list(request):
    if request.method == "POST":
        id = request.POST.get("id", 0)
        ticket = Ticket.objects.get(id=int(id))
        if "no_solved" in request.POST:
            ticket.is_solved = False
            ticket.save()
        elif "solved" in request.POST:
            ticket.is_solved = True
            ticket.save()
        return redirect("/admin/custom/ticket")

    is_solved = request.GET.get("is_solved", "false")
    ticket_objects = Ticket.objects.filter(is_solved=True if is_solved == "true" else False)

    paginator = Paginator(ticket_objects, int(request.GET.get("per_page", "5")))
    page = int(request.GET.get("page", "1"))
    try:
        tickets = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tickets = paginator.page(paginator.num_pages)
    context = {
        "tickets": tickets,
        "is_solved": is_solved,
    }
    return render(request, "custom_admin/ticket/index.html", context)


@login_required
@staff_member_required
def chat(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    if not ticket:
        return render(request, "ticket/chat_error.html", {})
    context = {"ticket": ticket, "chats": ticket.chat_set.order_by("created_at").all()}
    return render(request, "custom_admin/ticket/chat.html", context)
