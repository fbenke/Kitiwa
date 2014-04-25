from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def api_logout(request):
    if request.auth is not None:
        request.auth.delete()
    return Response({'status': 'success'})