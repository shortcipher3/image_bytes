
import argparse

parser = argparse.ArgumentParser(description='Convert raw images to jpg/png/etc\nCurrently supports YUV only')
parser.add_argument('--raw-path', type=str, help='path to the input image')
parser.add_argument('--out-path', default=None, type=str, help='path to the output image, format is determined based on extension, if not provided creates a jpg file')
parser.add_argument('--height', type=float, default=720)
parser.add_argument('--width', type=float, default=1280)
parser.add_argument('--bpp', type=str, default=1, help='bytes per pixel')
parser.add_argument('--rowwise', type=bool, default=False, help='True if model input is rgb, False if bgr (default is False)')
parser.add_argument('--yuv', type=bool, default=True, help='True if yuv False if y channel only')

from image_bytes.image_bytes import *
import cv2

args = parser.parse_args()
if not args.out_path:
    args.out_path = '.'.join(args.raw_path.split('.')[:-1]) + '.jpg'

yuv = file2arr(args.raw_path, args.width, args.height, bpp=args.bpp, rowwise=args.rowwise, yuv_channels=args.yuv)
color = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
cv2.imwrite(args.out_path, color)
