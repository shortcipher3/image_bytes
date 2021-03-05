#!/bin/env python
import numpy as np
import cv2
import struct

# TODO - deal with headers, continued reads smarter
# TODO remove unused code from the library
# TODO support different yuv formats, eg nv12

def clamp(a, lower, upper):
    """
    Clamp a value to the range provided by lower and upper, if the value is
    larger than upper returns upper, if lower than lower returns lower,
    otherwise returns the value
    Parameters
      a: a numpy array of values
      lower: the lowest value in the desired range
      upper: the highest value in the desired range
    """
    a[a>upper]=upper
    a[a<lower]=lower
    return a

def yuv2rgb(y, u, v):
    """
    Converts yuv channels into an rgb image
    Parameters
      y: the luminance channel
      u: one of the color channels
      v: one of the color channels
    Returns
      color: an image that is a color array
    """
    Y = y
    U = cv2.resize(u.astype(np.uint8), y.shape[::-1], interpolation=cv2.INTER_LINEAR)
    U = U.astype(np.float64)
    V = cv2.resize(v.astype(np.uint8), y.shape[::-1], interpolation=cv2.INTER_LINEAR)
    V = V.astype(np.float64)
    r = Y + (1.370705 * (V-128))
    g = Y - (0.698001 * (V-128)) - (0.337633 * (U-128))
    b = Y + (1.732446 * (U-128))
    r = clamp(r, 0, 255)
    g = clamp(g, 0, 255)
    b = clamp(b, 0, 255)
    return cv2.merge((r, g, b))

def file2arr(path, height, width, offset=0, bpp=2, rowwise=True, yuv_channels=False, bytes_read=False):
    """
    Converts an image file to an array
    Parameters
      path: the filepath to the image
      width: the image width
      height: the image height
      offset: offset to begin reading (useful for headers/video)
      bpp: the number of bytes per pixel
      yuv_channels: if True will read y, u, and v channels otherwise assumes 1 channel
      bytes_read: return the number of bytes read, useful if making multiple reads
    Returns
      array: the image as a numpy array of the designated size
      bytes_read: the number of bytes read
    """
    if bpp==1:
        byte_str = "<B"
        out_type = np.uint8
    elif bpp==2:
        byte_str = "<h"
        out_type = np.uint16
    else:
        raise("unsupported byte per pixel size: " + str(bpp))
    if yuv_channels:
        yuv_mult = 1.5
    else:
        yuv_mult = 1
    bytes_to_read = int(width*height*bpp*yuv_mult+offset)
    with open(path, 'rb') as f:
        val = f.read(bytes_to_read)
    vec = []
    for k in range(int(width*height*yuv_mult)):
        vec.append(struct.unpack(byte_str, val[(offset+bpp*k):(offset+bpp*(k+1))]))
    if rowwise:
        arr = np.reshape(vec, (int(height*yuv_mult), width))
    else:
        arr = np.reshape(vec, (int(width*yuv_mult), height))
    arr = arr.astype(out_type)
    if not bytes_read:
        return arr
    else:
        return arr, bytes_to_read

def arr2yuv(arr, yuv_order: bool=True):
    """
    Convert the flat array to y, u, and v arrays (IYUV-420 format)
    Parameters
      arr: the flat array
      yuv_order: True for yuv, False for yvu order
    Returns
      y: the y channel
      u: the u channel
      v: the v channel
    """
    height = int(arr.shape[0]/3.0*2.0)
    width = arr.shape[1]
    vec = arr.ravel()
    y = np.reshape(vec[:width*height], (height, width))
    u = np.reshape(vec[(width*height):(width*height+width*height//2//2)], (height//2, width//2))
    v = np.reshape(vec[(width*height+width*height//2//2):(width*height+width*height//2//2*2)], (height//2, width//2))
    if yuv_order:
        return y, u, v
    else:
        return y, v, u

def flat2channels(raw, offsets=[[[0,0]],[[1,0],[0,1]],[[1,1]]], blocksize=(2,2)):
    """
    Takes an (M,N) array of pixels and creates and (M,N,C) array of pixels,
    where C is the number of channels. Bayer patterns typically have 3 channels
    represented in a 2x2 block.
    Parameters
      raw: an (M,N) array of pixels
      offsets: a list of offsets in a block for each channel, for a Bayer
        pattern, typically something like [[[0,0]],[[1,0],[0,1]],[[1,1]]]
      blocksize: (w,h) the width and height of a block, for a Bayer pattern
        (2,2)
    Returns
      raw_channels: an (M,N,C) array of pixels
    """
    sw = blocksize[0] # step_width
    sh = blocksize[1] # step height
    channels = []
    for channel_offsets in offsets:
        channel = np.zeros(raw.shape, np.float32)
        for offset in channel_offsets:
            channel[offset[1]::sh, offset[0]::sw] = raw[offset[1]::sh, offset[0]::sw]
        channels.append(channel)
    raw_channels = np.stack(channels, axis=2)
    return raw_channels

def freeman_demosaic(raw_channels, bits=14):
    """
    Performs image demosaicking from a RAW image to a color image
    Parameters
      raw_channels: a numpy array representing an image, should be (M,N,3) with
        0 for missing values
    Returns
      color: a color image
    """
    color = raw_channels / (2.0**bits-1)
    h1 = np.array([[1,2,1],
                   [2,4,2],
                   [1,2,1]], dtype=np.float32)/4.0
    h2 = np.array([[0,1,0],
                   [1,4,1],
                   [0,1,0]], dtype=np.float32)/4.0
    color[:, :, 0] = cv2.filter2D(color[:, :, 0], cv2.CV_32F, h1)
    color[:, :, 1] = cv2.filter2D(color[:, :, 1], cv2.CV_32F, h2)
    color[:, :, 2] = cv2.filter2D(color[:, :, 2], cv2.CV_32F, h1)
    color = (color*255).astype(np.uint8)
    return color


def file2yuv(filepath, width=1920, height=1920, bts=1, color=1):
    """
    YUV I420
    for single image file
    to do color/grayscale, bytes better
    """
    if bts==2:
        with open(filepath, 'rb') as f:
            val = f.read(int(width*height*2*1.5))
        vec = []
        for k in range(int(width*height*1.5)):
            vec.append(struct.unpack("<h", val[(2*k):(2*(k+1))]))
    elif bts==1:
        with open(filepath, 'rb') as f:
            val = f.read(int(width*height*1.5))
        vec = []
        for k in range(int(width*height*1.5)):
            vec.append(struct.unpack("<B", val[k:(k+1)]))


    y = np.reshape(vec[:width*height], (height, width))
    u = np.reshape(vec[(width*height):(width*height+width*height//2//2)], (height//2, width//2))
    v = np.reshape(vec[(width*height+width*height//2//2):(width*height+width*height//2//2*2)], (height//2, width//2))

    return y, u, v

def yuvfile2rgb(filepath_in, filepath_out, x=1920, y=1920):
    y, u, v = file2yuv(filepath_in)
    rgb = yuv2rgb(y, u, v)
    cv2.imwrite(filepath_out, rgb)

def read_yuv_video(path, output_folder, width, height, bpp=1, rowwise=True, yuv_channels=False, header_len=0):
    idx = 0
    bytes_read = 0
    while True:
        offset = bytes_read + header_len
        try:
            arr, bytes_read = file2arr(path, width, height, offset=offset, bpp=bpp,
                                       rowwise=rowwise, yuv_channels=yuv_channels, bytes_read=True)
        except:
            break
        if yuv_channels:
            y, v, u = arr2yuv(arr)
            rgb = yuv2rgb(y, u, v)
            result = cv2.cvtColor(rgb.astype(np.uint8))
        else:
            result = arr.astype(np.uint8)
        cv2.imwrite(output_folder + str(idx) + ".png", result)
        idx += 1


