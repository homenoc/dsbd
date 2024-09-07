from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.shortcuts import redirect, render

from custom_auth.models import Group
from ticket.form import TicketForm
from ticket.models import Ticket


@login_required
def index(request):
    if request.method == "POST":
        id = request.POST.get("id", 0)
        if "no_solved" in request.POST:
            ticket = Ticket.objects.get_one_ticket(int(id), request.user)
            ticket.is_solved = False
            ticket.save()
        elif "solved" in request.POST:
            ticket = Ticket.objects.get_one_ticket(int(id), request.user)
            ticket.is_solved = True
            ticket.save()
        return redirect("/ticket")

    is_solved = request.GET.get("is_solved", "false")
    ticket_objects = Ticket.objects.get_ticket(user=request.user, is_solved=True if is_solved == "true" else False)

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
    return render(request, "ticket/index.html", context)


@login_required
def ticket_add(request):
    groups = request.user.groups.filter(status=1)
    form = TicketForm(groups, request.POST)

    context = {
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            group = None
            ticket_type = form.cleaned_data.get("ticket_type")
            if ticket_type != "user":
                # この場合はgroup
                if groups.exists() & groups.filter(id=int(ticket_type)).exists():
                    group = Group.objects.filter(id=int(ticket_type)).first()
                else:
                    context["error"] = "グループが存在しません"
                    return render(request, "ticket/add.html", context)
            Ticket.objects.create(
                group=group,
                user=request.user,
                title=form.cleaned_data.get("title"),
                body=form.cleaned_data.get("body"),
            ).save()
            return redirect("/ticket")

    return render(request, "ticket/add.html", context)


@login_required
def chat(request, ticket_id):
    ticket = Ticket.objects.get_one_ticket(ticket_id, request.user)

    if request.method == "POST":
        if "no_solved" in request.POST:
            ticket.is_solved = False
            ticket.save()
        elif "solved" in request.POST:
            ticket.is_solved = True
            ticket.save()
        return redirect("/ticket/" + str(ticket_id) + "/chat")

    if not ticket:
        return render(request, "ticket/chat_error.html", {})
    context = {"ticket": ticket, "chats": ticket.chat_set.order_by("created_at").all()}
    return render(request, "ticket/chat.html", context)
