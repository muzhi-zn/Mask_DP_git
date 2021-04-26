from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from jdv.models import lot_info


@csrf_exempt
def test_create_jb_file(request):
    """测试创建jb文件的方法"""
    tip_no = request.POST.get('tip_no')  # 获取前端选中的tip_no
    print(tip_no)
    lot_list = lot_info.objects.filter(tip_no=tip_no)  # 查询tip_no下的所有lot
    for lot in lot_list:
        mask_name = lot.mask_name  # lot对应的mask_name
        print(mask_name)
    
    return JsonResponse({'success': True})
