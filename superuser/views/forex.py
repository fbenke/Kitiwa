import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from kitiwa import settings as s
from kitiwa.utils import log_error


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_usd_ghs(request):
    try:
        r = requests.get(s.OPEN_EXCHANGE_RATE_API_URL)
        if r.status_code == 200:
            try:
                rate = r.json().get('rates').get('GHS')
                return Response({'rate': rate})
            except AttributeError:
                log_error(
                    'ERROR - FOREX (get_usd_ghs): rates[GHS] not present in 200 response'
                )
                return Response(r.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            log_error(
                'ERROR - FOREX (get_usd_ghs): Call returned response code: ' +
                str(r.status_code)
            )
            return Response(r.json(), status=r.status_code)
    except requests.RequestException as e:
        log_error(
            'ERROR - FOREX (get_usd_ghs): Call gave a request exception ' +
            repr(e)
        )
        return Response(r.json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
