from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from catalog.catalog_views import CatalogList, start_catalog, catalog_error_list, catalog_move_back, catalog_change, \
    catalot_op_operation
from catalog.tool_status_views import ToolStatus, ToolRouteDetail, gen_exptool, ChangeExptool, upload_progress
from catalog.tool_view import ToolView, GroupView, ToolMaintainAdd, ToolMaintainEdit, ToolMaintainDel, GroupAdd, \
    GroupEdit, GroupDel, ToolRouteList, ToolRouteAdd, ToolRouteEdit, ToolRouteDel

# from catalog.views import CatalogAllInfo

urlpatterns = [
    # url(r'^catalog_info/all_info/$', csrf_exempt(CatalogAllInfo)),
    url(r'^tool_maintain/tool_info/$', ToolView.as_view()),
    url(r'tool_maintain/group_maintain/', GroupView.as_view()),
    url(r'tool_maintain/add/', ToolMaintainAdd.as_view()),
    url(r'tool_maintain/edit/', ToolMaintainEdit.as_view()),
    url(r'tool_maintain/del/', ToolMaintainDel.as_view()),
    url(r'group/add/', GroupAdd.as_view()),
    url(r'group/edit/', GroupEdit.as_view()),
    url(r'group/del/', GroupDel.as_view()),
    url(r'tool_status/list/', ToolStatus.as_view()),
    url(r'tool_name_route/list/', ToolRouteList.as_view()),
    url(r'tool_name_route/add/', ToolRouteAdd.as_view()),
    url(r'tool_name_route/edit/', ToolRouteEdit.as_view()),
    url(r'tool_name_route/del/', ToolRouteDel.as_view()),
    url(r'tool_status/view_detail/', ToolRouteDetail.as_view()),
    url(r'tool_status_detail/gen_exptool/', gen_exptool),
    url(r'catalog/change_exptool/', ChangeExptool.as_view()),
    url(r'catalog_info/all_info/', csrf_exempt(CatalogList.as_view())),
    url(r'catalog_info/start_catalog/', start_catalog),
    url(r'catalog_info/upload_progress/', csrf_exempt(upload_progress.as_view())),

    url(r'catalog_info/error_list/', catalog_error_list.as_view()),
    url(r'catalog_info/catalog_op_operation/', csrf_exempt(catalot_op_operation.as_view())),
    # url(r'catalog_info/catalog_op_cancel/', catalog_op_cancel),
    # url(r'catalog_info/catalog_op_comp/', catalog_op_comp),
    url(r'catalog_info/catalog_move_back/', catalog_move_back),
    url(r'catalog_info/catalog_change/', catalog_change),
]
