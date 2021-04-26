from utilslibrary.mes_webservice import mes_utils
import datetime, time

client = mes_utils.get_ws_client()


# TxLotInfoInq__160(pptUser requestUserID,
#                   objectIdentifierSequence lotID,
#                   xs:boolean lotBasicInfoFlag,
#                   xs:boolean lotControlUseInfoFlag,
#                   xs:boolean lotFlowBatchInfoFlag,
#                   xs:boolean lotNoteFlagInfoFlag,
#                   xs:boolean lotOperationInfoFlag,
#                   xs:boolean lotOrderInfoFlag,
#                   xs:boolean lotControlJobInfoFlag,
#                   xs:boolean lotProductInfoFlag,
#                   xs:boolean lotRecipeInfoFlag,
#                   xs:boolean lotLocationInfoFlag,
#                   xs:boolean lotWipOperationInfoFlag,
#                   xs:boolean lotWaferAttributesFlag,
#                   xs:boolean lotListInCassetteInfoFlag,
#                   xs:boolean waferMapInCassetteInfoFlag,
#                   xs:boolean lotBackupInfoFlag)
ppt_user = {'userID': 'DP_Test', 'password': 'utfU`QE'}
catalog_lot_id = 'MA100263.001'

def lotinfo_inquery(catalog_lot_id, ppt_user):
    """查询lot相关信息"""
    parmUser = client.factory.create('pptUser')
    parmUser.userID.identifier = ppt_user['userID']
    parmUser.password = ppt_user['password']

    lot_id_sequence = client.factory.create('objectIdentifierSequence')
    lot_id = client.factory.create('objectIdentifier')
    lot_id.identifier = catalog_lot_id
    lot_id_sequence.item.append(lot_id)

    result = client.service.TxLotInfoInq__160(parmUser, lot_id_sequence, True, True, True, True, True, True, True,
                                              True, True, True, True, True, True, True, True)
    # print(result.strLotInfo.item)
    for item in result.strLotInfo.item:
        ds_stamp_time = item.strLotBasicInfo.dueTimeStamp.replace(".", ":", 2).replace("-", ' ').replace(' ', '-', 2)
        t = datetime.datetime.strptime(ds_stamp_time, "%Y-%m-%d %H:%M:%S.%f").timetuple()
        ds_timeStamp = int(time.mktime(t))
        now_timeStamp = int(time.time())
        priority = item.strLotBasicInfo.externalPriority
    try:
        clip = int((ds_timeStamp-now_timeStamp)/3600)
        return clip, priority
    except:
        return clip, priority


if __name__ == "__main__":
    lotinfo_inquery(catalog_lot_id, ppt_user)


"""
[(pptLotInfo__160){
   strLotBasicInfo = 
      (pptLotBasicInfo__140){
         lotID = 
            (objectIdentifier){
               identifier = "MA100261.001"
               stringifiedObjectReference = "SPIORLL:N:P16/#PosLot#F16#kr12k90zc_ql3omg"
            }
         lotType = "Production"
         subLotType = "A"
         lotContent = "Wafer"
         lotStatus = "Waiting"
         strLotStatusList = 
            (pptLotStatusListSequence){
               item[] = 
                  (pptLotStatusList){
                     stateName = "Lot State"
                     stateValue = "ACTIVE"
                     siInfo = 
                        (CORBA.Any){
                           type = 
                              (CORBA.TypeCode){
                                 definition = None
                                 typename = None
                              }
                           value = ""
                        }
                  },
                  (pptLotStatusList){
                     stateName = "Lot Production State"
                     stateValue = "INPRODUCTION"
                     siInfo = 
                        (CORBA.Any){
                           type = 
                              (CORBA.TypeCode){
                                 definition = None
                                 typename = None
                              }
                           value = ""
                        }
                  },
                  (pptLotStatusList){
                     stateName = "Lot Hold State"
                     stateValue = "NOTONHOLD"
                     siInfo = 
                        (CORBA.Any){
                           type = 
                              (CORBA.TypeCode){
                                 definition = None
                                 typename = None
                              }
                           value = ""
                        }
                  },
                  (pptLotStatusList){
                     stateName = "Lot Finished State"
                     stateValue = None
                     siInfo = 
                        (CORBA.Any){
                           type = 
                              (CORBA.TypeCode){
                                 definition = None
                                 typename = None
                              }
                           value = ""
                        }
                  },
                  (pptLotStatusList){
                     stateName = "Lot Process State"
                     stateValue = "Waiting"
                     siInfo = 
                        (CORBA.Any){
                           type = 
                              (CORBA.TypeCode){
                                 definition = None
                                 typename = None
                              }
                           value = ""
                        }
                  },
                  (pptLotStatusList){
                     stateName = "Lot Inventory State"
                     stateValue = "OnFloor"
                     siInfo = 
                        (CORBA.Any){
                           type = 
                              (CORBA.TypeCode){
                                 definition = None
                                 typename = None
                              }
                           value = ""
                        }
                  },
            }
         dueTimeStamp = "2020-12-16-09.38.41.236572"
         priorityClass = "4"
         internalPriority = "-23"
         externalPriority = "1"
         totalWaferCount = 1
         productWaferCount = 1
         controlWaferCount = 0
         totalGoodDieCount = 0
         totalBadDieCount = 0
         bankID = 
            (objectIdentifier){
               identifier = None
               stringifiedObjectReference = None
            }
         qtimeFlag = False
         processLagTime = None
         parentLotID = 
            (objectIdentifier){
               identifier = None
               stringifiedObjectReference = None
            }
         vendorLotID = None
         familyLotID = 
            (objectIdentifier){
               identifier = "MA100261.001"
               stringifiedObjectReference = "SPIORLL:N:P16/#PosLotFamily#F16#rg12k92ek_ql3omg"
            }
         lastClaimedTimeStamp = "2020-12-16-15.12.56.327969"
         lastClaimedUserID = 
            (objectIdentifier){
               identifier = "AlbertYu"
               stringifiedObjectReference = "SPIORLL:N:P18/#PosPerson#F18#8p12n1zfo_q8hw7q"
            }
         stateChangeTimeStamp = "2020-12-16-15.08.16.402477"
         inventoryChangeTimeStamp = "2020-12-10-09.39.52.234513"
         requiredCassetteCategory = None
         sorterJobExistFlag = False
         inPostProcessFlagOfCassette = False
         inPostProcessFlagOfLot = False
         interFabXferState = "-"
         bondingGroupID = None
         autoDispatchControlFlag = False
         strEqpMonitorID = 
            (pptEqpMonitorID){
               equipmentID = 
                  (objectIdentifier){
                     identifier = 
                        (string){
                           _nil = "true"
                        }
                     stringifiedObjectReference = 
                        (string){
                           _nil = "true"
                        }
                  }
               chamberID = 
                  (objectIdentifier){
                     identifier = 
                        (string){
                           _nil = "true"
                        }
                     stringifiedObjectReference = 
                        (string){
                           _nil = "true"
                        }
                  }
               eqpMonitorID = 
                  (objectIdentifier){
                     identifier = 
                        (string){
                           _nil = "true"
                        }
                     stringifiedObjectReference = 
                        (string){
                           _nil = "true"
                        }
                  }
               eqpMonitorJobID = 
                  (objectIdentifier){
                     identifier = 
                        (string){
                           _nil = "true"
                        }
                     stringifiedObjectReference = 
                        (string){
                           _nil = "true"
                        }
                  }
               siInfo = 
                  (CORBA.Any){
                     type = 
                        (CORBA.TypeCode){
                           definition = None
                           typename = None
                        }
                     value = ""
                  }
            }
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotControlUseInfo = 
      (pptLotControlUseInfo){
         usedCount = 0
         recycleCount = 0
         controlUseState = None
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotFlowBatchInfo = 
      (pptLotFlowBatchInfo){
         flowBatchID = 
            (objectIdentifier){
               identifier = None
               stringifiedObjectReference = None
            }
         flowBatchReserveEquipmentID = 
            (objectIdentifier){
               identifier = 
                  (string){
                     _nil = "true"
                  }
               stringifiedObjectReference = 
                  (string){
                     _nil = "true"
                  }
            }
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotNoteFlagInfo = 
      (pptLotNoteFlagInfo){
         lotCommentFlag = False
         lotNoteFlag = False
         lotOperationNoteFlag = False
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotOperationInfo = 
      (pptLotOperationInfo__160){
         routeID = 
            (objectIdentifier){
               identifier = "OMOG_01.1"
               stringifiedObjectReference = "SPIORLL:N:P13/#PosProcessDefinition#F13#0r12n4viw_q8ikzn"
            }
         operationID = 
            (objectIdentifier){
               identifier = "MCDDIS.1"
               stringifiedObjectReference = "SPIORLL:N:P13/#PosProcessDefinition#F13#dp12n2aug_q8ijfm"
            }
         operationNumber = "100.600"
         operationName = "MCDDIS"
         stageID = 
            (objectIdentifier){
               identifier = "MA_DP"
               stringifiedObjectReference = "SPIORLL:N:P2/#PosStage#F2#th12o111g_q8i5kg"
            }
         maskLevel = None
         department = "MKDP"
         mandatoryOperationFlag = True
         processHoldFlag = False
         strLotEquipmentList = 
            (pptLotEquipmentListSequence){
               item[] = 
                  (pptLotEquipmentList){
                     equipmentID = 
                        (objectIdentifier){
                           identifier = "MDCOM01"
                           stringifiedObjectReference = "SPIORLL:N:P10/#PosMachine#F10#ax12n5qg0_q8gqnv"
                        }
                     equipmentName = None
                     siInfo = 
                        (CORBA.Any){
                           type = 
                              (CORBA.TypeCode){
                                 definition = None
                                 typename = None
                              }
                           value = ""
                        }
                  },
            }
         planStartTimeStamp = "1901-01-01-00.00.00.000000"
         planEndTimeStamp = "1901-01-01-00.00.00.000000"
         plannedEquipmentID = 
            (objectIdentifier){
               identifier = None
               stringifiedObjectReference = None
            }
         queuedTimeStamp = "2020-12-16-15.12.56.433430"
         testSpecID = 
            (objectIdentifier){
               identifier = None
               stringifiedObjectReference = None
            }
         inspectionType = None
         reworkCount = 0
         pdType = "Virtual"
         strBackOperationList = ""
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotOrderInfo = 
      (pptLotOrderInfo){
         orderNumber = "TP0200018"
         customerCode = "QXIC"
         shipRequireFlag = False
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotControlJobInfo = 
      (pptLotControlJobInfo){
         controlJobID = 
            (objectIdentifier){
               identifier = None
               stringifiedObjectReference = None
            }
         processReserveEquipmentID = 
            (objectIdentifier){
               identifier = 
                  (string){
                     _nil = "true"
                  }
               stringifiedObjectReference = 
                  (string){
                     _nil = "true"
                  }
            }
         processReserveUserID = 
            (objectIdentifier){
               identifier = 
                  (string){
                     _nil = "true"
                  }
               stringifiedObjectReference = 
                  (string){
                     _nil = "true"
                  }
            }
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotProductInfo = 
      (pptLotProductInfo__101){
         productID = 
            (objectIdentifier){
               identifier = "TES012-158A1.00"
               stringifiedObjectReference = "SPIORLL:N:P17/#PosProductSpecification#F17#4612lkrsc_ql3okr"
            }
         productType = "Wafer"
         productGroupID = 
            (objectIdentifier){
               identifier = "NM"
               stringifiedObjectReference = "SPIORLL:N:P17/#PosProductGroup#F17#7a12n78ts_q8pzdg"
            }
         technologyCode = "OMOG"
         manufacturingLayer = "1"
         reticleSetID = None
         bomID = 
            (objectIdentifier){
               identifier = 
                  (string){
                     _nil = "true"
                  }
               stringifiedObjectReference = 
                  (string){
                     _nil = "true"
                  }
            }
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotRecipeInfo = 
      (pptLotRecipeInfo__150){
         logicalRecipeID = 
            (objectIdentifier){
               identifier = "DPNORMAL.1"
               stringifiedObjectReference = "SPIORLL:N:P19/#PosLogicalRecipe#F19#0412neacg_q8iecx"
            }
         processMonitorProductID = 
            (objectIdentifier){
               identifier = None
               stringifiedObjectReference = None
            }
         reticleGroupSeq = ""
         FFEnforceFlag = False
         FBEnforceFlag = False
         testTypeID = 
            (objectIdentifier){
               identifier = None
               stringifiedObjectReference = None
            }
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotLocationInfo = 
      (pptLotLocationInfo){
         cassetteID = 
            (objectIdentifier){
               identifier = "MA100261"
               stringifiedObjectReference = "SPIORLL:N:P8/#PosCassette#F8#zj12k8neg_ql3olv"
            }
         transferStatus = "-"
         transferReserveUserID = None
         stockerID = 
            (objectIdentifier){
               identifier = 
                  (string){
                     _nil = "true"
                  }
               stringifiedObjectReference = 
                  (string){
                     _nil = "true"
                  }
            }
         equipmentID = 
            (objectIdentifier){
               identifier = 
                  (string){
                     _nil = "true"
                  }
               stringifiedObjectReference = 
                  (string){
                     _nil = "true"
                  }
            }
         shelfPositionX = 
            (string){
               _nil = "true"
            }
         shelfPositionY = 
            (string){
               _nil = "true"
            }
         shelfPositionZ = 
            (string){
               _nil = "true"
            }
         cassetteCategory = "Dummy"
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotWipOperationInfo = 
      (pptLotWipOperationInfo){
         responsibleRouteID = 
            (objectIdentifier){
               identifier = "OMOG_01.1"
               stringifiedObjectReference = "SPIORLL:N:P13/#PosProcessDefinition#F13#0r12n4viw_q8ikzn"
            }
         responsibleOperationID = 
            (objectIdentifier){
               identifier = "MCDDIS.1"
               stringifiedObjectReference = "SPIORLL:N:P13/#PosProcessDefinition#F13#dp12n2aug_q8ijfm"
            }
         responsibleOperationNumber = "100.600"
         responsibleOperationName = "MCDDIS"
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   strLotWaferAttributes = 
      (pptLotWaferAttributesSequence__150){
         item[] = 
            (pptLotWaferAttributes__150){
               waferID = 
                  (objectIdentifier){
                     identifier = "MA100261.001.01"
                     stringifiedObjectReference = "SPIORLL:N:P16/#PosWafer#F16#6u12k8xm8_ql3omg"
                  }
               cassetteID = 
                  (objectIdentifier){
                     identifier = "MA100261"
                     stringifiedObjectReference = "SPIORLL:N:P8/#PosCassette#F8#zj12k8neg_ql3olv"
                  }
               aliasWaferName = None
               slotNumber = 1
               productID = 
                  (objectIdentifier){
                     identifier = "TES012-158A1.00"
                     stringifiedObjectReference = "SPIORLL:N:P17/#PosProductSpecification#F17#4612lkrsc_ql3okr"
                  }
               grossUnitCount = 0
               goodUnitCount = 0
               repairUnitCount = 0
               failUnitCount = 0
               controlWaferFlag = False
               STBAllocFlag = False
               reworkCount = 0
               eqpMonitorUsedCount = 0
               siInfo = 
                  (CORBA.Any){
                     type = 
                        (CORBA.TypeCode){
                           definition = None
                           typename = None
                        }
                     value = ""
                  }
            },
      }
   entityInhibitions = ""
   strLotBackupInfo = 
      (pptLotBackupInfo){
         backupProcessingFlag = False
         currentLocationFlag = True
         transferFlag = False
         strBornSiteAddress = 
            (pptBackupAddress){
               hostName = None
               serverName = None
               itDaemonPort = None
               siInfo = 
                  (CORBA.Any){
                     type = 
                        (CORBA.TypeCode){
                           definition = None
                           typename = None
                        }
                     value = ""
                  }
            }
         strLotBackupSourceDataSeq = ""
         strLotBackupDestDataSeq = ""
         returnRouteID = 
            (objectIdentifier){
               identifier = 
                  (string){
                     _nil = "true"
                  }
               stringifiedObjectReference = 
                  (string){
                     _nil = "true"
                  }
            }
         returnOperationNumber = 
            (string){
               _nil = "true"
            }
         siInfo = 
            (CORBA.Any){
               type = 
                  (CORBA.TypeCode){
                     definition = None
                     typename = None
                  }
               value = ""
            }
      }
   siInfo = 
      (CORBA.Any){
         type = 
            (CORBA.TypeCode){
               definition = None
               typename = None
            }
         value = ""
      }
 }]
"""
