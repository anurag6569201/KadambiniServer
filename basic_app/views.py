from django.shortcuts import render
from django.conf import settings

# basic_app page view
def basic_app(request):
    return render(request, 'basic_app/basic_app.html')

# Custom 404 error view (Page Not Found)
def page_not_found_view(request, exception):
    return render(request, 'basic_app/404.html', status=404)

# Custom 500 error view (Server Error)
def server_error_view(request):
    return render(request, 'basic_app/500.html', status=500)

# Custom 403 error view (Permission Denied)
def permission_denied_view(request, exception):
    return render(request, 'basic_app/403.html', status=403)

# Custom 400 error view (Bad Request)
def bad_request_view(request, exception):
    return render(request, 'basic_app/400.html', status=400)
