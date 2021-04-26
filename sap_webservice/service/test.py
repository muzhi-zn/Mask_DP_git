import os

from suds.client import Client
from suds.transport.http import HttpAuthenticated

sap_url = "http://qxs4apdev:8000/sap/bc/srt/wsdl/flv_10002A111AD1/bndg_url/sap/bc/srt/rfc/sap/zpp00101/300/zpp00101" \
          "/zpp00101?sap-client=300"

transport = HttpAuthenticated(username="q00263", password="qxic666666")

if __name__ == "__main__":
    client = Client(sap_url, transport=transport)
    print(client)
    trorder = client.factory.create("TableOfZpps001order")
    # Aufnr 订单号 Auart ZP04 生产类型 Matnr 物料号
    # TES532-780A1 TES670-868A1 TES667-860A1
    result = client.service.ZPp00101("TES670-868A1", "2000", trorder)
    print(result)
    print(result.TReorder.item[0])
