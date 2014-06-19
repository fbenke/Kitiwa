from django.http import HttpResponse
from rest_framework import status
from rest_framework.renderers import JSONRenderer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def page_not_found(request):
    return JSONResponse({'detail': 'Page Not Found'}, status=status.HTTP_404_NOT_FOUND)


def custom_error(request):
    return JSONResponse({'detail': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def permission_denied(request):
    return JSONResponse({'detail': 'Permission Denied'}, status=status.HTTP_403_FORBIDDEN)


def bad_request(request):
    return JSONResponse({'detail': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
