# coding=utf-8

from machine.views import machine_manage_list, machine_manage_add, \
    machine_manage_view, RoleCheckName, machine_manage_edit, machine_manage_del, WriterMappingList, WriterMappingAdd, \
    WriterMappingEdit, WriterMappingDel, WriterMappingView, get_machine_options, gen_catalog_tool_id, \
    gen_info_tree_tool_id
from django.conf.urls import url


urlpatterns = [
    url(r'^machine_manage/list/$', machine_manage_list.as_view()),

    url(r'^machine_manage/view/$', machine_manage_view.as_view()),
    url(r'^machine_manage/add/$', machine_manage_add.as_view()),
    url(r'^machine_manage/edit/$', machine_manage_edit.as_view()),
    url(r'^machine_manage/del/$', machine_manage_del.as_view()),

    url(r'^machine_manage/check/name/$', RoleCheckName.as_view()),
    url(r'^writer_mapping/list/$', WriterMappingList.as_view()),
    url(r'^writer_mapping/add/$', WriterMappingAdd.as_view()),
    url(r'^writer_mapping/edit/$', WriterMappingEdit.as_view()),
    url(r'^writer_mapping/del/$', WriterMappingDel.as_view()),
    url(r'^writer_mapping/view/$', WriterMappingView.as_view()),
    url(r'^options/', get_machine_options),
    url(r'^info_tree/gen_selects/', gen_info_tree_tool_id),
    url(r'^catalog/gen_tool_id/', gen_catalog_tool_id),
]