from django.conf.urls import url

from query_system.test_create_jb_file_view import test_create_jb_file
from query_system.views import ProductionList, DeviceListView, MaskNameGroupStatusView, StageStatusView, \
    JDVAccountListView, JDVAccountAddView, JdvDataUploadListView, JDVDataListView, JDVDataReleaseFormView, \
    JdvDataUploadFormView, sgd_account_options, get_jb_file_list, jdv_data_del

urlpatterns = [
    url(r'^production/list/$', ProductionList.as_view()),
    url(r'^production/device_list/$', DeviceListView.as_view()),
    url(r'^device_group/to_status_page/$', MaskNameGroupStatusView().get),
    url(r'^device_group/get_stage_data/$', MaskNameGroupStatusView().post),
    url(r'^production/get_stage_status/$', StageStatusView().get_stage_status),
    url(r'^production/to_stage_status/$', StageStatusView().get),
    url(r'^jdv/account_list/$', JDVAccountListView.as_view()),
    url(r'^jdv/account_add/$', JDVAccountAddView.as_view()),
    url(r'^jdv/account_options/$', sgd_account_options),
    url(r'^jdv/job_deck_options/$', get_jb_file_list),
    url(r'^jdv/data_upload_list/$', JdvDataUploadListView.as_view()),
    url(r'^jdv_data/del/$', jdv_data_del),
    url(r'^jdv_data/list/$', JDVDataListView.as_view()),
    url(r'^jdv_data/release/$', JDVDataReleaseFormView.as_view()),
    url(r'^jdv_data/hold/$', JDVDataListView().hold),
    url(r'^jdv_data/to_released_page/$', JDVDataListView().to_released_page),
    url(r'^jdv_data/upload_form/$', JdvDataUploadFormView.as_view()),
    url(r'^device_group/to_status_page/$', MaskNameGroupStatusView().get),
    url(r'^device_group/get_stage_data/$', MaskNameGroupStatusView().post),
    url(r'^jdv/test_create_jb_file/$', test_create_jb_file)

]
