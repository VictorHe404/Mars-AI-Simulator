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
        self.target_brain=None
        self.target_environment=None
        self.target_task=None
        self.map_manager=MapManager.MapManager()
        self.result_trail=None
        self.map_minValue=0.0
        self.map_maxValue=99999.0


    #def set_avatar(self,name):
        """
        set the tager_avatar with a Avatar object
        Parameters:
        name(string): represent the Avatar object’s name
        """

    #def set_brain(self,name:str):
    """
    set the target_brain with a Avatar object
    Parameters:
    name(string): represent the Brain object’s name
    """

    # def get_Avatarnames(self):
    # return the avatar_names from AvatarManager class

    # add_avatar(String name): Boolean


    def set_map(self, name:str):
        """
        set the target_map to the user wanted
        update map_minValue , map_maxValue with respect to the target_map
        Parameters:
        name(string): represent the map’s name in the map_names
        """
        (self.target_map,self.map_minValue,self.map_maxValue)=self.map_manager.get_mapByName(name)

    def set_task(self,s_row,s_col,d_row, d_col) :
        """
        set the target_task's related 4 fields
        Parameters:
        s_row(int) :start_row
        s_col(int) :start_col
        d_row(int) :des_row
        d_col(int) :des_col
        """
        self.target_task.start_row=s_row
        self.target_task.start_col=s_col
        self.target_task.des_row=d_row
        self.target_task.des_col=d_col

    def get_brainnames(self):
        """

        :return: brain_list(Str[]) : a Brain's name list
        """
        return self.brain_list

#test code block:
#simulator=Simulator()
#simulator.set_map("100x100Louth_Crater_ice_mound_subPart")
#print(simulator.target_map)
#print(simulator.map_maxValue)
#print(simulator.map_minValue)





