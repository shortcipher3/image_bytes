# image_bytes

This project is for having low-level control of reading and writing raw and yuv images. It contains
a collection of methods that are useful for interacting with the raw bytes from images. If you don't
care to deal at the technical level you may be better served by trying `rawpixels.net` first. 
`opencv` now also supports converting a wide variety of bayer and yuv images.

## Examples

### Convert a IYUV to rgb
```
from image_bytes.image_bytes import *

yuv = file2arr('data/image_720x1280.yuv', 720, 1280, bpp=1, rowwise=True, yuv_channels=True)
y, u, v = arr2yuv(yuv)
color = yuv2rgb(y, u, v)
cv2.imwrite('output/image_720x1280.jpg', color[:, :, ::-1])
```

### Convert a IYUV to rgb
```
from image_bytes.image_bytes import *

yuv = file2arr('data/image_720x1280.yuv', 720, 1280, bpp=1, rowwise=True, yuv_channels=True)
y, u, v = arr2yuv(yuv)
color = yuv2rgb(y, u, v)
cv2.imwrite('output/image_720x1280.jpg', color[:, :, ::-1])
```

### Convert YUV NV12 to rgb

```
yuv = file2arr('data/image_1664x1664.yuv', 1664, 1664, bpp=1, rowwise=True, yuv_channels=True)
y, u, v = arr2yuv(yuv, interleaved=True)
cv2.imwrite('output/test.jpg', u)
color = yuv2rgb(y, u, v)
cv2.imwrite('output/image_1664x1664.jpg', color[:, :, ::-1])
```

### Y channel only
This yuv image has only the Y-channel:
```
y = file2arr('data/video_1080x1920.yuv', 1080, 1920, bpp=1, rowwise=True, yuv=False)
cv2.imwrite('output/1080x1920.jpg', y)
```

### Y channel only video
Since it is a video you can read multiple frames:
```
read_yuv_video('data/video_1080x1920.yuv', 'output/1080x1920_frame_', 1080, 1920, bpp=1, rowwise=True, yuv_channels=False, header_len=0)
```

### Y channel header
Sometimes video files have a header for each frame that must also be skipped.  This is an example
of skipping a header that contains meta data such as the height, width, frame number, format, etc.
```
y = file2arr('data/video_1080x1920_h40.yuv', 1080, 1920, offset=40, bpp=1, rowwise=True, yuv_channels=False)
cv2.imwrite('output/1080x1920.jpg', y)
```

### Y channel header video
Reading video frames while skipping headers:
```
read_yuv_video('data/video_1080x1920_h40.yuv', 'output/1080x1920_h40_frame_', 1080, 1920, bpp=1, rowwise=True, yuv_channels=False, header_len=40)
```

### Using OpenCV to convert
OpenCV now has functions that take care of YUV conversion.
```
yuv = file2arr('data/image_1664x1664.yuv', 1664, 1664, bpp=1, rowwise=True, yuv_channels=True)
bgr= cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
cv2.imwrite('output/opencv_1664x1664.jpg', bgr)
```
