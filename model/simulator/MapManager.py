import os
#from typing import List
import numpy as np
import rasterio




class MapManager:
    def find_project_repo(self):
        """
        注意：这里的project_repo,是指在费争扬本地电脑中用于储存361代码repo的文件夹名
        当把代码pull到本地中，若要使用MapManager的__init__函数，请自行修改此函数中
        "if os.path.basename(current_dir) == "project_repo" 中的project_repo为你本地电脑中用于
        储存361代码repo的文件夹名
        from current execute file，Recursively search upwards for the `project_repo`
        directory and return its absolute path.
        """
        current_dir = os.path.abspath(__file__)  # 获取当前文件的绝对路径
        while current_dir != os.path.dirname(current_dir):

            if os.path.basename(current_dir) == "project_repo": #！！！！修改处！！！！
                return current_dir
            current_dir = os.path.dirname(current_dir)  # 向上一级目录移动
        raise FileNotFoundError("未找到 `project_repo` 目录，请确保代码位于正确的项目结构内！"
                                "或按照注释要求修改find_project_repo函数中对应行的代码")

    def __init__(self):
        """
        Initialize the MapManager class. map data store in cloud
        Parameters:
        map_names(string[]): an attribute to store a string list, contain names of different maps
        1 is default value, represent the 100x100Louth_Crater_ice_mound_subPart.tif
        map_path (str) : store the document's path , the document contains all the map files under this document
        """
        self.map_names=["100x100Louth_Crater_ice_mound_subPart"]
        project_repo_dir = self.find_project_repo()  # 获取 `project_repo/` 目录
        self.map_path = os.path.join(project_repo_dir, "MapImage/")  # 拼接 `MapImage/`

        #"/Users/zhengyangfei/mcgill/E_disk/COMP/comp361/project/project_repo/MapImage/"


    def read_tif_to_array(self,file_path: str):
        """
        读取 TIFF 文件并返回一个二维 float 数组
        Reads a TIFF file and returns a 2D float array
        """
        with rasterio.open(file_path) as src:
            array = src.read(1).astype(np.float32)
            return array

    def get_mapByName(self,name)-> tuple:
        """
        return the map the user want
        Parameters:
        name(string): represent the map’s name in the map_names
        Returns:
        a tuple （map 2d array,min,max）min and max represent the min and max value in the 2d array.
        """
        file_path=os.path.join(self.map_path, name + ".tif")
        #self.map_path+name+".tif"
        if (name not in self.map_names) :
            print("the map you want is not in the map_names")
            return (np.empty(),0,0)

        map_array=self.read_tif_to_array(file_path)
        max_value = np.max(map_array)
        min_value = np.min(map_array)
        return (map_array,min_value,max_value)








