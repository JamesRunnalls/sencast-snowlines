#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" This adapter gets the snow-ice from a Polymer file """

import os
import subprocess
from snappy import ProductIO, ProductUtils, ProgressMonitor, jpy, Product, ProductData
ImageManager = jpy.get_type('org.esa.snap.core.image.ImageManager')
JAI = jpy.get_type('javax.media.jai.JAI')


def export_to_geotiff(input_file, name, bands):
    output_file = os.path.join(os.path.dirname(input_file), name)
    product = ProductIO.readProduct(input_file)
    width = product.getSceneRasterWidth()
    height = product.getSceneRasterHeight()
    out_product = Product('rgb', 'GeoTIFF', width, height)
    writer = ProductIO.getProductWriter('GeoTIFF')
    ProductUtils.copyGeoCoding(product, out_product)
    out_product.setProductWriter(writer)
    for band in bands:
        ProductUtils.copyBand(band, product, out_product, True)
    ProductIO.writeProduct(out_product, output_file, 'GeoTIFF')


    """red = product.getBand('RED')
    green = product.getBand('GREEN')
    blue = product.getBand('BLUE')
    bands = [red, green, blue]
    image_info = ProductUtils.createImageInfo(bands, True, ProgressMonitor.NULL)
    im = ImageManager.getInstance().createColoredBandImage(bands, image_info, 0)
    print(im)
    out_product = Product('rgb', 'rgb', width, height)
    writer = ProductIO.getProductWriter('GeoTIFF')
    ProductUtils.copyGeoCoding(product, out_product)
    out_product.setProductWriter(writer)
    out_band = out_product.addBand("rgb", ProductData.TYPE_FLOAT32)
    out_product.writeHeader(output_file)
    #out_band.writePixels(0, 0, width, height, im)
    out_product.closeIO()"""

export_to_rgb("/media/jamesrunnalls/JamesSSD/Eawag/EawagRS/Sencast/build/DIAS/output_data/snowline_run_sui_2019-12-14_2019-12-14/L2SNOW/L2SNOW_reproj_idepix_subset_S3A_OL_1_EFR____20191214T093535_20191214T093835_20191215T142923_0179_052_307_2160_LN1_O_NT_002.SEN3.nc")


