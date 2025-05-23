import os
#from typing import List
import numpy as np
import rasterio




class MapManager:
    def __init__(self):
        """
        Initialize the MapManager class. map data store in cloud
        Parameters:
        map_names(string[]): an attribute to store a string list, contain names of different maps
        1 is default value, represent the Louth_Crater_Normal.tif
        map_path (str) : store the document's path , the document contains all the map files under this document
        """
        self.map_names=["Louth_Crater_Normal", "Louth_Crater_Sharp", "Eolian_Normal", "Dune_Normal"]
        base_dir = os.path.dirname(os.path.abspath(__file__))  # get abs path of `MapManager.py`
        project_repo_dir = os.path.abspath(os.path.join(base_dir, "../../"))  # move 2 level of directory to the repo directory
        self.map_path = os.path.join(project_repo_dir, "MapImage/")  # combie the above path with `MapImage/`

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
            return (np.empty((0,0)),-10000,-10000)

        map_array=self.read_tif_to_array(file_path)
        max_value = np.max(map_array)
        min_value = np.min(map_array)
        return (map_array,min_value,max_value)


    def get_map_names(self):
        return self.map_names








