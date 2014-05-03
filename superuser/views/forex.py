import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from kitiwa import settings as s


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_usd_ghs(request):
    r = requests.get(s.OPEN_EXCHANGE_RATE_API_URL)
    if r.status_code == 200:
        rate = r.json().get('rates').get('GHS')
        return Response({'rate': rate})
    else:
        return Response(r.json(), status=r.status_code)
