from django.conf.urls import url

from semi_automatic.views import LotRecordList, LotRecordAdd, LotRecordFtp, LotRecordCatalog, get_ftp_record_list, \
    get_catalog_record_list, InsertLot

urlpatterns = [
    url(r'lot_record/list/', LotRecordList.as_view()),
    url(r'lot_record/add/', LotRecordAdd.as_view()),
    url(r'lot_record/ftp/', LotRecordFtp.as_view()),
    url(r'lot_record/catalog/', LotRecordCatalog.as_view()),
    url(r'lot_record/get_ftp_record_list/', get_ftp_record_list),
    url(r'lot_record/get_catalog_record_list/', get_catalog_record_list),
    url(r'lot_record/insert_lot_id/', InsertLot.as_view())
]
