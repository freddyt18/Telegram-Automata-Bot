import pprint
import mysql.connector
import utilities.FiniteAutomaton as FiniteAutomaton
import html
import hashlib

class DatabaseConnection:
    def __init__(self, host: str, user: str, passwd: str, database: str):
        '''
            • Create a connection to the database.\n
            • Takes in ``host: str``, ``username: str``, ``password: str`` and the ``database: str`` you want to connect.\n
            • Returns an object ``DatabaseConnection``
        '''

        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database

        self.creating_tables()

    def creating_tables(self):
        con = self.connect_to_database()
        cursor = con.cursor()

        usermachine_tbl = """
        CREATE TABLE IF NOT EXISTS UserMachine_Tbl (
            machineID int NOT NULL AUTO_INCREMENT,
            set_of_states text NOT NULL,
            alphabet text NOT NULL,
            delta text NOT NULL,
            start_state varchar(25) NOT NULL,
            set_of_final_states text NOT NULL,
            PRIMARY KEY (machineID)
        ) ENGINE InnoDB,
        CHARSET utf8mb4,
        COLLATE utf8mb4_0900_ai_ci;
        """

        client_tbl = """
            CREATE TABLE IF NOT EXISTS Client_Tbl (
            clientID int NOT NULL AUTO_INCREMENT,
            chatID text NOT NULL,
            machineID int NOT NULL,
            username text NOT NULL,
            PRIMARY KEY (clientID)
        ) ENGINE InnoDB,
        CHARSET utf8mb4,
        COLLATE utf8mb4_0900_ai_ci;
        """

        usermachinedetail_tbl = """
        CREATE TABLE IF NOT EXISTS UserMachineDetail_Tbl (
            machineDetailID int NOT NULL AUTO_INCREMENT,
            machineID int NOT NULL,
            type text,
            machineHash text NOT NULL,
            description longtext,
            PRIMARY KEY (machineDetailID)
        ) ENGINE InnoDB,
        CHARSET utf8mb4,
        COLLATE utf8mb4_0900_ai_ci;
        """

        usermachinestring_tbl = """
        CREATE TABLE IF NOT EXISTS UserMachineString_Tbl (
            stringID int NOT NULL AUTO_INCREMENT,
            machineHash text NOT NULL,
            string text NOT NULL,
            is_accepted tinyint NOT NULL,
            PRIMARY KEY (stringID)
        ) ENGINE InnoDB,
        CHARSET utf8mb4,
        COLLATE utf8mb4_0900_ai_ci;
        """
        

        cursor.execute(usermachine_tbl)
        cursor.execute(client_tbl)
        cursor.execute(usermachinedetail_tbl)
        cursor.execute(usermachinestring_tbl)
        con.commit()
        cursor.close()


    def connect_to_database(self):
        '''Returns a ``connection``'''

        return mysql.connector.connect(
            host = self.host,
            user = self.user,
            passwd = self.passwd,
            db = self.database
        )


    def execute_query(self, query: str, type: str, storage: dict = None):
        '''
            • An automation for executing a query.\n
            • Returns
                ``cusor.fetchall()`` if ``type`` is ``select``\n
                ``cursor.lastrowid`` if ``type`` is ``insert``

            NOTE\n
            • `storage` is `optional`\n
            • If `storage` is given, The function will automatically
            assign each machine to a key to the storage.
        '''
        
        connection = self.connect_to_database()
        cursor = connection.cursor()
        cursor.execute(query)

        if type.lower() == "select":
            if not storage is None:
                for row in cursor:
                    temp = list()

                    states = html.unescape(str(row[1]))
                    alphabet = html.unescape(str(row[2]))
                    delta = html.unescape(str(row[3]))
                    start_state = html.unescape(str(row[4]))
                    final_states = html.unescape(str(row[5]))

                    temp.extend([
                        str(states), 
                        str(alphabet), 
                        str(delta), 
                        str(start_state), 
                        str(final_states)
                    ])

                    storage[row[0]] = temp
                
                result = storage

            else:
                result = cursor.fetchall()

            cursor.close()
            return result
        
        elif type.lower() == "insert":
            connection.commit()
            last_row_id = cursor.lastrowid
            cursor.close()
            
            return last_row_id 
        
        elif type.lower() == "type_select":
            if not storage is None:
                for row in cursor:
                    temp = list()

                    states = html.unescape(str(row[1]))
                    alphabet = html.unescape(str(row[2]))
                    delta = html.unescape(str(row[3]))
                    start_state = html.unescape(str(row[4]))
                    final_states = html.unescape(str(row[5]))
                    type = str(row[6])

                    temp.extend([
                        str(states), 
                        str(alphabet), 
                        str(delta), 
                        str(start_state), 
                        str(final_states),
                        str(type)
                    ])

                    storage[row[0]] = temp
                
                result = storage

            else:
                result = cursor.fetchall()

            cursor.close()
            return result
        
        else:
            connection.commit()
            cursor.close()



    def is_duplicated(self, FA: FiniteAutomaton.FiniteAutomaton):
        '''
            • Check if a specific machine already exists in the database
            by using the `machine's hash` to loop over `UserMachineDetail_Tbl`
            whether there's already a hash.\n
            • Returns
                `True` if there is.\n
                `False` if there isn't.
        '''

        hash_of_machine = FA.hash_of_machine()

        query = f"SELECT * FROM UserMachineDetail_Tbl WHERE machineHash = '{hash_of_machine}';"
        if(self.execute_query(query, "select")):
            return True
        return False



    def assign_user_machine(self, FA: FiniteAutomaton.FiniteAutomaton, chatID: str, username: str, duplicated: bool = False):
        '''
            • Assign a machine to a specific user.\n
            NOTE\n
            • Every value of each attribute of object ``FiniteAutomaton`` will be ``escaped`` using ``html.escape()`` before inserting into the database.\n
            • Make sure to ``unescape`` them before using.\n
            • `duplicated` is `optional`\n
            • If `duplicated` is given, the function will assign the user with a `machineID` that has the same hash as the given FA instead of inputting the machine into the database again.
        '''

        if duplicated:
            #There are two types of duplication:
            #   1. Same chat machine duplication
            #   2. Different chat machine duplication
            #   
            #   In This case, we will check to see if duplicated machine is entered by the same chat.
            #   If the chat is not the same, then we can assign the duplicated machine to the chat 

            try:
                query = f"SELECT umdt.machineID, ct.chatID FROM UserMachineDetail_Tbl umdt INNER JOIN Client_Tbl ct ON ct.machineID = umdt.machineID WHERE umdt.machineHash = '{FA.hash_of_machine()}';"
                result = self.execute_query(query, "select")

                duplicated_machine_id = result[0][0]
                temp_chatID = result

                if temp_chatID is str:
                    if(str(temp_chatID[0][1]) != str(chatID)):
                        query = f"INSERT INTO Client_Tbl(chatID, machineID, username) VALUES ('{chatID}',{int(duplicated_machine_id)},'{username}')"
                        self.execute_query(query, "insert")
                        # print("HIIII")
                    else:
                        return str("Duplicated machine is entered by the same chat.")
                    
                else:
                    for eachID in temp_chatID:
                        if(str(eachID[1]) == str(chatID)):
                            return str("Duplicated machine is entered by the same chat.")

                    query = f"INSERT INTO Client_Tbl(chatID, machineID, username) VALUES ('{chatID}',{int(duplicated_machine_id)},'{username}')"
                    self.execute_query(query, "insert")
                    # pprint.pprint(temp_chatID)

                
            
            except:
                duplicated_machine_id = self.execute_query(f"SELECT machineID FROM UserMachineDetail_Tbl WHERE machineHash = '{FA.hash_of_machine()}';", "select")[0][0]

                query = f"INSERT INTO Client_Tbl(chatID, machineID, username) VALUES ('{chatID}',{int(duplicated_machine_id)},'{username}')"
                self.execute_query(query, "insert")

                # print("or here")
            

        else:
            query = f"INSERT INTO UserMachine_Tbl(set_of_states, alphabet, delta, start_state, set_of_final_states) VALUES ('{html.escape(str(FA.states))}','{html.escape(str(FA.alphabet))}','{html.escape(str(FA.transition_function))}','{html.escape(str(FA.initial_state))}','{html.escape(str(FA.final_states))}');"
            last_row_id_of_machine = self.execute_query(query, "insert")


            query = f"INSERT INTO Client_Tbl(chatID, machineID, username) VALUES ('{chatID}',{int(last_row_id_of_machine)},'{username}');"
            self.execute_query(query, "insert")

            hash = FA.hash_of_machine()
            query = f"INSERT INTO UserMachineDetail_Tbl(machineID, machineHash) VALUES ({int(last_row_id_of_machine)},'{hash}');"
            self.execute_query(query, "insert")


        



    def get_machine_of_user(self, chatID: str, storage: dict, type: str = 'all'):
        '''
            • Get all machine a specific user owns.\n
            • Takes in\n 
                ``chatID`` : ``str``\n
                ``storage`` : ``dict``\n
                ``type``: ``str``\n
            • Returns a ``DICTIONARY``
                ``of FA Machines`` if ``type`` is ``all``\n
                ``of NFA Machines`` if ``type`` is ``nfa``\n
        '''

        temp_storage = dict()
        if type.lower() == 'all':
            temp_storage = self.execute_query(f"SELECT um.machineID, set_of_states, alphabet, delta, start_state, set_of_final_states FROM UserMachine_Tbl um INNER JOIN Client_Tbl cl ON cl.machineID = um.machineID WHERE cl.ChatID = '{str(chatID)}' ORDER BY um.machineID ASC;", "select", temp_storage)
        elif type.lower() == 'nfa':
            temp_storage = self.execute_query(f"SELECT um.machineID, set_of_states, alphabet, delta, start_state, set_of_final_states, umd.type FROM UserMachine_Tbl um INNER JOIN Client_Tbl cl ON cl.machineID = um.machineID INNER JOIN UserMachineDetail_Tbl umd on umd.machineID = um.machineID WHERE cl.ChatID = '{str(chatID)}' AND (umd.type = 'NFA' OR umd.type IS NULL) ORDER BY um.machineID ASC;", "type_select", temp_storage)
        elif type.lower() == 'all_type':
            temp_storage = self.execute_query(f"SELECT um.machineID, set_of_states, alphabet, delta, start_state, set_of_final_states, umd.type FROM UserMachine_Tbl um INNER JOIN Client_Tbl cl ON cl.machineID = um.machineID INNER JOIN UserMachineDetail_Tbl umd on umd.machineID = um.machineID WHERE cl.ChatID = '{str(chatID)}' ORDER BY um.machineID ASC;", "type_select", temp_storage)
    
        if(not temp_storage):
            if type.lower() == 'nfa':
                temp_storage["error"] = "You do not have any NFA Machine. Please use /design to create a new machine."
            else:
                temp_storage["error"] = "You do not have any machine. Please use /design to create a new machine."
                
            storage = temp_storage

        else:
            for key, machine in temp_storage.items():
                if type.lower() == 'all':
                    temp = FiniteAutomaton.FiniteAutomaton(
                        machine[0],
                        machine[1],
                        eval(machine[2]),
                        machine[3],
                        machine[4],
                    )
                else:
                    if type.lower() == 'nfa' and machine[5] == 'None':
                        continue
                    else:
                        temp = FiniteAutomaton.FiniteAutomaton(
                            machine[0],
                            machine[1],
                            eval(machine[2]),
                            machine[3],
                            machine[4],
                            machine[5]
                        )
                        
                storage[f"FA_{key}"] = temp

        return storage
        

