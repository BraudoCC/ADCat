import pandas as pd
import numpy as np
from django.shortcuts import render
from django.http import HttpResponse
import os
from .models import *
import openpyxl
import csv
from test import adbench_cal, service1_cal, run_adgym


# Create your views here.
# 是adbench功能的第一个页面，主要用来展示用户上传的数据，为下一步选择算法打下基础。
def upload_file(request):
    if request.method == "POST":    # 请求方法为POST时，进行处理
        myfile = request.FILES.get("file_upload", None)    # 获取上传的文件，如果没有文件，则默认为None
        # algo = request.POST.get('choose_algo')
        if not myfile:
            return HttpResponse("no files for upload!")
        destination = open(os.path.join("media/", myfile.name), 'wb+')    # 打开特定的文件进行二进制的写操作
        for chunk in myfile.chunks():      # 分块写入文件
            destination.write(chunk)
        destination.close()

        # 若有登录信息，就存下，否则email置空；
        # if request.session['user_email']:
        user_email = request.session.get('user_email', None)
        # 存储文件名
        filename = myfile.name
        # 存入表AdbenchUpload
        AdbenchUpload.objects.create(user_email=user_email, file=filename, algo='Tobeadded')

        # wb = openpyxl.load_workbook(myfile)

        # 读取用户上传的数据
        default_road = 'media/'  # 文件存储的相对路径
        load_path = default_road + str(myfile.name)  # 加上文件名就是打开文件的路径
        if load_path.endswith(".xlsx"):
            wb = openpyxl.load_workbook(myfile)
            # 获得excel的第一张表
            worksheet = wb.worksheets[0]
            # 获取第一行，作为table的thead
            thead_data = list()
            for cell in worksheet[1]:
                thead_data.append(str(cell.value))

            # 获取从第二行开始的数据内容，作为table的tbody
            max_row_num = worksheet.max_row
            excel_data = list()
            for row in range(2, max_row_num + 1):
                row_data = list()
                for cell in worksheet[row]:
                    row_data.append(str(cell.value))
                excel_data.append(row_data)
            # global global_excel_data
            # global_excel_data = excel_data

        elif load_path.endswith(".csv"):
            # csv_file = open(load_path, 'r', newline='', encoding='utf-8')
            # reader = csv.reader(csv_file)
            csvfile = pd.read_csv(load_path)
            data = csvfile.values[:, :]
            # 获取第一行，作为table的thead
            order1 = np.array(csvfile.columns)
            thead_data = order1.tolist()

            # 获取从第二行开始的数据内容，作为table的tbody
            excel_data = data.tolist()

        global global_excel_data
        global_excel_data = excel_data
        global global_thead_data
        global_thead_data = thead_data

        return render(request, 'adbench_choose_algo.html', {"filename": filename,
                                                            "thead_data": thead_data,
                                                            "excel_data": excel_data})


# 是adbench的第二个页面，主要是加上了score的数据展示
def show_result(request):
    notselected = request.POST.getlist('Checkbox', []) # 不入模的列，值是列表list
    algo = request.POST.get('choose_algo') # 算法，值是文本
    islabel = request.POST.get('islabel')  # 标签列，值是文本

    if request.session.get('user_email'):  # 如果用户登陆了
        user_email = request.session.get('user_email')
        # 把数据库中关于algo的信息补全
        AdbenchUpload.objects.filter(user_email=user_email, algo='Tobeadded').update(algo=algo)
        # 并且获得该用户最近一次使用特定算法的数据，取出文件名
        latest_data = AdbenchUpload.objects.filter(user_email=user_email, algo=algo).last()
        filename = latest_data.file
    else:
        # 获得该用户最近一次的数据，取出文件名（依然会进行异常检测，毕竟algo是接收到了的；只是不会在数据库中记录）
        latest_data_nolog = AdbenchUpload.objects.filter(algo='Tobeadded').last()
        filename = latest_data_nolog.file


    # 读取用户上传的数据
    default_road = 'media/'  # 文件存储的相对路径
    load_path = default_road + str(filename)  # 加上文件名就是打开文件的路径
    if load_path.endswith(".xlsx"):
        df = pd.read_excel(load_path, sheet_name='Sheet1')
    elif load_path.endswith(".csv"):
        df = pd.read_csv(load_path)

    # 根据用户选择的：不入模的列，删除指定列（这里以列名为索引；如果用列号索引，会隔列删除，永动机删除）
    # notselected = [int(x) for x in notselected]
    # 如果用户选了“没有不入模的列”，那么不删除任何列(下面这个逻辑已经足够）
    for item in notselected:
        if item in df.columns:
            df = df.drop(item, axis=1)
        else:
            df = df

    # 更新数据（这一次删除指定列）,重新存储excel
    new_file_name = f'{filename}'  # 更新的文件名：和原文件名字相同
    file_path = os.path.join(default_road, new_file_name)
    if load_path.endswith(".xlsx"):
        df.to_excel(file_path, index=False)  # index=True是保留索引列，False不保留
    elif load_path.endswith(".csv"):
        df.to_csv(file_path, index=False)

    # 使用test.py中的adbench_cal函数，计算得到anomaly score
    anomaly_score, features_num, nums = adbench_cal(filename, algo, islabel)

    # 添加新列"Anomaly score"
    df['Anomaly score'] = anomaly_score

    # 再次更新数据（这一次加上anomaly score）,重新存储excel
    new_file_name = f'{filename}'  # 更新的文件名：和原文件名字相同
    file_path = os.path.join(default_road, new_file_name)
    if file_path.endswith(".xlsx"):
        df.to_excel(file_path, index=False)  # index=True是保留索引列，False不保留
        # 读取更新后的数据
        wb = openpyxl.load_workbook(file_path)
        # 获取数据的第一张表
        worksheet = wb.worksheets[0]
        # 获取第一行，作为table的thead
        thead_data = list()
        for cell in worksheet[1]:
            thead_data.append(str(cell.value))

        # 获取从第二行开始的数据内容，作为table的tbody
        max_row_num = worksheet.max_row
        excel_data = list()
        for row in range(2, max_row_num + 1):
            row_data = list()
            for cell in worksheet[row]:
                row_data.append(str(cell.value))
            excel_data.append(row_data)
    elif file_path.endswith(".csv"):
        df.to_csv(file_path, index=False)
        csvfile = pd.read_csv(file_path)
        data = csvfile.values[:, :]
        # 获取第一行，作为table的thead
        order1 = np.array(csvfile.columns)
        thead_data = order1.tolist()

        # 获取从第二行开始的数据内容，作为table的tbody
        excel_data = data.tolist()

    global global_excel_data
    global_excel_data = excel_data
    global global_thead_data
    global_thead_data = thead_data

    return render(request, 're.html', {'islabel': islabel, 'algo': algo, 'filename': filename, "thead_data": thead_data,
                                       "excel_data": excel_data, "notselected": notselected,
                                       "features_num": features_num, "nums": nums})


# 是在线训练的页面唯一展示，直接展示加上了score的数据
def service1_result(request):
    myfile = request.FILES.get("service1_file", None)    # 获取上传的文件，如果没有文件，则默认为None
    if not myfile:
        return HttpResponse("no files for upload!")
    destination = open(os.path.join("media/service1/", myfile.name), 'wb+')    # 打开特定的文件进行二进制的写操作
    for chunk in myfile.chunks():      # 分块写入文件
        destination.write(chunk)
    destination.close()
    filename = myfile.name

    # 读取用户上传的数据
    default_road = 'media/service1/'  # 文件存储的相对路径
    load_path = default_road + str(filename)  # 加上文件名就是打开文件的路径
    if load_path.endswith(".xlsx"):
        df = pd.read_excel(load_path, sheet_name='Sheet1')
    elif load_path.endswith(".csv"):
        df = pd.read_csv(load_path)

    # 使用test.py中的service1_cal函数，计算得到anomaly score
    anomaly_score, anomaly_num, features_num, nums = service1_cal(filename)

    # 添加新列"Anomaly score"
    df['Anomaly score'] = anomaly_score

    # 再次更新数据（这一次加上anomaly score）,重新存储excel
    new_file_name = f'{filename}'  # 更新的文件名：和原文件名字相同
    file_path = os.path.join(default_road, new_file_name)
    if file_path.endswith(".xlsx"):
        df.to_excel(file_path, index=False)  # index=True是保留索引列，False不保留
        # 读取更新后的数据
        wb = openpyxl.load_workbook(file_path)
        # 获取数据的第一张表
        worksheet = wb.worksheets[0]
        # 获取第一行，作为table的thead
        thead_data = list()
        for cell in worksheet[1]:
            thead_data.append(str(cell.value))

        # 获取从第二行开始的数据内容，作为table的tbody
        max_row_num = worksheet.max_row
        excel_data = list()
        for row in range(2, max_row_num + 1):
            row_data = list()
            for cell in worksheet[row]:
                row_data.append(str(cell.value))
            excel_data.append(row_data)
    elif file_path.endswith(".csv"):
        df.to_csv(file_path, index=False)
        csvfile = pd.read_csv(file_path)
        data = csvfile.values[:, :]
        # 获取第一行，作为table的thead
        order1 = np.array(csvfile.columns)
        thead_data = order1.tolist()

        # 获取从第二行开始的数据内容，作为table的tbody
        excel_data = data.tolist()

    global global_excel_data
    global_excel_data = excel_data
    global global_thead_data
    global_thead_data = thead_data

    return render(request, 'service1_re.html', {'filename': filename, "thead_data": thead_data, "excel_data": excel_data,
                                                'anomaly_num': anomaly_num, "features_num": features_num, "nums": nums})


# 是adgym的第一个页面，只展示best_pipeline
def adgym_re1(request):
    myfile = request.FILES.get("adgym_file", None)    # 获取上传的文件，如果没有文件，则默认为None
    if not myfile:
        return HttpResponse("no files for upload!")
    destination = open(os.path.join("media/adgym/", myfile.name), 'wb+')    # 打开特定的文件进行二进制的写操作
    for chunk in myfile.chunks():      # 分块写入文件
        destination.write(chunk)
    destination.close()
    filename = myfile.name

    # 使用test.py中的run_adgym函数，计算得到best_pipeline, fit_time, score
    best_pipeline_list, fit_time, anomaly_score = run_adgym(filename)
    # parameters=['augmentation','preprocess','network_architecture','hidden_size','act_fun','dropout',
    #             'network_initialization','trainging_strategy','loss_name','optimizer_name','batch_resample',
    #             'epochs','batch_size','lr','weight_decay']
    # for i in best_pipeline_list:
    #     parameters[i] = i
    augmentation = best_pipeline_list[0]
    preprocess = best_pipeline_list[1]
    network_architecture = best_pipeline_list[2]
    hidden_size = best_pipeline_list[3]
    act_fun = best_pipeline_list[4]
    dropout = best_pipeline_list[5]
    network_initialization = best_pipeline_list[6]
    trainging_strategy = best_pipeline_list[7]
    loss_name = best_pipeline_list[8]
    optimizer_name = best_pipeline_list[9]
    batch_resample = best_pipeline_list[10]
    epochs = best_pipeline_list[11]
    batch_size = best_pipeline_list[12]
    lr = best_pipeline_list[13]
    weight_decay = best_pipeline_list[14]


    # 若有登录信息，就存下，否则email置空；
    # if request.session['user_email']:
    user_email = request.session.get('user_email', None)
    # 存储文件名
    filename = myfile.name
    # 存入表adgym_info
    adgym_info.objects.create(user_email=user_email, file=filename, best_pipeline=best_pipeline_list, fit_time=fit_time,
                              anomaly_score=anomaly_score)


    # 读取用户上传的数据
    default_road = 'media/adgym/'  # 文件存储的相对路径
    load_path = default_road + str(myfile.name)  # 加上文件名就是打开文件的路径
    if load_path.endswith(".xlsx"):
        wb = openpyxl.load_workbook(myfile)
        # 获得excel的第一张表
        worksheet = wb.worksheets[0]
        # 获取第一行，作为table的thead
        thead_data = list()
        for cell in worksheet[1]:
            thead_data.append(str(cell.value))

        # 获取从第二行开始的数据内容，作为table的tbody
        max_row_num = worksheet.max_row
        excel_data = list()
        for row in range(2, max_row_num + 1):
            row_data = list()
            for cell in worksheet[row]:
                row_data.append(str(cell.value))
            excel_data.append(row_data)

    elif load_path.endswith(".csv"):
        csvfile = pd.read_csv(load_path)
        data = csvfile.values[:, :]
        # 获取第一行，作为table的thead
        order1 = np.array(csvfile.columns)
        thead_data = order1.tolist()

        # 获取从第二行开始的数据内容，作为table的tbody
        excel_data = data.tolist()

    global global_excel_data
    global_excel_data = excel_data
    global global_thead_data
    global_thead_data = thead_data

    return render(request, 'adgym_re1.html', {'filename': filename, "thead_data": thead_data, "excel_data": excel_data,
                                              'augmentation':augmentation,'preprocess':preprocess,
                                              'network_architecture':network_architecture,'hidden_size':hidden_size,
                                              'act_fun':act_fun,'dropout':dropout,'network_initialization':network_initialization,
                                              'trainging_strategy':trainging_strategy,'loss_name':loss_name,
                                              'optimizer_name':optimizer_name,'batch_resample':batch_resample,
                                              'epochs':epochs,'batch_size':batch_size,'lr':lr,'weight_decay':weight_decay
                                              })


# 是adgym的第二个页面，这一步展示fit_time和anomaly_score
def adgym_re2(request):
    if request.session.get('user_email'):  # 如果用户登陆了
        user_email = request.session.get('user_email')
        # 获得该用户最近一次的数据，取出文件名
        latest_data = adgym_info.objects.filter(user_email=user_email).last()
        filename = latest_data.file
    else:
        # 获得数据库记录的最近一次的数据，取出文件名
        latest_data_nolog = adgym_info.objects.last()
        filename = latest_data_nolog.file

    # 读取用户上传的数据
    default_road = 'media/adgym/'  # 文件存储的相对路径
    load_path = default_road + str(filename)  # 加上文件名就是打开文件的路径
    if load_path.endswith(".xlsx"):
        df = pd.read_excel(load_path, sheet_name='Sheet1')
    elif load_path.endswith(".csv"):
        df = pd.read_csv(load_path)

    # 使用test.py中的run_adgym函数，计算得到best_pipeline, fit_time, score
    best_pipeline_list, fit_time, anomaly_score = run_adgym(filename)
    augmentation = best_pipeline_list[0]
    preprocess = best_pipeline_list[1]
    network_architecture = best_pipeline_list[2]
    hidden_size = best_pipeline_list[3]
    act_fun = best_pipeline_list[4]
    dropout = best_pipeline_list[5]
    network_initialization = best_pipeline_list[6]
    trainging_strategy = best_pipeline_list[7]
    loss_name = best_pipeline_list[8]
    optimizer_name = best_pipeline_list[9]
    batch_resample = best_pipeline_list[10]
    epochs = best_pipeline_list[11]
    batch_size = best_pipeline_list[12]
    lr = best_pipeline_list[13]
    weight_decay = best_pipeline_list[14]

    fit_time = format(fit_time, '.4f')

    # 添加新列"Anomaly score"
    df['Anomaly score'] = anomaly_score

    # 再次更新数据（这一次加上anomaly score）,重新存储excel
    new_file_name = f'{filename}'  # 更新的文件名：和原文件名字相同
    file_path = os.path.join(default_road, new_file_name)
    if file_path.endswith(".xlsx"):
        df.to_excel(file_path, index=False)  # index=True是保留索引列，False不保留
        # 读取更新后的数据
        wb = openpyxl.load_workbook(file_path)
        # 获取数据的第一张表
        worksheet = wb.worksheets[0]
        # 获取第一行，作为table的thead
        thead_data = list()
        for cell in worksheet[1]:
            thead_data.append(str(cell.value))

        # 获取从第二行开始的数据内容，作为table的tbody
        max_row_num = worksheet.max_row
        excel_data = list()
        for row in range(2, max_row_num + 1):
            row_data = list()
            for cell in worksheet[row]:
                row_data.append(str(cell.value))
            excel_data.append(row_data)
    elif file_path.endswith(".csv"):
        df.to_csv(file_path, index=False)
        csvfile = pd.read_csv(file_path)
        data = csvfile.values[:, :]
        # 获取第一行，作为table的thead
        order1 = np.array(csvfile.columns)
        thead_data = order1.tolist()

        # 获取从第二行开始的数据内容，作为table的tbody
        excel_data = data.tolist()

    global global_excel_data
    global_excel_data = excel_data
    global global_thead_data
    global_thead_data = thead_data

    return render(request, 'adgym_re2.html',
                  {'filename': filename, "thead_data": thead_data, "excel_data": excel_data,
                  'augmentation':augmentation,'preprocess':preprocess,
                  'network_architecture':network_architecture,'hidden_size':hidden_size,
                  'act_fun':act_fun,'dropout':dropout,'network_initialization':network_initialization,
                  'trainging_strategy':trainging_strategy,'loss_name':loss_name,
                  'optimizer_name':optimizer_name,'batch_resample':batch_resample,
                  'epochs':epochs,'batch_size':batch_size,'lr':lr,'weight_decay':weight_decay, 'time': fit_time})

