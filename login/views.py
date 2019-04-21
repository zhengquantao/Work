from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from login.models import UserInfo, Execel
from io import BytesIO
import xlwt
from functools import wraps
from django.db.models import Count


def decorate(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        user = request.session.get('user')
        if user:
            return func(request, *args, **kwargs)
        else:
            return redirect('/')
    return inner


# 存数据到数据库中
def insert(request):
    area = request.GET.get('area')
    type = request.GET.get('type')
    phone = request.GET.get('phone')
    # datetime = request.GET.get('datetime')
    exit = Execel.objects.filter(phone=phone)
    if exit:
        return HttpResponse("存在了")
    Execel.objects.create(area=area, type=type, phone=phone)
    return HttpResponse("ok")


# 登入
def login(request):
    if request.method == "POST":
        name = request.POST.get('user')
        pwd = request.POST.get('pwd')

        user = UserInfo.objects.filter(name=name, pwd=pwd)
        if user:
            request.session['user'] = name
            return JsonResponse({"code": 1, 'url': '/index/'})
        else:
            return JsonResponse({"code": 0})
    return render(request, 'login.html')


# 导出
@decorate
def export_excel(request):
    start_time = request.GET.get('start', '')
    end_time = request.GET.get('end', '')
    types = request.GET.get('types', '')
    print('types:', types)

    # print('export_excel:', start_time, end_time)
    # 设置HTTPResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=content.xls'
    # 创建一个文件对象
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet')

    # 设置文件头的样式,这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
                font:
                    name Arial,
                    colour_index white,
                    bold on,
                    height 0xA0;
                align:
                    wrap off,
                    vert center,
                    horiz center;
                pattern:
                    pattern solid,
                    fore-colour 0x19;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """)

    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '地点名称', style_heading)
    sheet.write(0, 2, '类型名称', style_heading)
    sheet.write(0, 3, '手机号码', style_heading)
    sheet.write(0, 4, '时间日期', style_heading)

    # 写入数据
    data_row = 1
    # 这个是查询条件,可以根据自己的实际需求做调整.
    if types:
        if start_time != '' and start_time == end_time:
            start = start_time.replace('-', ',').split(',')
            # print(start[1])
            Excel = Execel.objects.filter(datetime__year=int(start[0]),
                                            datetime__month=int(start[1]),
                                            datetime__day=int(start[2]), type=types)
        elif start_time and end_time:
            Excel = Execel.objects.filter(datetime__range=(start_time, end_time), type=types)
        elif start_time:
            Excel = Execel.objects.filter(datetime__gte=start_time, type=types)
        elif end_time:
            Excel = Execel.objects.filter(datetime__lte=end_time, type=types)
        else:
            Excel = Execel.objects.filter(type=types)
    else:
        if start_time != '' and start_time == end_time:
            start = start_time.replace('-', ',').split(',')
            # print(start[1])
            Excel = Execel.objects.filter(datetime__year=int(start[0]),
                                            datetime__month=int(start[1]),
                                            datetime__day=int(start[2]))
        elif start_time and end_time:
            Excel = Execel.objects.filter(datetime__range=(start_time, end_time))
        elif start_time:
            Excel = Execel.objects.filter(datetime__gte=start_time)
        elif end_time:
            Excel = Execel.objects.filter(datetime__lte=end_time)
        else:
            Excel = Execel.objects.all()

    for i in Excel:
        # 格式化datetime
        datetime = i.datetime.strftime('%Y-%m-%d %H:%M:S')
        sheet.write(data_row, 0, i.id)
        sheet.write(data_row, 1, i.area)
        sheet.write(data_row, 2, i.type)
        sheet.write(data_row, 3, i.phone)
        sheet.write(data_row, 4, datetime)

        data_row = data_row + 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


@decorate
def show_excel(request):
    type_list = Execel.objects.values('type').annotate(Count('type'))
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    types = request.GET.get('types', '')
    print(type(types))
    if types != str(0):
        # 时间相同时
        if start != '' and start == end:
            cstart = start.replace('-', ',').split(',')
            # print(start[1])
            all_message = Execel.objects.filter(datetime__year=int(cstart[0]),
                                                datetime__month=int(cstart[1]),
                                                datetime__day=int(cstart[2]), type=types)
            # print(all_message, '===')
            # print(start)
            return render(request, 'index.html', {"all_message": all_message, "start": start, "end": end, 'types': types, 'type_list': type_list})
        # 有时间范围， 查询这个时间范围的
        elif start and end:
            all_message = Execel.objects.filter(datetime__range=(start, end), type=types)
            return render(request, 'index.html', {"all_message": all_message, "start": start, "end": end, 'types': types, 'type_list': type_list})
        # 只有开始时间， 查询比开始时间大的
        elif start:
            all_message = Execel.objects.filter(datetime__gte=start, type=types)
            return render(request, 'index.html', {"all_message": all_message, "start": start, "end": end, 'types': types, 'type_list': type_list})
        # 只有结束时间，查询比结束时间小的
        elif end:
            all_message = Execel.objects.filter(datetime__lte=end, type=types)
            return render(request, 'index.html', {"all_message": all_message, "start": start, "end": end, 'types': types, 'type_list': type_list})
        # 没有输入时间， 默认全部查询
        else:
            # response = {}
            all_message = Execel.objects.filter(type=types)
            # response['all_message'] = json.loads(serializers.serialize('json', all_message))
            # print(response)
            return render(request, 'index.html',
                          {"all_message": all_message, "start": start, "end": end, 'types': types, 'type_list': type_list})
    else:
        # 时间相同时
        if start != '' and start == end:
            cstart = start.replace('-', ',').split(',')
            # print(start[1])
            all_message = Execel.objects.filter(datetime__year=int(cstart[0]),
                                                datetime__month=int(cstart[1]),
                                                datetime__day=int(cstart[2]))
            # print(all_message, '===')
            # print(start)
            return render(request, 'index.html', {"all_message": all_message, "start": start, "end": end, 'types': types, 'type_list': type_list})
        # 有时间范围， 查询这个时间范围的
        elif start and end:
            all_message = Execel.objects.filter(datetime__range=(start, end))
            return render(request, 'index.html', {"all_message": all_message, "start": start, "end": end, 'types': types, 'type_list': type_list})
        # 只有开始时间， 查询比开始时间大的
        elif start:
            all_message = Execel.objects.filter(datetime__gte=start)
            return render(request, 'index.html', {"all_message": all_message, "start": start, "end": end, 'types': types, 'type_list': type_list})
        # 只有结束时间，查询比结束时间小的
        elif end:
            all_message = Execel.objects.filter(datetime__lte=end)
            return render(request, 'index.html', {"all_message": all_message, "start": start, "end": end, 'types': types, 'type_list': type_list})
        # 没有输入时间， 默认全部查询
        else:
            # response = {}
            all_message = Execel.objects.all()
            # response['all_message'] = json.loads(serializers.serialize('json', all_message))
            # print(response)
            return render(request, 'index.html', {"all_message": all_message, "start": start, "end": end, 'types': types, 'type_list': type_list})


# 主页
@decorate
def index(request):
    type_list = Execel.objects.values('type').annotate(Count('type'))
    test = Execel.objects.filter()
    # print('======', type_list)
    return render(request, 'index.html', {'type_list': type_list})


@decorate
def delete(request):
    Execel.objects.all().delete()
    return JsonResponse({"code": 1, 'url': '/index/'})
