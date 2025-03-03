import rasterio
from rasterio.transform import from_origin
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.path import Path



def read_tif_to_array(file_path: str) -> np.ndarray:
    """
    读取 TIFF 文件并返回一个二维 float 数组
    Reads a TIFF file and returns a 2D float array
    """
    with rasterio.open(file_path) as src:
        array = src.read(1).astype(np.float32)
        return array



def crop_and_resize_tif(tif_path: str, roi: tuple, output_size=(100, 100)) -> np.ndarray:
    """
    裁剪 TIFF 图像并调整到 100x100 大小 (无 OpenCV 版本)。

    参数：
    - tif_path (str): TIFF 文件路径
    - roi (tuple): 感兴趣区域 (xmin, ymin, xmax, ymax) 以像素坐标表示
    - output_size (tuple): 输出数组大小，默认 (100, 100)且outputsize必须是一个正方形

    返回：
    - np.ndarray: 100x100 处理后的二维数组
    Crop TIFF image and resize to 100x100 (no OpenCV version).

    Parameters:
    - tif_path (str): TIFF file path
    - roi (tuple): region of interest (xmin, ymin, xmax, ymax) in pixel coordinates
    - output_size (tuple): output array size, default (100, 100) and output size must be a square

    Returns:
    - np.ndarray: 100x100 processed 2D array
    """
    with rasterio.open(tif_path) as src:

        full_array = src.read(1)

        xmin, ymin, xmax, ymax = roi
        #数组切片操作，切得我们需要的这部分array
        # Array slicing operation, cut the part of the array we need
        cropped_array = full_array[ymin:ymax, xmin:xmax]

        # 原始裁剪区域的尺寸
        #original area size
        original_height, original_width = cropped_array.shape

        #当期望裁剪的地图尺寸（output_size）大于等于原始裁剪区域尺寸 ,直接返回原始裁剪区域
        # When the desired cropped map size (output_size) is greater than or equal to the original
        # cropped area size, return directly to the original cropped area
        if calculate_square_Length(tif_path, roi)==output_size or calculate_square_Length(tif_path, roi)[0] < output_size[0]:
            return cropped_array

        # 计算缩放比例 (均值池化的块大小)
        #当从原本size缩小到outputsize时，每个block_size_x*block_size_y的区域会被缩小成一个pixel，
        # 取block_size_x*block_size_y的平均值，赋给最终的这个缩小后的pixel
        # Calculate the scaling ratio (block size of mean pooling)
        # When shrinking from the original size to outputsize,
        # each block_size_x*block_size_y area will be shrunk to one pixel,
        # Take the average of block_size_x*block_size_y and assign it to the final shrunk pixel
        block_size_y = original_height // output_size[0]
        block_size_x = original_width // output_size[1]

        # 使用均值池化来缩小数组大小
        #去除所有的多余的像素，确保数组会成为outputsize这么大小的像素
        small_array = cropped_array[:block_size_y * output_size[0], :block_size_x * output_size[1]]
        small_array = small_array.reshape(output_size[0], block_size_y, output_size[1], block_size_x)
        resized_array = small_array.mean(axis=(1, 3))
        return resized_array


def save_array_to_tif(array: np.ndarray, output_path: str,reference_tif_path: str = None,
                      nodata_value: float = -3.4028227e+38) -> None:
    """
    将二维数组保存为新的 GeoTIFF 文件。

    参数：
    - array (np.ndarray): 要保存的二维数组 (float32)。
    - output_path (str): 输出 TIFF 文件的路径。
    - reference_tif_path (str, 可选): 参考的原始 TIFF 文件路径，用于复制元数据。
    - nodata_value (float): 用于填充无数据值的数值，默认与原始 TIFF 文件相同。
    Save a 2D array as a new GeoTIFF file.

    Parameters:
    - array (np.ndarray): The 2D array (float32) to save.
    - output_path (str): The path to the output TIFF file.
    - reference_tif_path (str, optional): The path to the original TIFF file to copy metadata.
    - nodata_value (float): The value to fill in nodata values,
    defaults to the same as the original TIFF file.

    """
    if reference_tif_path:
        # get meta data
        with rasterio.open(reference_tif_path) as src:
            metadata = src.meta.copy()
            transform = src.transform
            crs = src.crs
    else:
        # if no reference file, use default data
        metadata = {
            'driver': 'GTiff',
            'dtype': 'float32',
            'nodata': nodata_value,
            'width': array.shape[1],
            'height': array.shape[0],
            'count': 1,
            'crs': None,  # 默认无坐标参考系
            'transform': from_origin(0, 0, 1, 1)  # 简单的像素坐标系
        }
        transform = metadata['transform']
        crs = metadata['crs']

    # 更新元数据以匹配数组大小
    metadata.update({
        'width': array.shape[1],
        'height': array.shape[0],
        'dtype': 'float32',
        'nodata': nodata_value,
        'transform': transform,
        'crs': crs
    })

    # 将 NaN 替换为 NoData 值
    array = np.where(np.isnan(array), nodata_value, array)

    # 保存为新的 TIFF 文件
    with rasterio.open(output_path, 'w', **metadata) as dst:
        dst.write(array.astype(np.float32), 1)

    print(f"successfully save as TIFF file in: {output_path}")


def visualize_mars_terrain(image_data: np.ndarray, range: tuple,nodata_value: float = -3.4028227e+38) -> None:
    """
    改进的火星地形二维数组可视化，正确处理无效数据为透明，并优化颜色映射范围。
    get visualization of 2D arrays of Mars terrain,

    Parameters:
    - image_data (np.ndarray): 2d array represent the tif file
    -range (tuple) : tuple , get from find_min_max_in_polygon
    - nodata_value (float): default is -3.4028227e+38 the invalid data value in array

    """
    # 处理无效数据，将其设置为掩膜 (透明)
    masked_array = np.ma.masked_equal(image_data, nodata_value)

    # 计算有效数据的最小值和最大值，避免极端无效值干扰颜色映射
    valid_data = image_data[image_data != nodata_value]

    # 可视化
    plt.figure(figsize=(10, 8))
    (vmin,vamx)=range

    #[important]the vmin and vmax is get from find_min_max_in_polygon
    img = plt.imshow(masked_array, cmap='terrain', vmin=vmin, vmax= vamx,aspect='auto')

    # add color bar
    plt.colorbar(img, label='Elevation/Depth')

    plt.title("Fixed Mars Terrain Visualization")
    plt.xlabel("X (Pixels)")
    plt.ylabel("Y (Pixels)")

    plt.show()


def display_image_with_matplotlib(image_path: str, title: str = "Image Display") -> None:
    """
    读取并在 matplotlib 中显示 JPG 图片。

    参数：
    - image_path (str): JPG 图片的文件路径。
    - title (str): 显示图片的标题 (默认: "Image Display")。
    Read and display a JPG image in matplotlib.

    Parameters:
    - image_path (str): File path to the JPG image.
    - title (str): Title of the displayed image (default: "Image Display").
    """
    image = Image.open(image_path)
    plt.figure(figsize=(8, 6))
    plt.imshow(image)
    plt.axis('off')
    plt.title(title)
    plt.show()


def map_jpg_to_tif_coordinates(jpg_image_path: str, tif_file_path: str,
                               jpg_x: float, jpg_y: float) -> tuple:
    """
    将 JPG 图片中的 matplotlib 坐标转换为原始 TIFF 文件中的坐标。

    参数：
    - jpg_image_path (str): JPG 图片文件路径。
    - tif_file_path (str): TIFF 文件路径。
    - jpg_x (float): 在 JPG 图片中的 X 坐标 (matplotlib 坐标系)。
    - jpg_y (float): 在 JPG 图片中的 Y 坐标 (matplotlib 坐标系)。

    返回：
    - (tif_x, tif_y) (tuple): 在 TIFF 文件中的坐标 (matplotlib 坐标系)。
    Convert matplotlib coordinates in a JPG image to coordinates in the original TIFF file.

    Parameters:
    - jpg_image_path (str): JPG image file path.
    - tif_file_path (str): TIFF file path.
    - jpg_x (float): X coordinate in the JPG image (matplotlib coordinate system).
    - jpg_y (float): Y coordinate in the JPG image (matplotlib coordinate system).

    Returns:
    - (tif_x, tif_y) (tuple): Coordinates in the TIFF file (matplotlib coordinate system).
    """
    # 读取 JPG 图片尺寸
    #Read JPG image size
    with Image.open(jpg_image_path) as img:
        jpg_width, jpg_height = img.size

    # 读取 TIFF 文件尺寸和仿射变换
    # Read TIFF file size and affine transformation
    with rasterio.open(tif_file_path) as src:
        tif_width, tif_height = src.width, src.height
        transform = src.transform

    # 计算坐标比例
    #Calculate coordinate scale
    scale_x = tif_width / jpg_width
    scale_y = tif_height / jpg_height

    # 计算在 TIFF 坐标系中的像素坐标
    #Calculate pixel coordinates in TIFF coordinate system
    tif_x = int(round(jpg_x * scale_x))
    tif_y = int(round(jpg_y * scale_y))

    print(f"JPG coordinate: ({jpg_x}, {jpg_y}) => TIFF coordinate: ({tif_x:.2f}, {tif_y:.2f})")

    return tif_x, tif_y


def crop_jpg_image(image_path: str, output_path: str, top_left: tuple, bottom_right: tuple) -> None:
    """
    根据输入的左上角和右下角坐标，裁剪 JPG 图片并保存为新的文件。

    参数：
    - image_path (str): 原始 JPG 图片文件路径。
    - output_path (str): 裁剪后的图片保存路径。
    - top_left (tuple): 左上角坐标 (x, y)。
    - bottom_right (tuple): 右下角坐标 (x, y)。
    Crop the JPG image and save it as a new file according to the input upper left and lower right corner coordinates.

    Parameters:
    - image_path (str): original JPG image file path.
    - output_path (str): cropped image save path.
    - top_left (tuple): upper left corner coordinates (x, y).
    - bottom_right (tuple): lower right corner coordinates (x, y).
    """

    image = Image.open(image_path)
    x_min, y_min = map(int, top_left)
    x_max, y_max = map(int, bottom_right)
    cropped_image = image.crop((x_min, y_min, x_max, y_max))
    cropped_image.save(output_path, format='JPEG')
    print(f"saved crop jpg file as: {output_path}")


def visualize_full_tif(image_data: np.ndarray, nodata_value: float = -3.4028227e+38) -> None:
    """
    可视化整个 TIFF 文件，正确处理无效数据为透明区域。

    参数：
    - image_data (np.ndarray): TIFF 文件中的二维数组。
    - nodata_value (float): 无效数据的填充值 (默认: -3.4028227e+38)。
    Visualize the entire TIFF file, correctly handling invalid data as transparent areas.

    Parameters:
    - image_data (np.ndarray): 2D array from the TIFF file.
    - nodata_value (float): fill value for invalid data (default: -3.4028227e+38).
    """
    # 将无效数据设置为掩膜
    # 创建有效数据的掩膜
    # Set invalid data as mask
    # Create a mask for valid data
    valid_mask = image_data != nodata_value

    # 计算有效数据的边界框
    #calculate the vaild data's boundary
    rows, cols = np.where(valid_mask)
    min_row, max_row = rows.min(), rows.max()
    min_col, max_col = cols.min(), cols.max()

    # 自动裁剪有效数据区域
    #crop data under valid area
    cropped_array = image_data[min_row:max_row + 1, min_col:max_col + 1]
    masked_array = np.ma.masked_equal(cropped_array, nodata_value)

    # 可视化裁剪后的有效区域
    #visualez valid area
    plt.figure(figsize=(10, 8))
    plt.imshow(masked_array, cmap='terrain', vmin=-4932.626953125, vmax= -4548.0 )
    plt.colorbar(label='Elevation/Depth')
    plt.title('Auto-Cropped Mars Terrain Visualization')
    plt.xlabel('X (Pixels)')
    plt.ylabel('Y (Pixels)')
    plt.show()

def find_min_max_in_polygon(tif_path: str,
                            nodata_value: float = -3.4028227e+38,
                            min_threshold: float = -6000) -> tuple:
    """
    遍历火星地形 TIFF 文件中由四个点 (a, b, c , d) 围成的不规则四边形区域，
    重要提醒：(a, b, c , d) 的默认值是劳斯陨石坑冰丘tif文件的4个边界点，换用不同的图时候,需要在函数内部修改a,b,c,d的值
    返回有效高度值的最大值和最小值，忽略无效数据值
    在寻找最小值时，跳过小于 min_threshold 的数据 (默认: -6000)
    a, b, c ,d在图中的排列方式如下图
    a------b
    ｜     ｜
    c------d

    参数：
    - tif_path (str): TIFF 文件路径
    - nodata_value (float): 无效数据的填充值 (默认: -3.4028227e+38)
    - min_threshold (float): 最小值的下限，低于此值的数据不计入最小值计算 (默认: -6000)

    返回：
    - (min_value, max_value) (tuple): 多边形区域内的最小值和最大值 (排除无效值和小于 min_threshold 的值)
    Traverse the irregular quadrilateral area surrounded by four points (a, b, c, d) in the Mars terrain TIFF file.
    Important reminder: The default value of (a, b, c, d) is the 4 boundary points of the Rous crater ice hill tif file. When using different images, you need to modify the values
    of a, b, c, d in the function
    Return the maximum and minimum values of valid height values, ignoring invalid data values
    When looking for the minimum value, skip data less than min_threshold (default: -6000)
    The arrangement of a, b, c, d in the figure is as follows
    a------b
    ｜     ｜
    c------d

    Parameters:
    - tif_path (str): TIFF file path
    - nodata_value (float): Fill value for invalid data (default: -3.4028227e+38)
    - min_threshold (float): The lower limit of the minimum value.
    Data below this value is not included in the minimum value calculation (default: -6000)

    Return:
    - (min_value, max_value) (tuple): minimum and maximum values
    within the polygon area (excluding invalid values and values less than min_threshold)


     !!!![待改进问题]!!!!
     最小高度-6000是人为尝试之后得出来的，不然的话得出来的最小值会无限接近于invalid data-3.4028227e+38

     !!![函数适用范围]!!!
     输入不同的地形数据文件得到的最大值和最小值各不相同
     。例如Louth Crater ice mound（劳斯陨石坑冰丘）的最大值=-4932.626953125, 最小值= -4548.0
    """

    # 四个点的 (x, y) 坐标 (注意坐标系方向：左上为原点)
    a = (130, 3516)
    b = (21000, 8497)
    c = (8570, 97)
    d = (10530, 5034)

    # 定义多边形 (不规则四边形) 的顶点
    polygon = np.array([a, b, d, c])

    # 创建多边形路径 (用于判断点是否在多边形内)
    poly_path = Path(polygon)

    with rasterio.open(tif_path) as src:
        # 读取整个 TIFF 文件中的第一波段数据
        image_data = src.read(1)
        height, width = image_data.shape

    # 计算多边形的最小外接矩形的边界
    min_x = max(min(polygon[:, 0]), 0)
    max_x = min(max(polygon[:, 0]), width - 1)
    min_y = max(min(polygon[:, 1]), 0)
    max_y = min(max(polygon[:, 1]), height - 1)

    print(f"Coordinates of the traversed rectangular area: X range [{min_x}, {max_x}], Y range [{min_y}, {max_y}]")

    # 遍历多边形内的所有像素点
    valid_values = []

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if poly_path.contains_point((x, y)):
                value = image_data[y, x]
                # 忽略无效数据和小于 min_threshold 的值
                if value != nodata_value and (value >= min_threshold or value > -6000):
                    valid_values.append(value)

    # 计算有效数据的最大值和最小值
    if not valid_values:
        print("no valid in roi area")
        return None, None

    min_value = np.min(valid_values)
    max_value = np.max(valid_values)

    print(f"The minimum value of valid data within the polygon area (Exclude less than {min_threshold} ): {min_value}")
    print(f"The maximum value of valid data in the polygon area: {max_value}")

    return min_value, max_value


def calculate_square_Length(tif_path: str, roi: tuple) -> tuple:
    """
        计算由两个点 (A, B) 作为对角线端点构成的正方形的边长。

        参数：
        - tif_path (str): TIFF 文件路径。
        - roi (tuple): (Ax, Ay, Bx, By) 两个点的坐标 (A, B)，构成正方形的对角线。

        返回：
        - (length, length): 正方形的边长 (像素单位)。

        抛出:
        - ValueError: 如果 ROI 坐标超出 TIFF 文件边界。

        Compute the length of the side of a square formed by two points (A, B) as diagonal endpoints.

        Parameters:
        - tif_path (str): TIFF file path.
        - roi (tuple): (Ax, Ay, Bx, By) Coordinates of two points (A, B) forming the diagonal of the square.

        Returns:
        - (length, length): Length of the side of the square in pixels.

        Throws:
        - ValueError: if ROI coordinates are outside the TIFF file boundaries.
        """


    Ax, Ay, Bx, By = roi

    with rasterio.open(tif_path) as src:
        height, width = src.height, src.width

    #print(f"TIFF size: length = {width}, length = {height}")

    # 检查 ROI 是否在 TIFF 文件的边界内
    #check if 2 points in the boundaty
    if not (0 <= Ax < width and 0 <= Bx < width and 0 <= Ay < height and 0 <= By < height):
        raise ValueError(f"coordinates access boundary: A({Ax}, {Ay}), B({Bx}, {By})")

    # 计算对角线长度
    #calculate the diagonal length
    diagonal_length = np.sqrt((Bx - Ax) ** 2 + (By - Ay) ** 2)

    # 计算正方形的边长
    #calculate the length of square
    length = int(diagonal_length / np.sqrt(2))

    #print(f"length of square: {length:.2f} pixel")

    return (length, length)


# 运行函数
def main():
    pass


if __name__=="_main_":
    main()