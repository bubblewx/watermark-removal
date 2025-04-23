import cv2
import numpy as np
import os
from glob import glob

# 图片列表
image_paths = sorted(glob('images/*.png'))  # 修改为你的路径
if not image_paths:
    raise FileNotFoundError("没有找到图像文件，请检查路径")

print(f"共加载 {len(image_paths)} 张图片")

# 初始化
brush_radius = 10
final_mask = None
base_size = None
drawing = False
ix, iy = -1, -1

def nothing(x):
    pass

# 鼠标绘图
def draw_mask(event, x, y, flags, param):
    global drawing, ix, iy, brush_radius

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cv2.circle(mask, (x, y), brush_radius, 255, -1)
            cv2.circle(img_show, (x, y), brush_radius, (0, 0, 255), -1)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.circle(mask, (x, y), brush_radius, 255, -1)
        cv2.circle(img_show, (x, y), brush_radius, (0, 0, 255), -1)

# 主处理流程
for idx, image_path in enumerate(image_paths):
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图像: {image_path}")
        continue

    if base_size is None:
        base_size = img.shape[:2]
        final_mask = np.zeros(base_size, dtype=np.uint8)

    # 调整图像大小
    img = cv2.resize(img, (base_size[1], base_size[0]))
    mask = np.zeros(base_size, dtype=np.uint8)
    img_show = img.copy()

    window_name = 'Draw Watermark Mask'
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, draw_mask)
    cv2.createTrackbar('Brush Size', window_name, brush_radius, 50, nothing)

    print(f"\n正在处理第 {idx+1}/{len(image_paths)} 张：{image_path}")
    print("→ 左键圈出水印，拖动滑块调节画笔")
    print("→ 按 'n' 下一张，按 'q' 立即退出")

    while True:
        brush_radius = max(1, cv2.getTrackbarPos('Brush Size', window_name))
        cv2.imshow(window_name, img_show)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('n'):  # 下一张
            break
        elif key == ord('q'):
            exit()

    cv2.destroyAllWindows()
    final_mask = cv2.bitwise_or(final_mask, mask)
    print("✅ 已添加本图的圈选区域到总 mask")

# 保存总 mask
cv2.imwrite("images/mask.png", final_mask)
print("\n🎉 所有圈选完成，已保存合成 mask：mask.png")
