from typing import List
import numpy as np

class MapManager:
    def __init__(self, map_names:List[str],map_list:List[np.ndarray]):
        """
        Initialize the MapManager class. map data store in cloud
        Parameters:
        map_names(string[]): an attribute to store a string list, contain names of different maps .
        map_list(np.ndarray[]): a 2-d array list , each 2d array list represent a Mars terrain data
        """

        if not isinstance(map_names, list) or not all(isinstance(name, str) for name in map_names):
            raise TypeError("map_names must be string list")

        if not isinstance(map_list, list) or not all(isinstance(arr, np.ndarray) and arr.ndim == 2 for arr in map_list):
            raise TypeError("map_list must be 2d array list")

        if len(map_names) != len(map_list):
            raise ValueError("the length of map_list and map_names is not equal")

        self.map_names=map_names
        self.map_list=map_list

    def get_map(self,nameOrIndex)-> np.ndarray:
        """
        return the map the user want
        Parameters:
        nameOrIndex(int or string): represent the index or the map’s name in the map_list
        Returns:
        the 2d array in the map_list
        """
        try:
            # get map by index
            if isinstance(nameOrIndex, int):
                if nameOrIndex< 0 or nameOrIndex >= len(self.map_names):
                    raise IndexError(f"index out of order")

                return self.map_list[nameOrIndex]

            # get map by map's name
            elif isinstance(nameOrIndex, str):
                if nameOrIndex not in self.map_names:
                    raise KeyError(f"map'{nameOrIndex}' not exist")
                index=self.map_names.index(nameOrIndex)
                return self.map_list[index]

            else:
                raise TypeError("nameOrIndex must be int (index) or str (name of map)")

        except (IndexError, KeyError, TypeError) as e:
            print(f"Exception: {e}")
            return None  # catch the exception,return None


"""
#test code block
#测试代码：
names = ["Mars_Region1", "Mars_Region2"]
maps = [np.random.rand(100, 100), np.random.rand(200, 200)]
manager = MapManager(names, maps)

print(" 正确查询 (按名称)")
print(manager.get_map("Mars_Region1"))  # 获取 "Mars_Region1" 的地图

print("\n 正确查询 (按索引)")
print(manager.get_map(1))  # 获取索引 1 的地图

print("\n 测试错误 (无效索引)")
print(manager.get_map(5))  # 超出范围

print("\n 测试错误 (不存在的名称)")
print(manager.get_map("Unknown_Region"))  # 不存在的地图名称

print("\n 测试错误 (错误类型)")
print(manager.get_map(3.5))  # 错误的类型

"""




