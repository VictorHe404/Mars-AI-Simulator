import tifreader
from MapImage.tifreader import visualize_mars_terrain_without_range


def print_map(map_array):

    for row in map_array:
        print(" ".join(str(cell) for cell in row))


def analyze_slopes(elevation_map):
    rows = len(elevation_map)
    cols = len(elevation_map[0]) if rows > 0 else 0

    max_slope = float('-inf')
    min_slope = float('inf')

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for i in range(rows):
        for j in range(cols):
            current_elevation = elevation_map[i][j]

            for di, dj in directions:
                ni, nj = i + di, j + dj

                if 0 <= ni < rows and 0 <= nj < cols:
                    neighbor_elevation = elevation_map[ni][nj]
                    slope = abs(current_elevation - neighbor_elevation)

                    max_slope = max(max_slope, slope)
                    min_slope = min(min_slope, slope)

    return max_slope, min_slope

def show_map_size(map_array):

    rows, cols = map_array.shape
    print(f"Map size: {rows} x {cols}")


if __name__ == "__main__":

    map = tifreader.read_tif_to_array("1000x1000Louth_Crater_ice_mound_subPart.tif")
    visualize_mars_terrain_without_range(map)
    show_map_size(map)
    cropped_map = tifreader.average_downsample(map)
    cropped_map_2 = tifreader.adaptive_downsample(map)
    visualize_mars_terrain_without_range(cropped_map)
    visualize_mars_terrain_without_range(cropped_map_2)
    #print_map(cropped_map)
    max_slope, min_slope = analyze_slopes(cropped_map_2)
    print(f"Biggest slope: {max_slope}")
    print(f"Smallest slope: {min_slope}")
    tifreader.save_array_to_tif(cropped_map_2, "100x100Louth_Crater_ice_mound_subPart_sharp.tif")
