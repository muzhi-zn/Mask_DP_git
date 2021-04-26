import traceback

from django.http import JsonResponse
from django.shortcuts import render

from catalog.models import tool_maintain, tool_name_route
from jdv.models import mes_blank_code
from machine.models import writer_mapping
from maintain.models import maintain_change_log
from utilslibrary.base.base import BaseView
import json


class MaintainChangeLog(BaseView):
    def get(self, request):
        return render(request, 'system_maintain_change_log.html')

    def post(self, request):
        super().post(request)
        operation = request.POST.get('operation')
        table = request.POST.get('change_table')
        query_set = maintain_change_log.objects.filter()
        if operation:
            query_set = query_set.object.filter(operation=operation)
        if table:
            query_set = query_set.object.filter(table=table)
        query_list = list(query_set.values())[self.startIndex: self.endIndex]
        data = {'total': query_set.count(), 'rows': query_list}
        return JsonResponse(data, safe=False)


class MaintainChangeLogView(BaseView):
    def get(self, request):
        id = request.GET.get('id')
        query = maintain_change_log.objects.get(id=id)
        new_data = query.new_data
        old_data = query.old_data
        if new_data:
            new_data = json.loads(new_data.replace('\'', '"'))
        else:
            new_data = {'No': 'Data'}
        if old_data:
            old_data = json.loads(old_data.replace('\'', '"'))
        else:
            old_data = {'No': 'Data'}
        return render(request, 'system_maintain_change_log_view.html',
                      {'new_data': new_data, 'old_data': old_data})


class MaintainChangeLogRestore(BaseView):
    def get(self, request):
        try:
            id = request.GET.get('id')
            query = maintain_change_log.objects.get(id=id)
            data_id = query.data_id
            table = query.table
            if table == 'Writer Mapping':
                table_query = writer_mapping.objects.get(id=data_id)
                old_data = json.loads(query.old_data.replace('\'', '"'))
                operation = query.operation
                if operation == 'Delete':
                    table_query.is_delete = 0
                    table_query.save()
                    query.delete()
                if operation == 'Add':
                    table_query.is_delete = 1
                    table_query.save()
                    query.delete()
                if operation == 'Edit':
                    writer_mapping.objects.filter(id=data_id).update(**old_data)
                    query.delete()
            if table == 'Blank Code':
                table_query = mes_blank_code.objects.get(id=data_id)
                old_data = json.loads(query.old_data.replace('\'', '"'))
                operation = query.operation
                if operation == 'Delete':
                    table_query.is_delete = 0
                    table_query.save()
                    query.delete()
                if operation == 'Add':
                    table_query.is_delete = 1
                    table_query.save()
                    query.delete()
                if operation == 'Edit':
                    mes_blank_code.objects.filter(id=data_id).update(**old_data)
                    query.delete()
            if table == 'Tool Maintain':
                table_query = tool_maintain.objects.get(id=data_id)
                old_data = json.loads(query.old_data.replace('\'', '"'))
                operation = query.operation
                if operation == 'Delete':
                    table_query.is_delete = 0
                    table_query.save()
                    query.delete()
                if operation == 'Add':
                    table_query.is_delete = 1
                    table_query.save()
                    query.delete()
                if operation == 'Edit':
                    tool_maintain.objects.filter(id=data_id).update(**old_data)
                    query.delete()
            if table == 'Tool Name Route':
                table_query = tool_name_route.objects.get(id=data_id)
                old_data = json.loads(query.old_data.replace('\'', '"'))
                operation = query.operation
                if operation == 'Delete':
                    table_query.is_delete = 0
                    table_query.save()
                    query.delete()
                if operation == 'Add':
                    table_query.is_delete = 1
                    table_query.save()
                    query.delete()
                if operation == 'Edit':
                    tool_name_route.objects.filter(id=data_id).update(**old_data)
                    query.delete()
            return JsonResponse({'success': True, 'msg': 'Restore Success'}, safe=False)
        except:
            traceback.print_exc()
            return JsonResponse({'success': False, 'msg': 'Restore Failed'}, safe=False)
