# _*_ coding: utf-8 _*_

__author__ = 'Ligo.Lu@qxic.net'
__date__ = '2019/12/18'

from tooling_form.tooling_contrast_sync_view import toolingSheetContrast

from tooling_form.show_tip_no_temp_view import ShowTipNo_tapeout_info_temp, ShowTipNo_ccd_table_temp, \
    ShowTipNo_device_info_temp, ShowTipNo_boolean_info_temp, ShowTipNo_layout_info_temp, ShowTipNo_mlm_info_temp

"""ani_2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
from tooling import tooling_view

"""
from django.contrib import admin

from django.conf.urls import url
from tooling_form.views import tooling_form_sop_download, tooling_form_download, tooling_form_upload, tooling_form_uploading, \
    tooling_ftp_service, get_files_list, check_files_list, file_upload, file_merge, file_check, file_upload_check, \
    tooling_tip_no_options, tooling_form_sop_download_file, tooling_form_download_file, done, create_lot_id, test_layout
from tooling_form.wrong_view import WrongList_tipno, WrongList, WrongForm_type1, \
    WrongListExport, CheckList, CheckListView, CheckListDelete
from tooling_form.show_tip_no_view import ShowTipNoList, ShowTipNo_del, ShowTipNo_data_view, ShowTipNo_product_info, \
    ShowTipNo_tapeout_info, ShowTipNo_device_info, ShowTipNo_ccd_table, ShowTipNo_boolean_info, ShowTipNo_layout_info, \
    ShowTipNo_mlm_info
from tooling_form.file_analysis_info_view import fileAnalysisInfoList
from tooling_form.tooling_view import import_main
from tooling_form.service.tooling_service import ToolService

urlpatterns = [
    url(r'^form_sop_download/$', tooling_form_sop_download),
    url(r'^form_sop_download/file', tooling_form_sop_download_file),
    url(r'^formDownload/$', tooling_form_download),
    url(r'^formDownload/file/$', tooling_form_download_file),
    url(r'^form_uploading/$', tooling_form_uploading),
    url(r'^ftp_service/$', tooling_ftp_service),
    url(r'^tip_no/options/$', tooling_tip_no_options),
    url(r'^form_upload/$', tooling_form_upload),
    url(r'^files/upload_check/', file_upload_check, name="文件上传校验"),
    url(r'^files/upload/', file_upload, name="文件分片上传"),
    url(r'^upload/complete/', file_merge, name="上传完成合并"),
    url(r'^files/list/', get_files_list),
    url(r'^files/check_list/', check_files_list),
    url(r'^file/check/', file_check),
    url(r'^file_analysis_info/', fileAnalysisInfoList.as_view()),
    url(r'^ftp_service/done/', done),
    url(r'^create_lot_id/', create_lot_id),
    url(r'^test_layout/', test_layout),
    # wrong_list
    url(r'wrong_list/', WrongList.as_view()),
    url(r'wrong_list_export/', WrongListExport.as_view()),
    # tooling form import ToolingFormUpload.
    url(r'^upload_status/', import_main),

    # url(r'wrong_list_tipno/', wrong_view.WrongList_tipno.as_view()),
    url(r'wrong_form_type1/', WrongForm_type1.as_view()),

    # tip_no_list
    url(r'ShowTipNoList/', ShowTipNoList.as_view()),
    url(r'ShowTipNo/del/', ShowTipNo_del.as_view()),
    url(r'ShowTipNo/data_view/', ShowTipNo_data_view.as_view()),
    url(r'ShowTipNo/product_info/', ShowTipNo_product_info.as_view()),
    url(r'ShowTipNo/tapeout_info/', ShowTipNo_tapeout_info.as_view()),
    url(r'ShowTipNo/ccd_table/', ShowTipNo_ccd_table.as_view()),
    url(r'ShowTipNo/device_info/', ShowTipNo_device_info.as_view()),
    url(r'ShowTipNo/boolean_info/', ShowTipNo_boolean_info.as_view()),
    url(r'ShowTipNo/layout_info/', ShowTipNo_layout_info.as_view()),
    # url(r'ShowTipNo/mlr_info/', ShowTipNo_mlr_info.as_view()),
    url(r'ShowTipNo/mlm_info/', ShowTipNo_mlm_info.as_view()),

    url(r'contrast/toolingSheetContrast/', toolingSheetContrast.as_view()),

    # tooling_view
    # url(r'update_import_data', tooling_view.update_import_data.as_view()),

    url(r'check_list/', CheckList.as_view()),
    url(r'checkList/view/', CheckListView.as_view()),
    url(r'checkList/del/', CheckListDelete.as_view()),


    url(r'ShowTipNo/tapeout_info_temp/', ShowTipNo_tapeout_info_temp.as_view()),
    url(r'ShowTipNo/ccd_table_temp/', ShowTipNo_ccd_table_temp.as_view()),
    url(r'ShowTipNo/device_info_temp/', ShowTipNo_device_info_temp.as_view()),
    url(r'ShowTipNo/boolean_info_temp/', ShowTipNo_boolean_info_temp.as_view()),
    url(r'ShowTipNo/layout_info_temp/', ShowTipNo_layout_info_temp.as_view()),
    url(r'ShowTipNo/mlm_info_temp/', ShowTipNo_mlm_info_temp.as_view()),
]
