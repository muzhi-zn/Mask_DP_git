# coding=utf-8
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from making.fracture_views import FractureReDeck, FractureXORReDeck, FractureXORReDo, FractureReDo, FractureReDeckAndDo, \
    FractureXORReDeckAndDo, IsRunning, WriterRedo, FTPRedo
from making.lot_time_line_view import LotTimeline, get_lot_list, LotTrailDel
from making.views import enginnerLotList, compileLotList, ExptoolChange, compile_lot, convertOptions, convertStatus, \
    convert_log, convertOptionLogView, PassStation, pass_rfl, GenLotID, BlankPellicleChange, InsertBlankAndPellicle
from making.convert_status_view import ConvertStatusView
from making.call_back_log_view import CallBackLogList, CallBackDel, callback_log, CallBackLogProgressHistory
from making.call_back_log_view import CallBackLogList, CallBackDel, CallBackView
from making.views import GenStage

urlpatterns = [

    # convert status
    url(r'lot/convert/status/view/', ConvertStatusView.as_view()),
    url(r'lot/convert/status/get_mask_name_list/', convertOptions().get_mask_name_list),
    url(r'lot/convert/status/get_device_by_mask_name/', convertOptions().get_device_by_mask_name),
    url(r'lot/convert/status/get_device_by_lot_id/', convertOptions().get_device_by_lot_id),
    url(r'lot/convert/status/get_device_stages/', convertStatus().get_device_stages),
    url(r'lot/convert/status/get_frame_stages/', convertStatus().get_frame_stages),
    url(r'lot/convert/status/stage_operation_form/', convertStatus().stage_operation_form),
    url(r'lot/convert/status/operate/', convertStatus().convert_status_operate),
    url(r'lot/convert/status/gen_lot_id/', csrf_exempt(GenLotID.as_view())),
    url(r'convert/status/log/list/', convert_log.as_view()),
    url(r'convert/status/log/view/', convertOptionLogView.as_view()),

    # lot time line
    url(r'lot/timeline/view/', LotTimeline.as_view()),
    url(r'lot/timeline/lot/trail/del/', LotTrailDel.as_view()),

    url(r'lot/fracture/callback/', callback_log),

    url(r'jdv_enginner_lot_list/list/$', enginnerLotList.as_view()),
    url(r'jdv_compile_lot_list/list/$', compileLotList.as_view()),
    url(r'lot/list/', get_lot_list),
    url(r'lot/exptool_change/', ExptoolChange.as_view()),
    url(r'lot/blank_pellicle_change/', BlankPellicleChange.as_view()),
    url(r'lot/blank_pellicle_insert/', InsertBlankAndPellicle.as_view()),
    url(r'lot/op_test/', PassStation.as_view()),
    url(r'lot/pass_rfl/', pass_rfl),
    url(r'jdv_compile_lot_list/compile_status/$', compile_lot),

    url(r'call_back_log/list/$', CallBackLogList.as_view()),
    url(r'call_back_log/del/$', CallBackDel.as_view()),
    url(r'call_back_log/view/$', CallBackView.as_view()),

    url(r'^fracture/re/deck/$', FractureReDeck.as_view()),
    url(r'^fracture/re/do/$', FractureReDo.as_view()),
    url(r'^fracture/re/deck/do/$', FractureReDeckAndDo.as_view()),

    url(r'^fracture/xor/re/deck/$', FractureXORReDeck.as_view()),
    url(r'^fracture/xor/re/do/$', FractureXORReDo.as_view()),
    url(r'^fracture/xor/re/deck/do/$', FractureXORReDeckAndDo.as_view()),

    url(r'^fracture/is_running/$', IsRunning.as_view()),
    url(r'^call_back_log/progress_history/$', CallBackLogProgressHistory.as_view()),
    url(r'^covert/gen_tool_id/$', csrf_exempt(GenStage.as_view())),

    url(r'^writer/re/do/$', WriterRedo.as_view()),

    url(r'^ftp/re/do/$', FTPRedo.as_view()),
]
