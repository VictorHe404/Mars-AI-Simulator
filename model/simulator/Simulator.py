import MapManager


class Simulator:

    def __init__(self):
        """
        Initialize the Simulator class.

        field:
        target_map(np.ndarray): represent a Mars terrain data , the data will be used in current task
        which assigned to the current simulator
        target_avatar(Avatar) : an Avatar object assigned to the current simulator
        brain_list(Str[]) : a Brain's name list
        represent the available brain list the avatar can use
        avatar_manager(AvatarManager): an AvatarManager object asssigned to the current
        simulator, to manage the motion of the avatar
        target_brain (Brain) : a Brain object, which is currently used by the avatar.
        target_environment (Environment): an Environment object , represent the current
        environment applied to the avatar
        target_task (Task): a Task object,which represent
        map_manager: MapManager : a MapManger object assigned to manage the map
        result_trail: Log[] : a log list to record the information of path detected by avatar on map
        map_minValue:float
        map_maxValue:float
        """
        self.target_map=None
        self.target_avatar=None
        self.brain_list=None
        self.avatar_manager=None
        self.target_environment=None
        self.target_task=None
        self.map_manager=MapManager.MapManager()
        self.result_trail=None
        self.map_minValue=0.0
        self.map_maxValue=99999.0


    #def set_avatar(self,name):
        """
        set the tager avatar's name
        Parameters:
        name(string): represent the map’s name in the map_names
        Returns:
        the 2d array in the map_list
        """


    def set_map(self, name:str):
        """
        set the target_map to the user wanted
        update map_minValue , map_maxValue with respect to the target_map
        Parameters:
        name(string): represent the map’s name in the map_names
        """
        (self.target_map,self.map_minValue,self.map_maxValue)=self.map_manager.get_mapByName(name)






