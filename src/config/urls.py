from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.urls.conf import include
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import (
	SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView,
)

urlpatterns = [
	path('admin/', admin.site.urls),
	path('api/v1/accounts/', include('src.apps.accounts.urls')),
	path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
	path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
	path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
