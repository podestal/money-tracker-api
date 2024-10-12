from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
import debug_toolbar

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("tracker.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("__debug__/", include(debug_toolbar.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(
#         settings.MEDIA_URL,
#         document_root=settings.MEDIA_ROOT,
#     )
