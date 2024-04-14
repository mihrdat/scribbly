from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lobby(request):
    participant_id = request.query_params.get("participant_id", default=0)
    return render(request, "lobby.html", {"participant_id": participant_id})
