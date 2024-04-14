from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lobby(request):
    contact_id = request.query_params.get("contact_id", default=0)
    return render(request, "lobby.html", {"contact_id": contact_id})
