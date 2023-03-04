eps = "If the alphabet includes epsilon(ε), the automaton is typically considered a Non-deterministic Finite Automaton (NFA) because it allows for the possibility of transitioning without consuming an input symbol."
nfa_set_of_state = "The given machine is a Non-Deterministic Finite Automaton (NFA) because it has at least one state where, on a particular input symbol, it has multiple possible transitions."
def nfa_transition(state, alpha): return f"If the transition is less than |Q| x |Σ| which is {state} x {alpha} or a transition is missing, then it is an NFA. "
dfa = "The given machine is a Deterministic Finite Automaton (DFA) as it has a unique transition from each state on each input symbol"