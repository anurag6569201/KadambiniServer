from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from basic_app.views import bad_request_view, permission_denied_view, page_not_found_view, server_error_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('basic_app.urls')),
    
    path('api/auth/', include('authentication.urls')),
    path('api/maintree/', include('maintree.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = bad_request_view
handler403 = permission_denied_view
handler404 = page_not_found_view
handler500 = server_error_view