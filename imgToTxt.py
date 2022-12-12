from paddleocr import PaddleOCR

# Paddleocr目前支持中英文、英文、法语、德语、韩语、日语，可以通过修改lang参数进行切换
# 参数依次为`ch`, `en`, `french`, `german`, `korean`, `japan`。
ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory


def img_to_txt(dd, alt=None):
    if alt is None:
        alt = []
    img_path = dd
    result = ocr.ocr(img_path, cls=True)
    for i in range(len(result[0])):
        alt.append(result[0][i][-1][0])
    return alt


g