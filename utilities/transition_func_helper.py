# Convert each tran_func result to a list for easily accessing by index
# Expected output is something like this: {('q0', 'a'): ['q1'], ('q0', 'b'): ['q0', 'q1']} 
def get_transition_function(tran_func: dict):
    new_delta = {}
    for key in tran_func:
        my_set = set()
        
        try:
            my_set.add(tran_func[key])
        except TypeError:
            my_set = tran_func[key]
        
        new_delta[key] = list(my_set)
        
    return new_delta

""" 
transition_func = {('q0', 'a'): 'q1', ('q0', 'b'): ['q0', 'q1']}
print(get_transition_function(transition_func)) # {('q0', 'a'): ['q1'], ('q0', 'b'): ['q0', 'q1']} 
"""
