from __future__ import division
import os
import numpy as np
import cv2
from wand.image import Image
from skimage.measure import compare_ssim
import pdftotext

templateFolder = 'template'
matchingFolder = 'matching'
# All the 6 methods for comparison in a list
# methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR',
#             'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
templateLoad = list(map(lambda y: y[:-4], filter(lambda x: x[-3:] == 'pdf', os.listdir(templateFolder))))
matchingFiles = list(filter(lambda x: x[-3:] == 'pdf', os.listdir(matchingFolder)))
# matchingFiles = ['VN100944.pdf']
matchResult = []

templateImage = {}
templateWidth = {}
templateHeight = {}
remainWidth = {}
remainHeight = {}

for templateFile in templateLoad:
    if (not os.path.exists(templateFolder + '/' + templateFile + '.jpg')):
        with (Image(filename = templateFolder + '/' + templateFile + '.pdf', resolution = 360)) as source:
            pdfImage = source.convert("jpeg")
            page = Image(image = pdfImage.sequence[0])
            page.save(filename = templateFolder + '/' + templateFile + ".jpg")

    templateImage[templateFile] = cv2.imread(templateFolder + '/' + templateFile + '.jpg', 0)
    templateWidth[templateFile], templateHeight[templateFile] = templateImage[templateFile].shape[::-1]
    remainWidth[templateFile] = templateWidth[templateFile] * 0.1
    remainHeight[templateFile] = templateHeight[templateFile] * 0.1
    print(templateImage[templateFile].shape[::-1])

for file in matchingFiles:
    print(file)
    with (Image(filename = matchingFolder + '/' + file, resolution = 360)) as source:
        pdfImage = source.convert("jpeg")
        pageImage = Image(image = pdfImage.sequence[0])
        pageImage.save(filename = matchingFolder + '/image.jpg')

    image = cv2.imread(matchingFolder + '/image.jpg', 0)

    iW, iH = image.shape[::-1]

    # These below commented code is a stupid solution
    # print(image.shape[::-1])
    # if (iW < templateWidth or iH < templateHeight):
    #     matchResult.append([0])
    #     continue
    #
    # method = cv2.TM_CCOEFF
    # # Apply template Matching
    # res = cv2.matchTemplate(image, templateImage, method)
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    # if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
    #     top_left = min_loc
    # else:
    #     top_left = max_loc
    # bottom_right = (top_left[0] + templateWidth, top_left[1] + templateHeight)
    # print(top_left)
    # # print(bottom_right)
    #
    # if (sum(top_left) == 0):
    #     matchResult.append([1])
    # else:
    #     matchResult.append([0])

    resultDict = {}
    for template in templateImage:
        if (abs(iW - templateWidth[template]) > remainWidth[template] or abs(iH - templateHeight[template]) > remainHeight[template]):
            resultDict[template] = 0
            # os.remove(matchingFolder + '/image.jpg')
            continue
        elif (iW != templateWidth[template] or iH != templateHeight[template]):
            # print("resizing....")
            image = cv2.resize(image, (templateWidth[template], templateHeight[template]))
            iW, iH = image.shape[::-1]
        # print(remainWidth[template], remainHeight[template])

        score = compare_ssim(templateImage[template], image, win_size=3)
        # diff = (diff * 255).astype("uint8")
        print("SSIM: {}".format(score))
        if (score >= 0.9):
            resultDict[template] = 1
        elif (score >= 0.80):
            resultDict[template] = 2
        else:
            resultDict[template] = 0

    matchResult.append(resultDict)

    os.remove(matchingFolder + '/image.jpg')
    # cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 3)
    # cv2.imshow('image', cv2.resize(image, (540, 960)))
    # cv2.waitKey(0)

print(matchResult)

for result in matchResult:
    pass
# Tiep theo filter cac template co ket qua = 1
# Neu chi co 1 kq = 1 ===>> xong
# Co nhieu hon 2 kq = 1 ===>> Check tu khoa

# Neu khong co kq = 1, filter cac kq = 2
# Tiep tuc check tu khoa



# Check tu khoa:
# Kiem tra tat ca tu khoa trong config co xuat hien dung thu tu va day du khong
# Cho phep toi da 2 tu khoa khong xuat hien ===>> Nhieu hon thi bao la khong thuoc bat ky template nao
# Sau do tinh tong so tu khoa xuat hien dung, template nao co so luong nhieu nhat ===>> thuoc template do
