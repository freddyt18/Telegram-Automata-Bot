import hashlib


class FiniteAutomaton:
    def __init__(self, states: set, alphabet: set, transition_function: dict, initial_state: str, final_states: set, type: str = 'Unchecked'):
        '''
            Creating FiniteAutomaton instance.\n
            Takes in
                ``states``:``set``
                ``alphabet``:``set``
                ``transition_function``:``dict``
                ``initial_state``:``str``
                ``final_states``:``set``
                ``type (Optional)``:``str``
        '''
        
        self.states = states
        self.alphabet = alphabet
        self.transition_function = transition_function
        self.initial_state = initial_state
        self.final_states = final_states
        self.type = type


    def is_final_state(self, state):
        return state in self.final_states
    
    def hash_of_machine(self):

        text = f"{self.states},{self.transition_function},{self.alphabet},{self.initial_state},{self.final_states}".replace('"', "")
        
        encoded = text.encode('utf-8')
        hash_object = hashlib.sha256(encoded)
        hex_hash = hash_object.hexdigest()

        return str(hex_hash)

    def return_all(self):
        return "States: " + str(self.states) + "\n" + "Alphabet: " + str(self.alphabet) + "\n" + "Transition Function: " + str(self.transition_function) + "\n" + "Initial State: " + str(self.initial_state) + "\n" + "Final States: " + str(self.final_states)
        
