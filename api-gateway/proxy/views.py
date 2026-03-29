"""
proxy/views.py

A lightweight reverse-proxy view.
Incoming:  /api/<service>/<path>
Outgoing:  http://<service-host>/<path>

Preserves method, headers, body, and query string.
Streams the upstream response back to the client.
"""
import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework.views import APIView


# Headers that must not be forwarded blindly
HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "host",
}


class ProxyView(APIView):
    authentication_classes = []
    permission_classes = []

    def dispatch(self, request, service: str, path: str, *args, **kwargs):
        base_url = settings.SERVICE_URLS.get(service)
        if not base_url:
            return HttpResponseNotFound(
                f"Unknown service: '{service}'. "
                f"Available: {', '.join(settings.SERVICE_URLS)}"
            )

        # Build the upstream URL
        upstream_url = f"{base_url.rstrip('/')}/api/{service}/{path}"
        if request.META.get("QUERY_STRING"):
            upstream_url += f"?{request.META['QUERY_STRING']}"

        # Forward safe headers
        forward_headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in HOP_BY_HOP
        }

        try:
            upstream_resp = requests.request(
                method=request.method,
                url=upstream_url,
                headers=forward_headers,
                data=request.body,
                timeout=10,
                allow_redirects=False,
            )
        except requests.exceptions.ConnectionError as exc:
            return HttpResponse(f"Service '{service}' unreachable: {exc}")
        except requests.exceptions.Timeout:
            return HttpResponse(f"Service '{service}' timed out.")

        # Build the Django response, stripping hop-by-hop headers
        response = HttpResponse(
            content=upstream_resp.content,
            status=upstream_resp.status_code,
            content_type=upstream_resp.headers.get("Content-Type", "application/json"),
        )
        for key, value in upstream_resp.headers.items():
            if key.lower() not in HOP_BY_HOP:
                response[key] = value

        return response