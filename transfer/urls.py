from django.urls import path

from transfer.views import jsonrpc

urlpatterns = [
    path('', jsonrpc)
]
