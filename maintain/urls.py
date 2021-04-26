from django.conf.urls import url

from maintain.customer_code_views import CustomerCodeView, CustomerCodeAdd, CustomerCodeEdit, CustomerCodeDel, \
    check_code
from maintain.pellicle_mapping_views import PellicleList, PellicleAdd, PellicleView, PellicleEdit, PellicleDel
from maintain.user_customer_code_views import user_customer_code_list
from maintain.customer_ftp_views import CustomerFTPView, CustomerFTPAdd, get_customer_code, CustomerFTPDel, CustomerFTPEdit
from maintain.data_in_view import data_in_list, data_in_pass, data_in_pass_cancel, data_in_tree_json, data_in_export, get_customer
from maintain.customer_data_structure_views import customer_data_structure_list, customer_data_structure_pass, customer_data_structure_pass_cancel, customer_data_structure_tree_json, customer_data_structure_export, get_customer
from maintain.customer_data_retention_views import customer_data_retention_list, customer_data_retention_pass, customer_data_retention_pass_cancel, customer_data_retention_tree_json, customer_data_retention_export, get_customer

urlpatterns = [

    # customer_code
    url(r'^customer_code/list/$', CustomerCodeView.as_view()),
    url(r'^customer_code/add/$', CustomerCodeAdd.as_view()),
    url(r'^customer_code/edit/$', CustomerCodeEdit.as_view()),
    url(r'^customer_code/del/$', CustomerCodeDel.as_view()),
    url(r'^customer_code/check_code/$', check_code),

    # customer_code user
    url(r'^user_customer_code/list/$', user_customer_code_list.as_view()),

    # customer_ftp_account
    url(r'^customer_ftp/list/$', CustomerFTPView.as_view()),
    url(r'^customer_ftp/add/$', CustomerFTPAdd.as_view()),
    url(r'^customer_ftp/edit/$', CustomerFTPEdit.as_view()),
    url(r'^customer_ftp/del/$', CustomerFTPDel.as_view()),
    url(r'^customer_ftp/get_customer_code/$', get_customer_code),

    # pellicle_mapping
    url(r'^pellicle/list/$', PellicleList.as_view()),
    url(r'^pellicle/add/$', PellicleAdd.as_view()),
    url(r'^pellicle/view/$', PellicleView.as_view()),
    url(r'^pellicle/edit/$', PellicleEdit.as_view()),
    url(r'^pellicle/del/$', PellicleDel.as_view()),

    url(r'^data_in/list/$', data_in_list.as_view()),
    url(r'^data_in/tree_view_json/$', data_in_tree_json),
    url(r'^data_in/get_customer/$', get_customer),
    url(r'^data_in/pass/$', data_in_pass.as_view()),
    url(r'^data_in/cancel_pass/$', data_in_pass_cancel.as_view()),
    url(r'^data_in/export/$', data_in_export),
    #url(r'^data_in/mdt/list/$', data_in_mdt_list.as_view()),

    url(r'^customer_data_structure/list/$', customer_data_structure_list.as_view()),
    url(r'^customer_data_structure/tree_view_json/$', customer_data_structure_tree_json),
    url(r'^customer_data_structure/get_customer/$', get_customer),
    url(r'^customer_data_structure/pass/$', customer_data_structure_pass.as_view()),
    url(r'^customer_data_structure/cancel_pass/$', customer_data_structure_pass_cancel.as_view()),
    url(r'^customer_data_structure/export/$', customer_data_structure_export),

    url(r'^customer_data_retention/list/$', customer_data_retention_list.as_view()),
    url(r'^customer_data_retention/tree_view_json/$', customer_data_retention_tree_json),
    url(r'^customer_data_retention/get_customer/$', get_customer),
    url(r'^customer_data_retention/pass/$', customer_data_retention_pass.as_view()),
    url(r'^customer_data_retention/cancel_pass/$', customer_data_retention_pass_cancel.as_view()),
    url(r'^customer_data_retention/export/$', customer_data_retention_export),
]
