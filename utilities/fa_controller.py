import utilities.FiniteAutomaton as fa
import utilities.database as db
import utilities.table_name_const as tbl
import utilities.query_type_const as type
import utilities.transition_func_helper as trHelper
import utilities.user_machine_str as ma_str
import os
from dotenv import load_dotenv

load_dotenv()

# create a database connection
db = db.DatabaseConnection(
    os.getenv("DATABASE_HOST"),
    os.getenv("DATABASE_USER"),
    os.getenv("DATABASE_PASS"),
    os.getenv("DATABASE_NAME"),
)

conn = db.connect_to_database()


# a class to handle tha machines of a specific user
class FAController:
    
    #----------------------------------------------------------------------------
    def __init__(self, chatID):
        
        # store the chat id of the telegram user
        self.__chatID = chatID
        
        # let's retrieve machines of the user
        self.retrieve_machines()
        
        # all of the user's machines are fetched and stored in self.__finite_automata
        self.__finite_automata: dict # dict[str, FA.FiniteAutomaton]
        
        # used to store the final states calculated from delta
        self.__final_states_calculated = list()
    #----------------------------------------------------------------------------
        
    
    #-------------------------------------------------------------------------------------
    # here are just some getter methods
    def get_chatID(self) -> str:
        return self.__chatID
    
    def get_finite_automata(self) -> dict: # dict[str, FA.FiniteAutomaton]
        return self.__finite_automata
    #-------------------------------------------------------------------------------------
        
    
    #-------------------------------------------------------------------------------------
    # retrieve all machines of the user
    def retrieve_machines(self) -> None:
        self.__finite_automata = db.get_machine_of_user(self.__chatID, {})

        # in case there is no machine, the 'error' key exists so let's store the empty dictionary instead
        if (self.__finite_automata.get('error')):
            self.__finite_automata = dict()
            
            
        # TODO: may be nothing, we'll find out soon
        for key in self.__finite_automata:
            self.__finite_automata[key].transition_function = trHelper.get_transition_function(self.__finite_automata[key].transition_function)
    #-------------------------------------------------------------------------------------
    
    
    # get one machine only
    # def get_finite_automaton(self, fa_id: str):
    #     return self.__finite_automata[fa_id]
    
    
    #-----------------------------------------------------------------------------------------------------------
    # get all the final states from processing a string
    def get_final_states_calculated(self):
        return self.__final_states_calculated
    #-----------------------------------------------------------------------------------------------------------
    
    
    #-------------------------------------------
    def clear_final_states_calculated(self):
        self.__final_states_calculated = list()
    #---------------------------------------------
    
    
    # These methods are used together to check if a machine can accept a given string.
    #-----------------------------------------------------------------------------------------------------------
    def is_str_accepted(self, machine: fa.FiniteAutomaton, str: str) -> bool:
        print('--> START METHOD: is_str_accepted')
        # TODO: check if the string has been processed by the machine
        if (self.has_been_checked(machine, str) == 0):
            print('--> Has been checked once: rejected')
            return False
        elif (self.has_been_checked(machine, str) == 1):
            print('--> Has been checked once: accepted')
            return True
        
        print('--> Has not been checked')
        
        self.__is_str_accepted(machine = machine, str = str)
        
        # check if any element of the machine's final states matches the an element of the received final states
        set1 = set(self.__final_states_calculated)
        set2 = set(eval(machine.final_states))
        set3 = set1.intersection(set2)       # find if there is at least one matched element
        
        # TODO: store the str accepted by the machine in the database
        ma_str.UserMachineStrController().add_new(ma_str.UserMachineStrModel(
            machine_hash = machine.hash_of_machine(),
            string = str,
            str_type = 1 if (set3 != set()) else 0,
        ))
        
        print('<-- END METHOD: is_str_accepted')
        
        return set3 != set()
    #-----------------------------------------------------------------------------------------------------------


    #-----------------------------------------------------------------------------------------------------------
    # This method is made private as a mean to prevent from the modification of the default values of some parameters.
    def __is_str_accepted(
        self, 
        machine: fa.FiniteAutomaton,    # machine in which the string is to be processed with
        str: str,                       # string to be checked
        current_index: int = -1,         # keep track of the character index of the string
        current_states: list = []       # keep track of the states got from the transition function
    ) -> None:
        print("--> START METHOD: __is_str_accepted")
        
        # before we proceed any further, let's apply the epsilon closure on the start state first
        if (current_index == -1):
            # store the start state in a list
            l = list()
            l.append(machine.initial_state)
            print("--> let's apply the epsilon closure on the initial state")
            current_states = self.epsilon_closure(l, machine)
            print(f"--> (index = {current_index}) => state_list = {current_states}")
            
        
        # # the following condition provides the initial value to the current_states which is derived from 
        # # transition_function(start_state, first_symbol)
        # if (current_index == 0):
        #     print(f"--> start state: {machine.initial_state}, symbol: {str[current_index]}")       
        #     current_states = machine.transition_function[(machine.initial_state, str[current_index])]
        #     print(f"--> The calculated set of states: {set(current_states)}, let's apply the epsilon closure")
        #     current_states = self.epsilon_closure(current_states, machine)
    
    
        # if (current_index > -1):
        #     print(f"--> symbol = {str[current_index]} (index = {current_index}) => state_list = {current_states}")
        
        
        # increase the index of the string's character
        next_index = current_index + 1
        
        
        # condition to stop the recursion
        if (len(str) == next_index):
            print(f"--> index = {next_index}, gotta stop the recursion!") 
            
            # save the final result in the final states
            set1 = set(self.__final_states_calculated)  # convert to a set
            set2 = set(current_states)                  # convert to a set
            set3 = set1.union(set2)                     # performs union operation on the two set
            self.__final_states_calculated = list(set3) # convert back to list for easy element access
            # TODO: need to consider epsilon (DONE)
            return
        
        # loop through all the states calculated from the transition function
        for i in range(len(current_states)):
            
            current_state = current_states[i]
            current_symbol = str[next_index]
            
            print(f"--> state: {current_states[i]}, symbol: {current_symbol}")
            
            # check if the (state, symbol) exist as a key in the dictionary
            if (machine.transition_function.get((f'{current_state}', f'{current_symbol}')) is None):
                next_states = []
            else:
                next_states = machine.transition_function[(f'{current_state}', f'{current_symbol}')]
            
            print(f"--> The calculated set of states: {set(next_states)}, let's apply the epsilon closure")
            next_states = self.epsilon_closure(next_states, machine)
                
            # next recursive call
            print("--> NEXT RECURSIVE CALL OF __is_str_accepted")
            self.__is_str_accepted(
                machine = machine,
                current_states = next_states, 
                current_index = next_index, 
                str = str
            )
            
        print("<-- END METHOD: __is_str_accepted")
    #-----------------------------------------------------------------------------------------------------------
    
    
    #-----------------------------------------------------------------------------------------------------------        
    # check whether the string has been processed by a particular machine before
    def has_been_checked(self, machine: fa.FiniteAutomaton, str: str):
        # TODO: do something....
        controller = ma_str.UserMachineStrController()
        return controller.get_acceptance_type(machine, str)
    #-----------------------------------------------------------------------------------------------------------
    
    
    #-----------------------------------------------------------------------------------------------------------
    # apply epsilon closure to symbols which can be transited via eps
    def epsilon_closure(self, states: list, machine: fa.FiniteAutomaton) -> list:
        print('--> START METHOD: epsilon_closure')
        
        state_set = set(states)
        transited_output = set()
        delta = machine.transition_function
        new_set = set()
        
        for state in states:
            if (delta.get((state, 'eps'))):
                transited_output = set(delta[(state, 'eps')])
        
        new_set = state_set.union(transited_output)
        
        print(f"--> epsilon closure on {set(states)}: {new_set}")     
        print('<-- END METHOD: epsilon_closure')
        
        if (new_set != state_set):
            return self.epsilon_closure(list(new_set), machine)
        else:
            return list(new_set)
    #-------------------------------------------------------------------------------------------------------   
#-----------------------------------------------------------------------------------------------------------  


#-----------------------------------------------------------------------------------------------
def main() -> None:
    fa_controller = FAController()
    
    # process one string with one machine
    key = 'FA_2'
    str = '0101'
    processing_machine = fa_controller.get_finite_automata()[key]
    
    accepted = fa_controller.is_str_accepted(machine = processing_machine, str = str)

    print(f"\n{processing_machine.return_all()}")
    print(f"\nFinal states calculated: {set(fa_controller.get_final_states_calculated())}")
    print(f"Expected final states: {fa_controller.get_finite_automata()[key].final_states}\n")


    if accepted:
        print('<< Your string is accepted! >>')
    else:
        print('<< Your string is rejected! >>')
        
    # process one string with all machines
    
    # process multiple strings with one machines
    
    # process multiple strings with multiple machines
#-----------------------------------------------------------------------------------------------



# main()
