from django.test import TestCase

# Create your tests here.
from suds.client import Client
from suds.transport.http import HttpAuthenticated


SAP_URL = "http://10.1.14.10:8000/sap/bc/srt/wsdl/flv_10002A111AD1/bndg_url/sap/bc/srt/rfc/sap/zpp00101/400/zpp00101/zpp00101?sap-client=400"
SAP_FAB = "2000"


if __name__ == "__main__":
    # client = Client("http://127.0.0.1:8000/sap_webservice/notice_production_order/?wsdl")
    # result = client.service.notice_production_order("2000", "F00001", "TES003-384A1", "10000023", "ZP04", "100000",
    #                                                 "10", "1111")
    # print(client)
    # print(result)

    transport = HttpAuthenticated(username="CHQ.Zhang", password="123456")
    client = Client(SAP_URL, transport=transport)
    tr_order = client.factory.create("TableOfZpps001order")
    print(client)
    result = client.service.ZPp00101("TES667-860A1", SAP_FAB, tr_order)
    print(result)