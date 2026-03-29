from django.urls import path, re_path
from proxy.views import ProxyView

urlpatterns = [
    re_path(r"^api/(?P<service>[^/]+)/(?P<path>.*)$", ProxyView.as_view()),
]