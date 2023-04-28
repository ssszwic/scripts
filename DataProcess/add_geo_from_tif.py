import matplotlib.pyplot as plt
from osgeo import gdal
import glob
import os
import argparse

#输入图像
def read_tif(path):
    dataset = gdal.Open(path)
    cols = dataset.RasterXSize#图像宽度
    rows = (dataset.RasterYSize)#图像高度
    im_proj = (dataset.GetProjection())#读取投影
    im_Geotrans = (dataset.GetGeoTransform())#读取仿射变换
    im_data = dataset.ReadAsArray(0, 0, cols, rows)#转为numpy格式
    #im_data[im_data > 0] = 1 #除0以外都等于1
    del dataset
    return im_proj, im_Geotrans, im_data
    # geoTransform[0]：左上角像素纬度
    # geoTransform[1]：影像宽度方向上的分辨率(经度范围/像素个数)
    # geoTransform[2]：x像素旋转, 0表示上面为北方
    # geoTransform[3]：左上角像素经度
    # geoTransform[4]：y像素旋转, 0表示上面为北方label_dict
    # geoTransform[5]：影像宽度方向上的分辨率(纬度范围/像素个数)


def get_base_name(full_names):
    """
    去掉前缀和后缀，支持列表和变量
    :param full_names: 文件的全名 '/DataProcess/big_cut.py'
    :return name: 文件的基础名 'big_cut'
    """
    if isinstance(full_names, list):
        names = []
        for full_name in full_names:
            _, long_name = os.path.split(full_name)
            name, _, = os.path.splitext(long_name)
            names.append(name)
        return names
    else:
        _, long_name = os.path.split(full_names)
        name, _, = os.path.splitext(long_name)
        return name

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_path', type=str, required=True, help='process tif path')
    parser.add_argument('--geo_path', type=str, required=True, help='src tif path')
    parser.add_argument('--save_path', type=str, required=True, help='new tif save path')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_opt()
    img_path = args.img_path
    geo_path = args.geo_path
    dst_path = args.save_path

    father_path, _ = os.path.split(dst_path)
    if not os.path.isdir(father_path): os.makedirs(father_path)

    # read img tif
    img_proj, img_Geotrans, img_data = read_tif(img_path)
    if img_data.shape[0] == 4:
        img_data  = img_data [0:3]

    # read source tif
    geo_proj, geo_Geotrans, _ = read_tif(geo_path)

    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(dst_path, img_data.shape[2], img_data.shape[1], 3, gdal.GDT_Byte)

    if dataset is not None:
        dataset.SetGeoTransform(geo_Geotrans)
        dataset.SetProjection(geo_proj)
        dataset.WriteArray(img_data)