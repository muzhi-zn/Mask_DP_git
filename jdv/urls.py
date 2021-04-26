# coding=utf-8
from django.conf.urls import url
from jdv.views import jdvLotList, paymentCheckList, payment_mark, download_sop_file, release_lot, MappingBlankCodeList, \
    MappingBlankCodeView, MappingBlankCodeAdd, MappingBlankCodeDel, MappingBlankCodeEdit, check_length

urlpatterns = [
    url(r'jdv_lot_list/list/$', jdvLotList.as_view()),
    url(r'jdv_lot/release/', release_lot),
    url(r'payment_check/list/$', paymentCheckList.as_view()),
    url(r'payment_check/mark/', payment_mark),
    url(r'sop_file/download/', download_sop_file),
    url(r'blank_code/list/$', MappingBlankCodeList.as_view()),
    url(r'blank_code/view/$', MappingBlankCodeView.as_view()),
    url(r'blank_code/add/$', MappingBlankCodeAdd.as_view()),
    url(r'blank_code/edit/$', MappingBlankCodeEdit.as_view()),
    url(r'blank_code/del/$', MappingBlankCodeDel.as_view()),
    url(r'blank_code/check_length/$', check_length),

]
