import utilities.FiniteAutomaton as fa

#----------------------------------------------------------------------------------------------------------
class DFAHelper:

    def __init__(self):
        return
    # minimize dfa
    #------------------------------------------------------------------------------------------------------
    #------------------------------------------------------------------------------------------------------
    def get_minimized_machine(self, original_fa: fa.FiniteAutomaton):
        all_new_states = self.get_all_new_states(original_fa)
        new_delta = self.get_new_delta(original_fa, all_new_states)
        return fa.FiniteAutomaton(
            all_new_states['new_states'],
            original_fa.alphabet,
            new_delta,
            all_new_states['new_initial_state'],
            all_new_states['new_final_states'],
        )
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    def get_all_new_states(self, original_fa: fa.FiniteAutomaton):
        # remove non-accessible states
        dfa = fa.FiniteAutomaton(
            states = self.get_accessible_states(original_fa),
            alphabet = original_fa.alphabet,
            transition_function = original_fa.transition_function,
            initial_state = original_fa.initial_state,
            final_states = original_fa.final_states,
        )
        min_states = self.get_minimized_states(dfa, list()) # empty list is required
        old_new_map = dict()
        new_states = []
        new_initial_state = ''
        new_final_states = []
        i = 0
        for state in min_states:
            new_state = f"q{i}"
            
            for t in state:
                old_new_map[t] = new_state
            
            new_states.append(new_state)

            if ({dfa.initial_state}.intersection(set(state)) != set()):
                new_initial_state = new_state
            if (dfa.final_states.intersection(set(state)) != set()):
                new_final_states.append(new_state)
            i = i + 1
        
        return {
            'min_states': min_states,
            'new_states': new_states,
            'new_initial_state': new_initial_state,
            'new_final_states': new_final_states,
            'old_new_map': old_new_map,
        }
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    def get_accessible_states(self, dfa: fa.FiniteAutomaton):
        accessible_states = set()
        accessible_states.add(dfa.initial_state)
        for key, value in dfa.transition_function.items():
            accessible_states.add(value)

        return accessible_states
    #------------------------------------------------------------------------------------------------------
    

    #------------------------------------------------------------------------------------------------------
    def get_new_delta(self, original_fa: fa.FiniteAutomaton, all_new_state: dict):
        new_delta = dict()
        alphabet = original_fa.alphabet
        min_states = all_new_state['min_states']
        old_new_map = all_new_state['old_new_map']
        for state in min_states:
            for a in sorted(alphabet):
                tmp_output = original_fa.transition_function[(state[0], a)]
                new_delta[(old_new_map[state[0]], a)] = old_new_map[tmp_output]
        return new_delta
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    # this function will return the minimum number of states of a DFA
    # TODO: test this function more...
    def get_minimized_states(self, my_fa: fa.FiniteAutomaton, base_list_of_state_list: list):
        print("\n--> START METHOD: get_minimized_states()")
        # 0-equivalence, separate between the accepting and non-accepting states
        # [[non_accepting_states], [accepting_states]]
        if (base_list_of_state_list == list()):
            non_final_states = my_fa.states.difference(my_fa.final_states)
            base_list_of_state_list.extend([
                sorted(non_final_states), 
                sorted(my_fa.final_states),
            ])
            print(f"--> 0-equivalence: {base_list_of_state_list}")
            print("<-- END METHOD: get_minimized_states()\n")
            return self.get_minimized_states(my_fa, base_list_of_state_list)
        
        # start from 1-equivalence up
        # group the equivalent states together
        # [[equivalent_states_1], [equivalent_states_2], ...]
        new_list_of_state_list = list()

        # go through each list of equivalent states
        # state_list is the list of the equivalent states calculated from the previous recursive call
        for state_list in base_list_of_state_list:
            state_list: list

            # it is already distinguishable
            if (len(state_list) == 1): 
                new_list_of_state_list.append(state_list) # okay
            else:
                # check for equivalent states
                for state in state_list:
                    print(f"--> pairing state '{state}' with others")
                    # check if the state is already included
                    if (self.exist_in_new_list_element(state, new_list_of_state_list)):
                        print(f"--> {state} is already equivalent to a state")
                        continue

                    # it is not included in the list yet
                    new_list_of_state_list.append([state])

                    # create another state list
                    # used to pair with the current state
                    state_list2 = list()
                    state_list2 = state_list.copy()
                    state_list2.remove(state)

                    # used to store equivalent states
                    new_element = [state]

                    # let's check each pair
                    # (A, B) on 0, (A, B) on 1, (A, C) on 0, ...
                    for state2 in state_list2:
                        # the state is already included in an element of new_list_of_state_list
                        if (self.exist_in_new_list_element(state2, new_list_of_state_list)):
                            print(f"--> {state2} is already equivalent to a state")
                            continue

                        flag = self.is_equivalent(my_fa, [state, state2], base_list_of_state_list)

                        # check the equivalence of the two states
                        if (flag):
                            # add the state to its equivalent list
                            # ex: ['A'] to ['A', 'B'] where 'A' and 'B' are equivalent
                            new_element.append(state2)

                    # update the new state
                    # ex: from [['A'], ['C']] to [['A', 'B'], ['C']]
                    new_list_of_state_list[new_list_of_state_list.index([state])] = new_element

                    print(f"--> new_list_element: {new_element}")
                    print(f"--> new_list: {new_list_of_state_list}")

        print(f"--> list of all equivalent states: {new_list_of_state_list}")

        # there is no more distinguishable states, finish the process
        if (new_list_of_state_list == base_list_of_state_list):
            print("<-- END METHOD: get_minimized_states()\n")
            return new_list_of_state_list
        

        print("<-- END METHOD: get_minimized_states()\n")
        # the next recursive call for the next n-equivalence
        return self.get_minimized_states(my_fa, new_list_of_state_list)
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    # (A, B) on 0 -> ???, (A, B) on 1 -> ???
    def is_equivalent(self, my_fa: fa.FiniteAutomaton, pair: list, base_list: list):
        print("\n--> START METHOD: is_equivalent()")
        print(f"--> pair: {pair}")
        delta = my_fa.transition_function.copy()
        alphabet = my_fa.alphabet.copy()
        pair = set(pair)
        # base_list = set(base_list)

        for each_alphabet in sorted(alphabet):
            equivalent = False # set equivalence to false, then try to prove if it is true

            delta_output = set()
            for p in pair:
                delta_output.add(delta[(p, each_alphabet)])

            if (len(delta_output) == 1): # ex: when len(s) == 1, {A, B} -> {B, B} (which is equivalent)
                print(f"--> on {each_alphabet} delta output: {delta_output}")
                equivalent = True
                print(f"--> equivalent: {equivalent}")
                continue
            
            elif (len(delta_output) > 1): 
                for b in base_list:
                    b = set(b)
                    if (delta_output.issubset(b)):
                        equivalent
                        equivalent = True
                # if (not s.issubset(base_list)):
                #     return False

            print(f"--> on {each_alphabet} delta output: {delta_output}")
            print(f"--> equivalent: {equivalent}")

            if (not equivalent):
                print("<-- END METHOD: is_equivalent()\n")
                return equivalent

        print("<-- END METHOD: is_equivalent()\n")
        return equivalent
    #------------------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------------------
    def exist_in_new_list_element(self, state: str, list_of_state_list: list[list]):
        for state_set in list_of_state_list:
            state_set = set(state_set)
            if (state_set.intersection({state}) != set()):
                return True
        return False
    #------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------