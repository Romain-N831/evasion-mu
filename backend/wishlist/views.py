from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from activities.models import Activity
from hotels.models import RoomType
from users.models import Customer
from .models import Wishlist, WishlistItem


@login_required
def wishlist_view(request):
    if not request.user.is_authenticated:
        return render(
            request,
            "wishlist/wishlist.html",
            {
                "wishlist": None,
                "items": [],
                "profile_missing": False,
            },
        )

    customer = Customer.objects.filter(user=request.user).first()

    if customer is None:
        return render(
            request,
            "wishlist/wishlist.html",
            {"wishlist": None, "items": [], "profile_missing": True},
        )

    wishlist = Wishlist.objects.filter(customer=customer).first()

    items = (
        wishlist.items.select_related("activity", "room_type", "room_type__hotel")
        if wishlist else []
    )

    return render(
        request,
        "wishlist/wishlist.html",
        {
            "wishlist": wishlist,
            "items": items,
            "profile_missing": False,
        },
    )


@login_required
@require_POST
def add_to_wishlist(request):
    customer = get_object_or_404(Customer, user=request.user)

    activity_id = request.POST.get("activity_id")
    room_type_id = request.POST.get("room_type_id")

    # Exactly one target must be supplied.
    if bool(activity_id) == bool(room_type_id):
        return redirect("wishlist:detail")

    wishlist, created = Wishlist.objects.get_or_create(customer=customer)

    if activity_id:
        activity = get_object_or_404(Activity, pk=activity_id, is_active=True)
        WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            activity=activity,
        )
    else:
        room_type = get_object_or_404(RoomType, pk=room_type_id, is_active=True)
        WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            room_type=room_type,
        )

    return redirect("wishlist:detail")


@login_required
@require_POST
def remove_from_wishlist(request, item_id):
    customer = get_object_or_404(Customer, user=request.user)
    wishlist = get_object_or_404(Wishlist, customer=customer)

    item = get_object_or_404(
        WishlistItem,
        pk=item_id,
        wishlist=wishlist,
    )
    item.delete()

    return redirect("wishlist:detail")