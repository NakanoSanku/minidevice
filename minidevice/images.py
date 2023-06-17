import math
import urllib.request
import cv2
import numpy as np


class Colors:
    BLACK = "#FF000000"  # 黑色
    DKGRAY = "#FF444444"  # 深灰色
    GRAY = "#FF888888"  # 灰色
    LTGRAY = "#FFCCCCCC"  # 亮灰色
    WHITE = "#FFFFFFFF"  # 白色
    RED = "#FFFF0000"  # 红色
    GREEN = "#FF00FF00"  # 绿色
    BLUE = "#FF0000FF"  # 蓝色
    YELLOW = "#FFFFFF00"  # 黄色
    CYAN = "#FF00FFFF"  # 青色
    MAGENTA = "#FFFF00FF"  # 品红色
    TRANSPARENT = "#00000000"  # 透明

    def to_string(color):
        """
        to_string 16进制转颜色值的字符串

        Args:
            color (int): 0xFF112233

        Returns:
            颜色值的字符串 (str): 格式为 "#AARRGGBB"。
        """
        # 将整数RGB颜色值转换为16进制字符串
        hex_color = hex(color)[2:].upper().zfill(8)
        # 将16进制字符串转换为"AARRGGBB"格式的字符串
        a, r, g, b = [hex_color[i : i + 2] for i in range(0, 8, 2)]
        return f"#{a}{r}{g}{b}"

    def get_red(color):
        """
        get_red 返回颜色color的R通道的值,范围0~255.

        Args:
            color (int): 0xFF112233

        Returns:
            颜色color的R通道的值 (int): 范围0~255.
        """
        # 右移24位获取红色通道的值
        red = (color >> 16) & 0xFF
        return red

    def get_green(color):
        """
        get_green 返回颜色color的g通道的值,范围0~255.

        Args:
            color (int): 0xFF112233

        Returns:
            颜色color的g通道的值 (int): 范围0~255.
        """
        # 右移24位获取绿色通道的值
        green = (color >> 8) & 0xFF
        return green

    def get_blue(color):
        """
        get_blue 返回颜色color的b通道的值,范围0~255.

        Args:
            color (int): 0xFF112233

        Returns:
            颜色color的b通道的值 (int): 范围0~255.
        """
        # 右移24位获取蓝色通道的值
        blue = (color >> 0) & 0xFF
        return blue

    def is_similar(color1, color2, threshold=4, algorithm="diff"):
        """
        is_similar 返回两个颜色是否相似
        Args:
            color1 (int): 16进制颜色值
            color2 (int): 16进制颜色值
            threshold (int, optional): 相似度. Defaults to 4.
            algorithm (str, optional): 比较算法. Defaults to 'diff'.
                algorithm包括:
                    "diff": 差值匹配。与给定颜色的R、G、B差的绝对值之和小于threshold时匹配。
                    "rgb": rgb欧拉距离相似度。与给定颜色color的rgb欧拉距离小于等于threshold时匹配。
                    "rgb+": 加权rgb欧拉距离匹配(LAB Delta E)。
                    "hs": hs欧拉距离匹配。hs为HSV空间的色调值。
        - Returns:
            (两个颜色是否相似) bool: 
        """
        # 差值匹配算法
        if algorithm == "diff":
            r1 = (color1 >> 16) & 0xFF
            g1 = (color1 >> 8) & 0xFF
            b1 = color1 & 0xFF
            r2 = (color2 >> 16) & 0xFF
            g2 = (color2 >> 8) & 0xFF
            b2 = color2 & 0xFF
            diff = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
            return diff <= threshold
        # RGB欧拉距离相似度算法
        elif algorithm == "rgb":
            r1 = (color1 >> 16) & 0xFF
            g1 = (color1 >> 8) & 0xFF
            b1 = color1 & 0xFF
            r2 = (color2 >> 16) & 0xFF
            g2 = (color2 >> 8) & 0xFF
            b2 = color2 & 0xFF
            diff = math.sqrt(pow(r1 - r2, 2) + pow(g1 - g2, 2) + pow(b1 - b2, 2))
            return diff <= threshold
        # 加权RGB欧拉距离相似度算法
        elif algorithm == "rgb+":
            lab1 = rgb2lab(color1)
            lab2 = rgb2lab(color2)
            diff = deltaE(lab1, lab2)
            return diff <= threshold
        # HS欧拉距离相似度算法
        elif algorithm == "hs":
            hs1 = rgb2hs(color1)
            hs2 = rgb2hs(color2)
            diff = math.sqrt(pow(hs1[0] - hs2[0], 2) + pow(hs1[1] - hs2[1], 2))
            return diff <= threshold
        else:
            return False

    def parse_color(color_str):
        """
        parse_color 解析颜色值为16进制

        Args:
            color_str (str): "#112233"

        Returns:
            16进制颜色值 (int): 
        """
        color_str = color_str.strip("#")  # 移除字符串开头的 "#"
        red = int(color_str[0:2], 16)  # 提取红色分量并转换为整数
        green = int(color_str[2:4], 16)  # 提取绿色分量并转换为整数
        blue = int(color_str[4:6], 16)  # 提取蓝色分量并转换为整数
        color_value = (red << 16) + (green << 8) + blue  # 将分量组合为整数值
        return color_value


# RGB转LAB
def rgb2lab(color):
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    r = r / 255
    g = g / 255
    b = b / 255
    if r > 0.04045:
        r = pow((r + 0.055) / 1.055, 2.4)
    else:
        r = r / 12.92
    if g > 0.04045:
        g = pow((g + 0.055) / 1.055, 2.4)
    else:
        g = g / 12.92
    if b > 0.04045:
        b = pow((b + 0.055) / 1.055, 2.4)
    else:
        b = b / 12.92
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    x = x / 0.95047
    y = y / 1.00000
    z = z / 1.08883
    if x > 0.008856:
        x = pow(x, 1 / 3)
    else:
        x = (7.787 * x) + (16 / 116)
    if y > 0.008856:
        y = pow(y, 1 / 3)
    else:
        y = (7.787 * y) + (16 / 116)
    if z > 0.008856:
        z = pow(z, 1 / 3)
    else:
        z = (7.787 * z) + (16 / 116)
    l = (116 * y) - 16
    a = 500 * (x - y)
    b = 200 * (y - z)
    return [l, a, b]


# LAB Delta E
def deltaE(lab1, lab2):
    l1 = lab1[0]
    a1 = lab1[1]
    b1 = lab1[2]
    l2 = lab2[0]
    a2 = lab2[1]
    b2 = lab2[2]
    c1 = math.sqrt(pow(a1, 2) + pow(b1, 2))
    c2 = math.sqrt(pow(a2, 2) + pow(b2, 2))
    dc = c1 - c2
    dl = l1 - l2
    da = a1 - a2
    db = b1 - b2
    dh = math.sqrt(pow(da, 2) + pow(db, 2) - pow(dc, 2))
    k1 = 0.045
    k2 = 0.015
    sl = 1
    kc = 1
    kh = 1
    if l1 < 16:
        sl = (k1 * pow(l1 - 16, 2)) / 100
    if c1 < 16:
        kc = k1 * pow(c1, 2) / 100 + 1
    if dh < 180:
        kh = k2 * (dh**2) / 100 + 1
    return math.sqrt(
        pow(dl / (sl * k1), 2) + pow(dc / (kc * kc), 2) + pow(dh / (kh * kh), 2)
    )


# RGB转HS
def rgb2hs(color):
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    r = r / 255
    g = g / 255
    b = b / 255
    maxVal = max(r, g, b)
    minVal = min(r, g, b)
    diff = maxVal - minVal
    if diff == 0:
        h = 0
    elif maxVal == r:
        h = (g - b) / diff
        if h < 0:
            h += 6
    elif maxVal == g:
        h = (b - r) / diff + 2
    else:
        h = (r - g) / diff + 4
    h = h / 6
    s = 0 if maxVal == 0 else diff / maxVal
    return [h, s]


def raw2opencv(raw):
    """raw to opencv

    Args:
        raw (byte): raw

    Returns:
        opencv格式图像 (np.array): 
    """
    return cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)


class Images:
    def read(path, flag=cv2.IMREAD_COLOR):
        """
        read 读取图像

        Args:
            path (str): 图像路径
            flag (int) :
                - cv2.IMREAD_COLOR (默认)
                - cv2.IMREAD_GRAYSCALE

        Returns:
            opencv格式图像 (np.array): 
        """
        return cv2.imread(path, flags=flag)

    def load(path):
        """
        load 加载网络图片

        Args:
            path (str): 图像路径

        Returns:
            opencv格式图像 (np.array): 
        """

        # 下载图片数据
        response = urllib.request.urlopen(path)
        image_data = response.read()
        return raw2opencv(image_data)

    def show(img, title=""):
        """
        show 显示图像

        Args:
            img (mat): opencv格式图像
            title (str, optional): 显示的标题. Defaults to "".
        """
        cv2.imshow(title, img)
        cv2.waitKey()

    def save(img, path="save.png"):
        """
        save 保存图像到路径

        Args:
            path (str): 路径
            img (mat): opencv格式图像 默认保存到当前路径下save.png
        """
        cv2.imwrite(path, img)

    def pixel(img, x, y):
        """
        pixel 返回图片image在点(x, y)处的像素的RGB值。

        Args:
            img (Mat): opencv图像
            x (int): 横坐标
            y (int): 纵坐标

        Returns:
            坐标颜色值 (str): 
        """
        b, g, r = img[y, x]
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def find_color(img, color, region=None, threshold=4):
        """
        find_color 找色功能

        Args:
            img (mat): opencv格式图像
            color (str): 颜色值字符串
            region (list, optional): [xmin,ymin,xmax,ymax]. Defaults to None.
            threshold (int, optional): 颜色相似度. Defaults to 4.

        Returns:
            x (int): 
            y (int): 
        """
        x_min, y_min, x_max, y_max = region or (0, 0, img.shape[1], img.shape[0])
        img = img[y_min:y_max, x_min:x_max]
        # 将颜色值转换为 RGB 分量值
        r, g, b = np.array([int(color[i : i + 2], 16) for i in (1, 3, 5)])
        # 计算颜色差
        diff = np.abs(img - [b, g, r])
        # 判断颜色是否匹配
        match = np.logical_and.reduce(diff <= threshold, axis=2)
        # 获取匹配像素点的坐标
        y, x = np.where(match)
        return None if len(x) == 0 else x[0] + x_min, y[0] + y_min

    def find_all_color(img, color, region=None, threshold=4):
        """
        find_all_color 找到全图中所有符合要求的像素点

        Args:
            img (mat): opencv格式图像
            color (str): 颜色值字符串
            region (list, optional): [xmin,ymin,xmax,ymax]. Defaults to None.
            threshold (int, optional): 颜色相似度. Defaults to 4.

        Returns:
            颜色值所有点 (list): [(x,y),(x,y),(x,y)]
        """
        x_min, y_min, x_max, y_max = region or (0, 0, img.shape[1], img.shape[0])
        img = img[y_min:y_max, x_min:x_max]
        # 将颜色值转换为 RGB 分量值
        r, g, b = np.array([int(color[i : i + 2], 16) for i in (1, 3, 5)])
        # 计算颜色差
        diff = np.abs(img - [b, g, r])
        # 判断颜色是否匹配
        match = np.logical_and.reduce(diff <= threshold, axis=2)
        # 获取匹配像素点的坐标
        y, x = np.where(match)
        return (
            None
            if len(x) == 0
            else [(x[i] + x_min, y[i] + y_min) for i in range(len(x))]
        )

    def find_multi_colors(img, first_color, colors, region=None, threshold=4):
        """
        find_multi_colors 多点找色

        Args:
            img (mat): opencv格式图像
            first_color (str): 第一个图像的颜色值
            colors (list): [(x,y,color),(x,y,color)] x为相对第一个点偏移的坐标值,color为颜色值"#112233"
            region (list, optional): 范围数组[xmin,ymin,xmax,ymax]. Defaults to None.
            threshold (int, optional): 相似度. Defaults to 4.

        Returns:
            x (int): 第一个点的横坐标
            y (int): 第一个点的纵坐标
            
        """
        first_color_points = Images.find_all_color(
            img, first_color, region=region, threshold=threshold
        )
        if first_color_points is None:
            return None
        for x0, y0 in first_color_points:
            for x, y, target_color in colors:
                if not Colors.is_similar(
                    Colors.parse_color(target_color),
                    Colors.parse_color(Images.pixel(img, x + x0, y + y0)),
                    threshold=threshold,
                ):
                    break
            return x0, y0
        return None

    def find_image(img, template, threshold=0.8, region=None, level=3, debug=False):
        """
        find_image 模板匹配

        Args:
            img (mat): opencv格式图像
            template (mat): opencv格式图像
            threshold (float, optional): 匹配度. Defaults to 0.8.
            region (list, optional): 范围[xmin,ymin,xmax,ymax]. Defaults to None. 像素数量与查找效率几乎成正比
            level (int, optional): 图像金字塔等级. Defaults to 3. 全屏1080x2400查找情况下level3效率是level2的5倍,是level1的10倍,分辨率越低提升越不明显
            debug (bool,optional): 调试模式(方框绘制并显示) Defaults to False.
        Returns:
            max_loc (list): xmin,ymin,xmax,ymax
        """
        # 设置查找区域
        x_min, y_min, x_max, y_max = region or (0, 0, img.shape[1], img.shape[0])
        img = img[y_min:y_max, x_min:x_max]

        img_array = [img]
        template_array = [template]

        for i in range(1, level):
            img = cv2.pyrDown(img)
            template = cv2.pyrDown(template)
            img_array.append(img)
            template_array.append(template)

        for i, img_level, template_level in list(
            zip(range(level), img_array, template_array)
        )[::-1]:
            # 匹配模板图像
            res = cv2.matchTemplate(img_level, template_level, cv2.TM_CCOEFF_NORMED)
            # 选择相似度最高的一个结果
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > threshold:
                # 转换坐标系
                max_loc = (max_loc[0] * (2**i), max_loc[1] * (2**i))
                if region is not None:
                    max_loc = (max_loc[0] + x_min, max_loc[1] + y_min)
                if debug:
                    copy = img_array[0].copy()
                    cv2.rectangle(
                        copy,
                        [
                            max_loc[0],
                            max_loc[1],
                            template_array[0].shape[1],
                            template_array[0].shape[0],
                        ],
                        (0, 255, 0),
                        2,
                    )
                    Images.save(copy)
                return [
                    max_loc[0],
                    max_loc[1],
                    max_loc[0] + template_array[0].shape[1],
                    max_loc[1] + template_array[0].shape[0],
                ]
        return None

    def detect_and_compute_features(
        img, grayscale=True, method="SIFT", region=None, scale=1
    ):
        """
        detect_and_compute_features 计算特征点和描述值

        Args:
            img (mat): opencv格式图像
            grayscale (bool, optional): 是否灰度化图像. Defaults to True.
            method (str, optional): 特征点计算方法. Defaults to 'SIFT'.
            region (list, optional): 特征点计算范围[x_min, y_min, x_max, y_max]. Defaults to None.
            scale (int, optional): 图像缩放. Defaults to '1'. 分辨率较大时,计算效率与这个成正比

        Raises:
            ValueError: "Invalid feature detection method"

        Returns:
            特征点 (keypoints): 
            描述值 (descriptors): 
        """
        # 转换为灰度图像
        if grayscale:
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 选择特征计算方法
        if method == "SIFT":
            feature_detector = cv2.SIFT_create()
        elif method == "ORB":
            feature_detector = cv2.ORB_create()
        else:
            raise ValueError("Invalid feature detection method")

        x_min, y_min, x_max, y_max = region or (0, 0, img.shape[1], img.shape[0])
        img = img[y_min:y_max, x_min:x_max]
        img_new = cv2.resize(img, None, fx=scale, fy=scale)
        keypoints = feature_detector.detect(img_new)

        # 调整关键点坐标
        for kp in keypoints:
            kp.pt = ((kp.pt[0]) * (1 / scale), (kp.pt[1]) * (1 / scale))

        _, descriptors = feature_detector.compute(img, keypoints)
        # img = cv2.drawKeypoints(img,keypoints,img)
        # Images.save(f"{random.randint(8,100)}.png",img)
        # 返回特征信息
        return keypoints, descriptors

    def match_features(
        img,
        template,
        region=None,
        threshold=0.75,
        method="FLANNBASED",
        scale=1,
        debug=False,
    ):
        """
        match_features 特征匹配
        (计算小图花费不了多少资源,重要的是计算大图特,所以请务必区域特征计算)
        由于orb效果不尽人意,只采用sift计算特征
        计算2400x1080的大图消耗0.6s 500x1080的图消耗0.1s

        Args:
            img (mat): opencv格式图像 大图
            template (mat): opencv格式图像 小图
            region (list, optional): 大图特征范围[x_min, y_min, x_max, y_max ]. Defaults to None.
            threshold (float, optional): 相似度. Defaults to 0.75.
            method (str, optional): 特征匹配算法. Defaults to "FLANNBASED".其他可选"BRUTEFORCE","BRUTEFORCE_L1"
            scale (int, optional): 图像缩放. Defaults to '1'. 分辨率较大时,计算效率与这个成正比
            debug (bool,optional): 调试模式(方框绘制并显示) Defaults to False.

        Raises:
            ValueError: 算法不存在

        Returns:
            小图在大图中的范围 (list): [xmin,ymin,xmax,ymax]
        """
        # 计算关键点和描述符
        kp_template, des_template = Images.detect_and_compute_features(
            template, scale=scale
        )
        kp_target, des_target = Images.detect_and_compute_features(
            img, region=region, scale=scale
        )

        if method == "FLANNBASED":
            matcher = cv2.FlannBasedMatcher()
        elif method == "BRUTEFORCE_L1":
            matcher = cv2.BFMatcher(cv2.NORM_L1)
        elif method == "BRUTEFORCE":
            matcher = cv2.BFMatcher(cv2.NORM_L2)
        else:
            raise ValueError("Invalid matching method provided.")

        matches = matcher.knnMatch(des_template, des_target, k=2)

        # 应用Lowe的比例测试
        good_matches = []
        for m, n in matches:
            if m.distance < threshold * n.distance:
                good_matches.append(m)

        # 如果找到足够的好匹配，则计算单应性矩阵
        if len(good_matches) > 10:
            src_pts = np.float32(
                [kp_template[m.queryIdx].pt for m in good_matches]
            ).reshape(-1, 1, 2)
            dst_pts = np.float32(
                [kp_target[m.trainIdx].pt for m in good_matches]
            ).reshape(-1, 1, 2)

            # 计算单应性矩阵
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # 将模板图像的角点映射到目标图像中的相应位置
            h, w = template.shape[:2]
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(
                -1, 1, 2
            )
            dst = cv2.perspectiveTransform(pts, M)

            x_min, y_min, _, _ = region or (0, 0, img.shape[1], img.shape[0])
            # 计算矩形区域坐标
            x, y, w, h = cv2.boundingRect(dst)
            if debug:
                copy = img.copy()
                cv2.rectangle(copy, [x + x_min, y + y_min, w, h], (0, 255, 0), 2)
                Images.save(copy)
            return [x + x_min, y + y_min, w + x + x_min, h + y + y_min]

        else:
            print("Not enough matches are found - {}/{}".format(len(good_matches), 10))
            return None


if __name__ == "__main__":
    pass
