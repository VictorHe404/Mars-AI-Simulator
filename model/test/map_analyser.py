from model.simulator import Simulator, Task, MapManager, Environment

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


if __name__ == "__main__":

    simulator = Simulator()
    simulator.set_map("100x100Louth_Crater_ice_mound_subPart")
    map = simulator.target_map
    #print_map(map)

    max_slope, min_slope = analyze_slopes(map)
    print(f"Biggest slope: {max_slope}")
    print(f"Smallest slope: {min_slope}")

