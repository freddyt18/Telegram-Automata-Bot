import utilities.database as db
import utilities.table_name_const as tbl
import utilities.FiniteAutomaton as fa
import os
from dotenv import load_dotenv

load_dotenv()


#--------------------------------------------------------------------------------------
class UserMachineStrModel:
    def __init__(self, machine_hash, string, str_type) -> None:
        self.machine_hash = machine_hash
        self.string = string
        self.string_type = str_type
        
    
    # for inserting
    def to_tuple(self):
        return tuple((
            self.machine_hash, 
            self.string, 
            self.string_type))
#--------------------------------------------------------------------------------------



mocking_data = []
#--------------------------------------------------------------------------------------------------------
class UserMachineStrService:
    def __init__(self) -> None:
        self.my_db = db.DatabaseConnection(
            os.getenv("DATABASE_HOST"),
            os.getenv("DATABASE_USER"),
            os.getenv("DATABASE_PASS"),
            os.getenv("DATABASE_NAME"),
        )
        
    
    def select_all(self):
        conn = self.my_db.connect_to_database()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {tbl.USER_MACHINE_STRING}")
        
        # convert the mocking data to a dictionary
        # ease the process of updating
        new_dict = {}
        for row in cursor.fetchall():
            string: str = row[2]
            hash: str = row[1]
            str_type: int = row[3]
            
            strings = string.split(',')
            for i in range(len(strings)):
                strings[i] = strings[i].strip()
            
            if (not new_dict.get(hash)):
                new_dict[hash] = {}
            
            new_dict[hash][str_type] = strings
            
        # print(f"new dict: {new_dict}")
        return new_dict
    
    
    def add_new_string_to_database(self, user_ma_str_model: UserMachineStrModel):
        print(f"--> Adding {user_ma_str_model.machine_hash}, {user_ma_str_model.string}, {user_ma_str_model.string_type}")
        
        hash = user_ma_str_model.machine_hash
        string = user_ma_str_model.string
        string_type = user_ma_str_model.string_type
        
        
        user_ma_str_dict = self.select_all()
        
        # the hash exists
        if (user_ma_str_dict.get(hash)):
            # the machine with the hash used to accept/reject
            if (user_ma_str_dict[hash].get(string_type)):
                
                self.__update(hash, string_type, string)
                
                                
            # the machine with the hash did not use to accept/reject
            else:
                #insert new record
                self.__insert(user_ma_str_model)
        # the hash does not exist
        else:
            
            # insert new record
            # insert new data into the mocking data
            self.__insert(user_ma_str_model)
            
        print(f"--> mocking data {mocking_data}")
            
        
    def __insert(self, user_ma_str_model: UserMachineStrModel):
        conn = self.my_db.connect_to_database()
        cursor = conn.cursor()
        # print(f"inserting data: {user_ma_str_model.to_tuple()}")
        cursor.execute(f"INSERT INTO {tbl.USER_MACHINE_STRING} (machineHash, string, is_accepted) VALUES {user_ma_str_model.to_tuple()}")
        conn.commit()
        
        mocking_data.append(user_ma_str_model.to_tuple())
        
    def __update(self, hash, string_type, new_string):
        # let's just update the mocking data
        conn = self.my_db.connect_to_database()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {tbl.USER_MACHINE_STRING}")
        tmp_str = ''
        tmp_str_list = []
        
        # update statement
        d = tuple()
        for d in cursor.fetchall():
            if (d[1] == hash and d[3] == string_type):
                tmp_str_list = d[2].split(',')
                tmp_str_list.append(new_string)
                for s in tmp_str_list:
                    tmp_str += f"{s}"
                    if (tmp_str_list.index(s) < len(tmp_str_list) - 1):
                        tmp_str += ","
                break
        
        print(f"--> new str: {tmp_str}")
        cursor.execute(f"UPDATE {tbl.USER_MACHINE_STRING} SET string = '{tmp_str}' WHERE machineHash = '{hash}' AND is_accepted = {string_type}")
        conn.commit()
        
        return
#--------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------
class UserMachineStrController:
    def __init__(self) -> None:
        self.__user_ma_str_dict = dict() # store the user_machine_str data
        self.get_all()
        print(f"fetched: {self.get_user_ma_str_dict()}")
    
    def get_all(self):
        self.__user_ma_str_dict = UserMachineStrService().select_all()
        
    def get_user_ma_str_dict(self):
        return self.__user_ma_str_dict
        
    def get_acceptance_type(self, machine: fa.FiniteAutomaton, string) -> int:
        machine_hash = machine.hash_of_machine()
        print(machine_hash)
        data = self.get_user_ma_str_dict()
        # print(f"data: {data}")
        
        if (data.get(machine_hash)):
            if (data[machine_hash].get(0) and data[machine_hash][0].count(string)):
                return 0
            elif (data[machine_hash].get(1) and data[machine_hash][1].count(string)):
                return 1
            else:
                return -1
        else:
            return -1
        
    def add_new(self, user_ma_str_model: UserMachineStrModel):
        UserMachineStrService().add_new_string_to_database(user_ma_str_model)
#--------------------------------------------------------------------------------------------------------

