#new import statements
import rasterio
from rasterio.transform import from_origin
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.path import Path



def read_tif_to_array(file_path: str) -> np.ndarray:
    """
    Reads a TIFF file and returns a 2D float array
    """
    with rasterio.open(file_path) as src:
        array = src.read(1).astype(np.float32)
        return array

def downsample_min_max(elevation_map, factor=10):
    rows, cols = elevation_map.shape
    new_rows, new_cols = rows // factor, cols // factor

    elevation_map = elevation_map[:new_rows * factor, :new_cols * factor]
    min_map = elevation_map.reshape(new_rows, factor, new_cols, factor).min(axis=(1, 3))
    max_map = elevation_map.reshape(new_rows, factor, new_cols, factor).max(axis=(1, 3))

    return min_map, max_map


def adaptive_downsample(elevation_map, factor=10):
    rows, cols = elevation_map.shape
    new_rows, new_cols = rows // factor, cols // factor

    global_avg = np.mean(elevation_map)

    elevation_map = elevation_map[:new_rows * factor, :new_cols * factor]

    reshaped_map = elevation_map.reshape(new_rows, factor, new_cols, factor)

    local_avg = reshaped_map.mean(axis=(1, 3))

    local_max = reshaped_map.max(axis=(1, 3))
    local_min = reshaped_map.min(axis=(1, 3))

    downsampled_map = np.where(local_avg > global_avg, local_max, local_min)

    return downsampled_map


def average_downsample(input_array, factor=10):
    rows, cols = input_array.shape
    new_rows, new_cols = rows // factor, cols // factor

    input_array = input_array[:new_rows * factor, :new_cols * factor]

    reshaped_array = input_array.reshape(new_rows, factor, new_cols, factor)

    cropped_array = reshaped_array.mean(axis=(1, 3))  # Average pooling to downscale

    return cropped_array



def visualize_mars_terrain_without_range(image_data: np.ndarray, nodata_value: float = -3.4028227e+38) -> None:
    masked_array = np.ma.masked_equal(image_data, nodata_value)

    valid_data = image_data[image_data != nodata_value]
    vmin, vmax = valid_data.min(), valid_data.max()

    plt.figure(figsize=(10, 8))
    img = plt.imshow(masked_array, cmap='terrain', vmin=vmin, vmax=vmax, aspect='auto')

    plt.colorbar(img, label='Elevation/Depth')

    plt.title("Mars Terrain Visualization")
    plt.xlabel("X (Pixels)")
    plt.ylabel("Y (Pixels)")

    plt.show()



def crop_and_resize_tif(tif_path: str, roi: tuple, output_size=(100, 100)) -> np.ndarray:
    """
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
        # Array slicing operation, cut the part of the array we need
        cropped_array = full_array[ymin:ymax, xmin:xmax]

        #original area size
        original_height, original_width = cropped_array.shape

        # When the desired cropped map size (output_size) is greater than or equal to the original
        # cropped area size, return directly to the original cropped area
        if calculate_square_Length(tif_path, roi)==output_size or calculate_square_Length(tif_path, roi)[0] < output_size[0]:
            return cropped_array

        # Calculate the scaling ratio (block size of mean pooling)
        # When shrinking from the original size to outputsize,
        # each block_size_x*block_size_y area will be shrunk to one pixel,
        # Take the average of block_size_x*block_size_y and assign it to the final shrunk pixel
        block_size_y = original_height // output_size[0]
        block_size_x = original_width // output_size[1]

        small_array = cropped_array[:block_size_y * output_size[0], :block_size_x * output_size[1]]
        small_array = small_array.reshape(output_size[0], block_size_y, output_size[1], block_size_x)
        resized_array = small_array.mean(axis=(1, 3))
        return resized_array


def save_array_to_tif(array: np.ndarray, output_path: str,reference_tif_path: str = None,
                      nodata_value: float = -3.4028227e+38) -> None:
    """
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
            'crs': None,  
            'transform': from_origin(0, 0, 1, 1) 
        }
        transform = metadata['transform']
        crs = metadata['crs']

    metadata.update({
        'width': array.shape[1],
        'height': array.shape[0],
        'dtype': 'float32',
        'nodata': nodata_value,
        'transform': transform,
        'crs': crs
    })


    array = np.where(np.isnan(array), nodata_value, array)


    with rasterio.open(output_path, 'w', **metadata) as dst:
        dst.write(array.astype(np.float32), 1)

    print(f"successfully save as TIFF file in: {output_path}")


def visualize_mars_terrain(image_data: np.ndarray, range: tuple,nodata_value: float = -3.4028227e+38) -> None:
    """
    get visualization of 2D arrays of Mars terrain,

    Parameters:
    - image_data (np.ndarray): 2d array represent the tif file
    -range (tuple) : tuple , get from find_min_max_in_polygon
    - nodata_value (float): default is -3.4028227e+38 the invalid data value in array

    """

    masked_array = np.ma.masked_equal(image_data, nodata_value)
    valid_data = image_data[image_data != nodata_value]

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
    Parameters:
    - jpg_image_path (str): JPG image file path.
    - tif_file_path (str): TIFF file path.
    - jpg_x (float): X coordinate in the JPG image (matplotlib coordinate system).
    - jpg_y (float): Y coordinate in the JPG image (matplotlib coordinate system).

    Returns:
    - (tif_x, tif_y) (tuple): Coordinates in the TIFF file (matplotlib coordinate system).
    """
   
    #Read JPG image size
    with Image.open(jpg_image_path) as img:
        jpg_width, jpg_height = img.size


    # Read TIFF file size and affine transformation
    with rasterio.open(tif_file_path) as src:
        tif_width, tif_height = src.width, src.height
        transform = src.transform


    #Calculate coordinate scale
    scale_x = tif_width / jpg_width
    scale_y = tif_height / jpg_height

    #Calculate pixel coordinates in TIFF coordinate system
    tif_x = int(round(jpg_x * scale_x))
    tif_y = int(round(jpg_y * scale_y))

    print(f"JPG coordinate: ({jpg_x}, {jpg_y}) => TIFF coordinate: ({tif_x:.2f}, {tif_y:.2f})")

    return tif_x, tif_y


def crop_jpg_image(image_path: str, output_path: str, top_left: tuple, bottom_right: tuple) -> None:
    """
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
    Parameters:
    - image_data (np.ndarray): 2D array from the TIFF file.
    - nodata_value (float): fill value for invalid data (default: -3.4028227e+38).
    """

    # Set invalid data as mask
    # Create a mask for valid data
    valid_mask = image_data != nodata_value


    #calculate the vaild data's boundary
    rows, cols = np.where(valid_mask)
    min_row, max_row = rows.min(), rows.max()
    min_col, max_col = cols.min(), cols.max()

    #crop data under valid area
    cropped_array = image_data[min_row:max_row + 1, min_col:max_col + 1]
    masked_array = np.ma.masked_equal(cropped_array, nodata_value)

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


    """

    a = (130, 3516)
    b = (21000, 8497)
    c = (8570, 97)
    d = (10530, 5034)
    polygon = np.array([a, b, d, c])

 
    poly_path = Path(polygon)

    with rasterio.open(tif_path) as src:
        
        image_data = src.read(1)
        height, width = image_data.shape

    min_x = max(min(polygon[:, 0]), 0)
    max_x = min(max(polygon[:, 0]), width - 1)
    min_y = max(min(polygon[:, 1]), 0)
    max_y = min(max(polygon[:, 1]), height - 1)

    print(f"Coordinates of the traversed rectangular area: X range [{min_x}, {max_x}], Y range [{min_y}, {max_y}]")


    valid_values = []

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if poly_path.contains_point((x, y)):
                value = image_data[y, x]
               
                if value != nodata_value and (value >= min_threshold or value > -6000):
                    valid_values.append(value)


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

   
    #check if 2 points in the boundaty
    if not (0 <= Ax < width and 0 <= Bx < width and 0 <= Ay < height and 0 <= By < height):
        raise ValueError(f"coordinates access boundary: A({Ax}, {Ay}), B({Bx}, {By})")

   
    #calculate the diagonal length
    diagonal_length = np.sqrt((Bx - Ax) ** 2 + (By - Ay) ** 2)


    #calculate the length of square
    length = int(diagonal_length / np.sqrt(2))

    #print(f"length of square: {length:.2f} pixel")

    return (length, length)



def main():
    pass


if __name__=="_main_":
    main()
