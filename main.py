import os
import re
import shutil
import time

import fitz
import requests
import base64

import tkinter
import tkinter.messagebox

def remove_dir(filepath):
    """
    如果文件夹不存在就创建，如果文件存在就清空！
    """
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    else:
        shutil.rmtree(filepath)
        os.mkdir(filepath)


# 获取文件名称
def getfiles(file_name):
    list1 = []
    for filepath, dirnames, de_name in os.walk(file_name):
        for i in de_name:
            list1.append(os.path.join(filepath, i))
    return list1


# pdf转图片
def pyMuPDF_fitz(pdfPath, imagePath, num):
    pdfDoc = fitz.open(pdfPath)
    for pg in range(pdfDoc.pageCount):
        page = pdfDoc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=96
        zoom_x = 1.33333333  # (Source file.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = 1.33333333
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)

        if not os.path.exists(imagePath):  # 判断存放图片的文件夹是否存在
            os.makedirs(imagePath)  # 若图片文件夹不存在就创建

        pix.writePNG(imagePath + '/' + '%s.png' % num)  # 将图片写入指定的文件夹内
        break


def ocr(img_path: str) -> list:
    """
    根据图片路径，将图片转为文字，返回识别到的字符串列表

    """
    # 请求头
    global result
    headers = {
        'Host': 'cloud.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.76',
        'Accept': '*/*',
        'Origin': 'https://cloud.baidu.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://cloud.baidu.com/product/ocr/general',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    }
    # 打开图片并对其使用 base64 编码
    with open(img_path, 'rb') as f:
        img = base64.b64encode(f.read())
    data = {
        'image': 'data:image/jpeg;base64,' + str(img)[2:-1],
        'image_url': '',
        'type': 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic',
        'detect_direction': 'false'
    }
    # 开始调用 ocr 的 api,直到抓取到为dict为止
    while True:
        time.sleep(1)
        response = requests.post(
            'https://cloud.baidu.com/aidemo', headers=headers, data=data)
        result = response.json()['data']
        if isinstance(result, dict):
            break

    # 设置一个空的列表，后面用来存储识别到的字符串
    ocr_text = []
    if not result.get('words_result'):
        return []

    # 将识别的字符串添加到列表里面
    for r in result['words_result']:
        text = r['words'].strip()
        ocr_text.append(text)

    # 返回字符串列表
    return ocr_text


if __name__ == '__main__':
    print("正在准备转化中，请稍后。。。。。。。。。。。。。")
    filename = 'Source file'  # pdf文件路径
    imagePath = './temp'  # 临时图片路径
    resultFiles = './result/'

    remove_dir(imagePath)  # 清空图片文件夹路径
    remove_dir(resultFiles)  # 清空result文件夹

    num = 0
    alt = 0
    haofan = 1
    w_f = 1  # 目前完成的份数
    filenames = getfiles(filename)  # 获取PDF文件路径

    # 将PDF转换为全部转化为图片，放入到temp文件夹中
    for i in filenames:
        remove_dir(imagePath)
        pyMuPDF_fitz(i, imagePath, str(num))
        num += 1
        filenames2 = getfiles(imagePath)[0]  # 获取图片路径
        list1 = []  # 新PDF名称
        str1 = ''
        str2 = ''
        str3 = ''
        time.sleep(1)
        a = ocr(filenames2)
        try:
            str1 = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", a[a.index('物料批号') + 1])
            str2 = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", a[a.index('物料名称') + 1])
            str3 = a[a.index('物料代码') + 1]
            list1.append(str1 + "_" + str2 + "_" + str3)
        except:
            list1.append(str(alt) + "_" + str(alt) + "_" + str(alt))
            alt += 1

        ol = resultFiles + list1[0] + ".pdf"
        try:
            os.rename(i, ol)
        except:
            ol = resultFiles + list1[0] + "_" + str(haofan) + ".pdf"
            os.rename(i, ol)
            haofan += 1
        print("第 %s 份转换完成！" % w_f)
        w_f += 1
    print("*" * 20)
    print("全部转换完成！！")
    op = tkinter.messagebox.askokcancel('提示', '转换完成，是否打开结果目录进行转移文件')
    if op:
        a = os.getcwd()
        fl = a + "\\reslut\\"
        os.system("start result")

    remove_dir(imagePath)
