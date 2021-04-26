# coding=utf-8
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from infotree.released_view import released_list, released_tree_json, released_view, released_del, released_export, \
    released_mdt_list

from infotree.released_alta_view import released_alta_list, released_alta_tree_json, released_alta_view, \
    released_alta_del, released_alta_export, released_alta_mdt_list

from infotree.unreleased_view import unreleased_list, unreleased_view, unreleased_add, unreleased_edit, \
    unreleased_del, unreleased_dict, create_check, unreleased_tree_json, check_value, unreleased_edit_dict, \
    unreleased_export, unreleased_copy, unreleased_import, unreleased_import_check, unreleased_download, \
    unreleased_release, unreleased_mdt_list, unreleased_mdt_add, unreleased_mdt_view, unreleased_mdt_edit, \
    unreleased_mdt_del

from infotree.release_check_view import release_check_list, release_check_check, release_check_check_list, \
    MdtDetail

from infotree.release_version_view import release_version_list, MDTVersion, ViewMDTInformation

from infotree.unrelease_alta_view import unreleased_alta_list, unreleased_alta_view, unreleased_alta_add, \
    unreleased_alta_edit, unreleased_alta_del, unreleased_alta_copy, unreleased_alta_tree_json, unreleased_alta_dict, \
    unreleased_alta_create_check, unreleased_alta_check_value, unreleased_alta_edit_dict, unreleased_alta_export, \
    unreleased_alta_import, unreleased_alta_download, unreleased_alta_import_check, unreleased_alta_mdt_list, \
    unreleased_alta_mdt_view, unreleased_alta_mdt_add, unreleased_alta_mdt_edit, unreleased_alta_release, \
    unreleased_alta_mdt_del

from infotree.maintain_table_view import maintain_table_list, maintain_table_view, maintain_table_edit, get_row_count, \
    maintain_table_mdt_list, maintain_table_mdt_view, maintain_table_mdt_add, maintain_table_mdt_edit, \
    maintain_table_mdt_del

from infotree.unreleased_check_view import maintain_check_list

from infotree.template_view import template_dict, template_list, template_view, template_add, template_edit, \
    template_del, template_option_list, template_option_add, template_option_view, template_option_edit, \
    template_option_del

from infotree.tree_view import tree_list, tree_view, tree_add, tree_edit, tree_del, tree_option_view, tree_option_add, \
    tree_option_list, tree_option_edit, tree_option_del

from infotree.cd_map_view import cd_map_list, cd_map_upload, cd_map_view, cd_map_check_file_exists

from infotree.cec_view import cec_list, cec_upload, cec_view, cec_check_file_exists

urlpatterns = [
    # Released
    url(r'^released/list/$', released_list.as_view()),
    url(r'^released/tree_view_json/$', released_tree_json),
    url(r'^released/view/$', released_view.as_view()),
    url(r'^released/del/$', released_del.as_view()),
    url(r'^released/export/$', released_export),
    url(r'^released/mdt/list/$', released_mdt_list.as_view()),

    # Released Alta
    url(r'^released_alta/list/$', released_alta_list.as_view()),
    url(r'^released_alta/tree_view_json/$', released_alta_tree_json),
    url(r'^released_alta/view/$', released_alta_view.as_view()),
    url(r'^released_alta/del/$', released_alta_del.as_view()),
    url(r'^released_alta/export/$', released_alta_export),
    url(r'^released_alta/mdt/list/$', released_alta_mdt_list.as_view()),

    # Unreleased
    url(r'^unreleased/list/$', unreleased_list.as_view()),
    url(r'^unreleased/view/$', unreleased_view.as_view()),
    url(r'^unreleased/add/$', unreleased_add.as_view()),
    url(r'^unreleased/edit/$', unreleased_edit.as_view()),
    url(r'^unreleased/del/$', unreleased_del.as_view()),
    url(r'^unreleased/copy/$', unreleased_copy.as_view()),
    url(r'^unreleased/json/$', unreleased_tree_json),
    url(r'^unreleased/dict/$', unreleased_dict),
    url(r'^unreleased/create_check/$', create_check),
    url(r'^unreleased/check_value/$', check_value),
    url(r'^unreleased/edit_dict/$', unreleased_edit_dict),
    url(r'^unreleased/export/$', unreleased_export),
    url(r'^unreleased/import/$', unreleased_import.as_view()),
    url(r'^unreleased/download/$', unreleased_download),
    url(r'^unreleased/import_check/$', unreleased_import_check.as_view()),
    url(r'^unreleased/release/$', unreleased_release),
    url(r'^unreleased/mdt/list/$', unreleased_mdt_list.as_view()),
    url(r'^unreleased/mdt/view/$', unreleased_mdt_view.as_view()),
    url(r'^unreleased/mdt/add/', unreleased_mdt_add.as_view()),
    url(r'^unreleased/mdt/edit/$', unreleased_mdt_edit.as_view()),
    url(r'^unreleased/mdt/del/$', unreleased_mdt_del.as_view()),

    # Unreleased Alta
    url(r'^unreleased_alta/list/$', unreleased_alta_list.as_view()),
    url(r'^unreleased_alta/view/$', unreleased_alta_view.as_view()),
    url(r'^unreleased_alta/add/$', unreleased_alta_add.as_view()),
    url(r'^unreleased_alta/edit/$', unreleased_alta_edit.as_view()),
    url(r'^unreleased_alta/del/$', unreleased_alta_del.as_view()),
    url(r'^unreleased_alta/copy/$', unreleased_alta_copy.as_view()),
    url(r'^unreleased_alta/json/$', unreleased_alta_tree_json),
    url(r'^unreleased_alta/dict/$', unreleased_alta_dict),
    url(r'^unreleased_alta/create_check/$', unreleased_alta_create_check),
    url(r'^unreleased_alta/check_value/$', unreleased_alta_check_value),
    url(r'^unreleased_alta/edit_dict/$', unreleased_alta_edit_dict),
    url(r'^unreleased_alta/export/$', unreleased_alta_export),
    url(r'^unreleased_alta/import/$', unreleased_alta_import.as_view()),
    url(r'^unreleased_alta/download/$', unreleased_alta_download),
    url(r'^unreleased_alta/import_check/$', unreleased_alta_import_check.as_view()),
    url(r'^unreleased_alta/release/$', unreleased_alta_release),
    url(r'^unreleased_alta/mdt/list/$', unreleased_alta_mdt_list.as_view()),
    url(r'^unreleased_alta/mdt/view/$', unreleased_alta_mdt_view.as_view()),
    url(r'^unreleased_alta/mdt/add/', unreleased_alta_mdt_add.as_view()),
    url(r'^unreleased_alta/mdt/edit/$', unreleased_alta_mdt_edit.as_view()),
    url(r'^unreleased_alta/mdt/del/$', unreleased_alta_mdt_del.as_view()),

    # Released Check
    url(r'^release_check/list/$', release_check_list.as_view()),
    url(r'^release_check/check/$', release_check_check),
    # url(r'^release_check/view/$', release_check_list.as_view()),
    url(r'^release_check/check/list/$', release_check_check_list.as_view()),
    url(r'^release_check/mdt_detail/$', csrf_exempt(MdtDetail.as_view())),

    # Release Version
    url(r'^release_version/list/$', release_version_list.as_view()),
    url(r'^release_mdt_version/list/$', csrf_exempt(MDTVersion.as_view())),
    url(r'^release_mdt_version/view/$', csrf_exempt(ViewMDTInformation.as_view())),
    # url(r'^release_version/view/$', release_version_view.as_view()),

    # Maintain Table
    url(r'^maintain_table/list/$', maintain_table_list.as_view()),
    url(r'^maintain_table/view/$', maintain_table_view.as_view()),
    url(r'^maintain_table/edit/$', maintain_table_edit.as_view()),
    url(r'^maintain_table/get_row_count/$', get_row_count),

    # Maintain Check
    url(r'^maintain_check/list/$', maintain_check_list.as_view()),
    # url(r'^maintain_check/view/$', maintain_table_view.as_view()),
    # url(r'^maintain_check/edit/$', maintain_table_edit.as_view()),

    # Maintain Table MDT
    url(r'^maintain_table/mdt/list/$', maintain_table_mdt_list.as_view()),
    url(r'^maintain_table/mdt/view/$', maintain_table_mdt_view.as_view()),
    url(r'^maintain_table/mdt/add/$', maintain_table_mdt_add.as_view()),
    url(r'^maintain_table/mdt/edit/$', maintain_table_mdt_edit.as_view()),
    url(r'^maintain_table/mdt/del/$', maintain_table_mdt_del.as_view()),

    # Template
    url(r'^template/dict/$', template_dict),
    url(r'^template/list/$', template_list.as_view()),
    url(r'^template/view/$', template_view.as_view()),
    url(r'^template/add/$', template_add.as_view()),
    url(r'^template/edit/$', template_edit.as_view()),
    url(r'^template/del/$', template_del.as_view()),

    # Template option
    url(r'^template_option/list/$', template_option_list.as_view()),
    url(r'^template_option/view/$', template_option_view.as_view()),
    url(r'^template_option/add/$', template_option_add.as_view()),
    url(r'^template_option/edit/$', template_option_edit.as_view()),
    url(r'^template_option/del/$', template_option_del.as_view()),

    # Tree
    url(r'^tree/list/$', tree_list.as_view()),
    url(r'^tree/view/$', tree_view.as_view()),
    url(r'^tree/add/$', tree_add.as_view()),
    url(r'^tree/edit/$', tree_edit.as_view()),
    url(r'^tree/del/$', tree_del.as_view()),

    # Tree option
    url(r'^tree_option/list/$', tree_option_list.as_view()),
    url(r'^tree_option/view/$', tree_option_view.as_view()),
    url(r'^tree_option/add/$', tree_option_add.as_view()),
    url(r'^tree_option/edit/$', tree_option_edit.as_view()),
    url(r'^tree_option/del/$', tree_option_del.as_view()),

    # CD MAP
    url(r'^cd_map/list/$', cd_map_list.as_view()),
    url(r'^cd_map/upload/$', cd_map_upload.as_view()),
    url(r'^cd_map/view/$', cd_map_view.as_view()),
    url(r'^cd_map/check_file_exists/$', cd_map_check_file_exists),

    # CEC
    url(r'^cec/list/$', cec_list.as_view()),
    url(r'^cec/upload/$', cec_upload.as_view()),
    url(r'^cec/view/$', cec_view.as_view()),
    url(r'^cec/check_file_exists/$', cec_check_file_exists),
]
