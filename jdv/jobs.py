# -*- coding: utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from Mask_DP import settings

# 实例化调度器
from catalog.alta_catalog import alta_ftp_job
from catalog.catalog_views import regist_check_job
from making.service.main_flow_service import mainFlow
from sap_webservice.service.rework_order_service import rework_order_job
from utilslibrary.mes_webservice.mes_webservice import get_wip_for_task, get_lots, get_operation_info_list, \
    cross_operations, monitor_mes_new_lot
from system.models import sync_config
from datetime import datetime

scheduler = BackgroundScheduler()


def get_scheduler():
    return scheduler


def run_jobs():
    if settings.JOB_RUN:
        try:
            # 调度器使用DjangoJobStore()
            scheduler.add_jobstore(DjangoJobStore(), "default")
            register_events(scheduler)
            # scheduler.add_job()
            scheduler.start()
        except Exception as e:
            print(e)
            # 有错误就停止定时器
            scheduler.shutdown()


# 设置定时任务，选择方式为interval，时间间隔为10s
# 另一种方式为每天固定时间执行任务，对应代码为：
# @register_job(scheduler, 'cron', day_of_week='mon-fri', hour='9', minute='30', second='10',id='task_time')
@register_job(scheduler, "interval", seconds=30)
def query_lot_id():  # 获取lotID
    get_lots()


@register_job(scheduler, "interval", seconds=90)
def get_wip():
    get_wip_for_task()  # 获取lot的详细信息


@register_job(scheduler, 'cron', day_of_week='mon-fri', hour='0', minute='0', second='0', id="operation_list")
def get_operation_list():
    get_operation_info_list()  # 获取站点信息


@register_job(scheduler, "interval", seconds=30)
def run_main_flow():
    """执行主流程的job方法"""
    mainFlow().run()
    mainFlow().run_writer_flow()


@register_job(scheduler, "interval", seconds=30)
def cross_operations_job():
    """执行自动过站"""
    cross_operations()


@register_job(scheduler, "interval", seconds=60)
def writer_regist_check():
    """确认Esp_DataRegist是否成功"""
    regist_check_job().regist_check()


@register_job(scheduler, "interval", seconds=300)
def monitor_mes_new_lot_job():
    """监听mes手动新起lot的job"""
    monitor_mes_new_lot()


@register_job(scheduler, "interval", seconds=300)
def sap_rework_order_job():
    rework_order_job()


@register_job(scheduler, "interval", seconds=60)
def catalog_alta_ftp_job():
    alta_ftp_job()