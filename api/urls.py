from django.conf.urls import url

from api.views import auth_account, ad_conn_test

urlpatterns = [
    url(r'^auth_account/', auth_account),
    url(r'^ad_conn_test/', ad_conn_test),
]
