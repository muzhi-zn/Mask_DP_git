"""Mask_DP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.contrib import admin

# from iems.views import IEMSCallback
from iems.views import IEMSCallback
from index.views import index

from django.conf.urls import url, include, handler400, handler404, handler500

# from sap_webservice.views import notice_production_order_app, ship_or_unship_app
from system.views import page_not_found, page_error, Home, Index, CustomerIndex
from django.views import static
from django.conf import settings
from system.user_view import CustomerLogin, CustomerLogout
# import debug_toolbar

from tooling_form.file_analysis_info_view import calibrewb_callback

print('路由开始加载 system.maskdp........')
urlpatterns = [
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATICFILES_DIRS}, name='static'),
    # url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}),

    url('admin/', admin.site.urls),
    url(r'^$', CustomerIndex.as_view()),
    url(r'^index/$', Index.as_view()),
    url(r'^home/$', Home.as_view()),
    url(r'^login/$', CustomerLogin.as_view()),
    url(r'^logout/$', CustomerLogout.as_view()),

    url(r'^index/$', index),
    url(r'^jdv/', include('jdv.urls')),
    url(r'^system/', include('system.urls')),
    url(r'^machine/', include('machine.urls')),
    url(r'^maintain/', include('maintain.urls')),
    url(r'^infotree/', include('infotree.urls')),
    url(r'^making/', include('making.urls')),
    url(r'^api/', include('api.urls')),

    # url(r'^__debug__/', include(debug_toolbar.urls)),

    url(r'^callback/calibrewb/', calibrewb_callback),
    url(r'^iems/callback/', IEMSCallback().callback),
    url(r'^catalog/', include('catalog.urls')),
    url(r'^tooling_form/', include('tooling_form.urls')),
    # url(r'^sap_webservice/notice_production_order/', notice_production_order_app),
    # url(r'^sap_webservice/ship_or_unship/', ship_or_unship_app),
    url(r'^query_system/', include('query_system.urls')),
    url(r'^semi_automatic/', include('semi_automatic.urls')),
]

handler404 = page_not_found
handler500 = page_error
