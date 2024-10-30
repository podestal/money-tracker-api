from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
import debug_toolbar

urlpatterns = []

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

urlpatterns += [
    path("admin/", admin.site.urls),
    path("api/", include("tracker.urls")),
    path("auth/", include("core.urls")),
    # path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(
#         settings.MEDIA_URL,
#         document_root=settings.MEDIA_ROOT,
#     )
