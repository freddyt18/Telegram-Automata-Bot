import os
from dotenv import load_dotenv
load_dotenv()
import html
from telebot import types
import telebot
import utilities.FiniteAutomaton as FiniteAutomaton
import utilities.database as db
from tabulate import tabulate
import utilities.fa_controller as fa_controller
import utilities.FiniteAutomaton as fa
import utilities.text as text
import utilities.dfa_helper as dfa_helper
import utilities.transition_func_helper as tr_helper

#GLOBAL VARIABLE
    #Pitou
general_error = "There was some error during the process.\nWe apologize for this problem.\nPlease use /design to input the information to design the Finite Automaton again."

temporary_data_global = dict()

    #Samedy
my_fa_controller: fa_controller.FAController # a global controller
selected_machines = list() # a list of machines selected by the user

# API_TOKEN for Telegram
bot = telebot.TeleBot(os.getenv("Telegram_Dev"))

#Connecting Database
db_con = db.DatabaseConnection(
    os.getenv("DATABASE_HOST"),
    os.getenv("DATABASE_USER"),
    os.getenv("DATABASE_PASS"),
    os.getenv("DATABASE_NAME")
)

# Handle messages
@bot.message_handler(commands=['hello'])
def echo_message(message):

    m_to_send = f"""
    
    [Click here to view your profile.](tg://user?id={message.chat.id})\n
    

    """

    bot.send_message(message.chat.id, m_to_send, parse_mode="Markdown")


@bot.message_handler(commands=["my_machines"])
def send_sample(message):

    machines = dict()
    machines = db_con.get_machine_of_user(message.chat.id, machines)

    bot.send_message(
        message.chat.id, 
        machines["error"] 
        if "error" in machines 
        else "".join(
            f"Machine {key}:\n{value.return_all()}\n\n" for key,value in machines.items()
        )
    )

    # m_to_send = ""
    # for key,machine in machines.items():
    #     if(not db_con.is_duplicated(machine)):
    #         m_to_send += f"Machine {key} is NOT DUPLICATED\n"
    #     else:
    #         m_to_send += f"Machine {key} is DUPLICATED\n"

    # bot.send_message(message.chat.id, m_to_send)
        



@bot.message_handler(commands=["design"])
def design_states(message): 
    bot.send_message(message.chat.id, "• Enter the `states` of the FA. Separate them by commas.\n\nExample: `q1,q2,q3`", parse_mode='Markdown') 
    bot.register_next_step_handler(message, design_alphabets)

def design_alphabets(message):
    
    #Store user's input in a set called states to register it to the next function
    states = set()
    states.update(
        [state for state in str(message.text).replace(" ", "").split(",")]
    )
    states = sorted(states)
    

    bot.send_message(message.chat.id, "Enter the `alphabets` of the FA. Separate them by commas.\n• If there is an `ε` in the states, Enter: `eps`\n\nExample: `a,b,c,eps`", parse_mode='Markdown')
    bot.register_next_step_handler(message, design_delta ,states)

def design_delta(message, states):

    #Store user's input in a set called alphabets to register it to the next function
    alphabets = set()
    alphabets.update(
        [alphabet for alphabet in str(message.text).replace(" ", "").split(",")]
    )
    alphabets = sorted(alphabets)


    #if one of the elements is the symbol epsilon instead of 'eps', we'll replace it back to 'eps'
    alphabets = ["eps" if symbol == "ε" else symbol for symbol in alphabets]


    #Loop over states and alphabets to produce the transition patterns
    m_loop = ""
    error = False

    for state in states:
        if error:
            break

        for symbol in alphabets:

            #If the symbol is EMPTY, alert the user that there's an error
            if not str(symbol):
                error = True
                break

            if str(symbol) == "eps":
                symbol = "ε"

            m_loop += f"{state} transits on {symbol}: \n"


    m_to_send = f"• Seperate by commas, enter the `next states` of `each of those transitions`.\n• If there are multiple, separate them by `hyphen (-)`.\n• If the state transits on a symbol does not produce the next state(s), enter another `comma`\nExample:\nq0 transits on a\nq0 transits on b\nq1 transits on a\nq1 transits on b\n\nInput: `q1,q0,,(q1-q2)`\n\nYour machine:\n{m_loop}"


    if not error:
        bot.send_message(message.chat.id, m_to_send, parse_mode="Markdown")
        bot.register_next_step_handler(message, design_start_state, states, alphabets)
    else:
        bot.send_message(message.chat.id, "Please do not enter empty symbol(s).\nTo enter an `ε`, write: `eps`.\nUse /design to start over.", parse_mode="Markdown")


def design_start_state(message, states, alphabets):

    try:
        delta = dict()
        temp_delta = list(str(message.text).replace(" ", "").split(","))
        
        index = 0
        error = False
        type = False

        if len(states) * len(alphabets) != len(temp_delta):
            error = True
            type = True

        for state in states:
            if error:
                break

            for symbol in alphabets:
                if error:
                    break

                t = temp_delta[index]


                #if there's a paranthesis in the temporary delta,
                #that will mean this state moves on this symbol produces a SET OF NEXT_STATES
                if "(" in str(t):
                    temp_next_states = sorted(set(str(t).replace("(", "").replace(")", "").split("-")))

                    
                    #if one of the elements in the SET OF NEXT_STATES exists
                    #in the SET OF STATES, we will assign them to the dictionary delta
                    #else we will alert the user that there's an error
                    if set(temp_next_states).issubset(states):
                        delta[(state, symbol)] = temp_next_states
                    else:
                        error = True
                        break

                else:
                    
                    #if the next state is AN EMPTY STRING,
                    #we will skip the assignment to the dictionary as this FA is an NFA
                    #else we will repeat the step like above
                    if str(t):
                        if not (str(t) in states):
                            error = True
                            break

                        delta[(state, symbol)] = str(t)

                index += 1

        if not error:
            bot.send_message(message.chat.id, "Enter the `start state`.", parse_mode="Markdown")
            bot.register_next_step_handler(message, design_set_of_final_states, states, alphabets, delta)
        else:
            m_to_send = ""

            if type:
                m_to_send = "• There is/are missing pair(s) of transition.\n• If the pair(s) do/does not produce any state, use another `comma`."
            else:
                m_to_send = "• One of the next state(s) do/does not exist in set of states."
            
            bot.send_message(message.chat.id, f"{m_to_send}\n• Please use /design to start over and verify the next state(s) again.", parse_mode="Markdown")

    except:
        bot.send_message(message.chat.id, general_error)



def design_set_of_final_states(message, states, alphabets, delta):
    start_state = str(message.text)


    if start_state in states:
        bot.send_message(message.chat.id, "Enter the `final states`. If there are multiple, separate them by commas.", parse_mode="Markdown")
        bot.register_next_step_handler(message, design_finish, states, alphabets, delta, start_state)

    else:
        bot.send_message(message.chat.id, "The entered start state *does NOT* exist in the `set of states`.\nPlease use /design to start over again.", parse_mode="Markdown")


def design_finish(message, states, alphabets, delta, start_state):
    set_of_final_states = set([str(message.text).replace(" ", "")]) if "," not in str(message.text) else str(message.text).split(",")

    set_of_final_states = sorted(set_of_final_states)

    if set(set_of_final_states).issubset(states):
        FA = FiniteAutomaton.FiniteAutomaton(states, alphabets, delta, start_state, set_of_final_states)


        #We will check the FA whether it already EXISTS in the database to
        #avoid inputting duplicate data
        if db_con.is_duplicated(FA):
            m_to_send = db_con.assign_user_machine(FA, message.chat.id, message.from_user.username, True)

            
            #if the machine already EXISTS, the function assign_user_machine will return back an error message.
            if m_to_send:
                bot.send_message(message.chat.id, m_to_send)
            else:
                bot.send_message(message.chat.id, FA.return_all())


        else:
            bot.send_message(message.chat.id, FA.return_all())
            db_con.assign_user_machine(FA, message.chat.id, message.from_user.username)


    else:
        bot.send_message(message.chat.id, "One or some of the final state(s) *does/do NOT* exist in `states`.\nPlease use /design to start over again.", parse_mode="Markdown")

            

@bot.message_handler(commands=["delete"])
def delete_machines(message, source = None):
    machines = dict()
    machines = db_con.get_machine_of_user(message.chat.id, machines)
    
    if "error" in machines:
        bot.send_message(message.chat.id, machines["error"])

    else:
        global temporary_data_global

        temporary_data_global[f"{message.chat.id}"] = dict()

        temporary_data_global[f"{message.chat.id}"]["command"] = "delete"
        
        keyboard = types.InlineKeyboardMarkup()
        temp_list_of_machine = list()


        for key, value in machines.items():
            temp_list_of_machine.append(types.InlineKeyboardButton(f"{key}", callback_data=f"{key}"))


        

        temporary_data_global[f"{message.chat.id}"]["machines"] = machines


        for button in temp_list_of_machine:
            keyboard.add(button)


        if source is None:
            bot.send_message(message.chat.id, "Choose a machine to delete:", reply_markup=keyboard)
        else:
            bot.edit_message_text(chat_id=source[0], message_id=source[1], text = "Choose a machine to delete:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call:True)
def all_handlers(call):

    #PITOU
    if temporary_data_global[f"{call.message.chat.id}"]["command"] == "delete":

        keyboard = types.InlineKeyboardMarkup()

        key_yes = types.InlineKeyboardButton("Yes, I am sure.", callback_data="yes_delete")
        key_no = types.InlineKeyboardButton("<< No, Go back.", callback_data="no_delete")

        keyboard.add(key_no, key_yes)
        
        for key, value in temporary_data_global[f"{call.message.chat.id}"]["machines"].items():
            if str(key) == call.data:
                m_to_send = f"`{key}`\n{value.return_all()}\n\nYou are about to delete this machine.\n\n*Are you sure?*"
                
                temporary_data_global[f"{call.message.chat.id}"]["current_machine_id"] = f"{key}"

                bot.edit_message_text(chat_id = call.message.chat.id, message_id=call.message.message_id, text = m_to_send, parse_mode="Markdown", reply_markup=keyboard)

                break

        
        if call.data == "no_delete":
            delete_machines(call.message, [call.message.chat.id, call.message.message_id])
        elif call.data == "yes_delete":
            m_id = temporary_data_global[f"{call.message.chat.id}"]["current_machine_id"].replace("FA_", "")
            print(m_id)

            db_con.execute_query(f"DELETE FROM Client_Tbl WHERE ChatID = '{call.message.chat.id}' AND machineID = {m_id};", "delete")

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Machine FA_{m_id} has been deleted successfully.")

    
    #SAMEDY
    elif temporary_data_global[f"{call.message.chat.id}"]["command"] == "check_string":
        global selected_machines
        
        my_fa_controller.clear_final_states_calculated() # clear the final states calculated if there's any
        finite_automata = my_fa_controller.get_finite_automata() # get all machines
        key: str # store the key of the clicked machine
        
        # 'Continue' button
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text = 'Continue', callback_data = 'continue with string processing'))
        
        for key in finite_automata:
            # find the machine to be selected
            if (call.data == f"select_{key}"):
                print(f'--> you clicked: {key}, {finite_automata[key]}')
                # click to select, click again to deselect
                if (selected_machines.count(key)):
                    selected_machines.remove(key)
                else:
                    selected_machines.append(key)
                
                tmp_str = ''
                for s in selected_machines:
                    tmp_str += f"   .  {s}\n"
                
                reply_markup = None
                if (selected_machines != list()): 
                    reply_markup = keyboard
                
                bot.edit_message_text(
                    chat_id = call.message.chat.id, 
                    message_id = call.message.id + 2, 
                    text = f"Machine(s) you selected:\n\n<b>{tmp_str}</b>",
                    reply_markup = reply_markup,
                    parse_mode = 'HTML',
                )
                return
            # find the machine to be viewed
            elif (call.data == f"just_view_{key}"):
                table = to_table(finite_automata[key])

                if (is_dfa(finite_automata[key])):
                    tmp_dfa = fa.FiniteAutomaton(
                        states = eval(finite_automata[key].states),
                        alphabet = eval(finite_automata[key].alphabet),
                        transition_function = finite_automata[key].transition_function.copy(),
                        initial_state = finite_automata[key].initial_state,
                        final_states = list(eval(finite_automata[key].final_states)),
                    )
                    get_dfa_delta(tmp_dfa.transition_function)
                    table = dfa_to_table(tmp_dfa)

                try:
                    bot.edit_message_text(
                        chat_id = call.message.chat.id,
                        message_id = call.message.id + 1,
                        text = f"<b>{key}</b>:\n\n{finite_automata[key].return_all()}\n\n<pre>{table}</pre>\n", 
                        parse_mode = 'HTML',
                    )
                except:
                    bot.edit_message_text(
                        chat_id = call.message.chat.id,
                        message_id = call.message.id + 1,
                        text = "&lt<i>Your viewed machine</i>&gt", 
                        parse_mode = 'HTML',
                    )
                return
            
            # minimize dfa
            elif (call.data == f"minimize_{key}"):
                my_dfa_helper = dfa_helper.DFAHelper()
                my_dfa: fa.FiniteAutomaton = my_fa_controller.get_finite_automata()[key]
                tmp_dfa = fa.FiniteAutomaton(
                    states = set(eval(my_dfa.states)),
                    alphabet = set(eval(my_dfa.alphabet)),
                    transition_function = my_dfa.transition_function.copy(),
                    initial_state = my_dfa.initial_state,
                    final_states = set(eval(my_dfa.final_states)),
                )
                get_dfa_delta(tmp_dfa.transition_function)
                new_min_dfa = my_dfa_helper.get_minimized_machine(tmp_dfa)

                if (len(new_min_dfa.states) == len(tmp_dfa.states)): # still the same number of states
                    bot.send_message(call.message.chat.id, f"Your <b>{key}</b> DFA is already minimal!\n\n", parse_mode = "HTML")
                else:
                    bot.send_message(call.message.chat.id, f"The Minimal DFA of {key}:\n\n{new_min_dfa.return_all()}\n\n<pre>{dfa_to_table(new_min_dfa)}</pre>", parse_mode = 'HTML')
                return
        
        # process with all machines
        if (call.data == "process with all machines"):
            selected_machines = my_fa_controller.get_finite_automata()
            bot.send_message(call.message.chat.id, text = "\nPlease enter the string(s):\n")
            bot.register_next_step_handler(call.message, input_string, selected_machines)
            # for key in selected_machines:
            #     bot.register_next_step_handler(call.message, process_string, machine_key = key)
        
        
        # continue with the selected machines
        elif (call.data == "continue with string processing"):
        
            # bot.send_message(call.message.chat.id, text = f"You selected {key}:\n\t<pre>{to_table(finite_automata[key])}</pre>\n", parse_mode = 'HTML')
            
            bot.send_message(call.message.chat.id, text = "\nPlease enter the string(s):\n")
            bot.register_next_step_handler(call.message, input_string, selected_machines)
            return
                

        # if (call.data == "view machine as simple text"):
        #     keyboard = types.InlineKeyboardMarkup()
        #     keyboard.add(types.InlineKeyboardButton('Tabular Form', callback_data = "view machine as tabular form"))
        #     bot.edit_message_text(chat_id = call.message.chat.id, 
        #                           message_id = call.message.message_id, 
        #                           text = f"{call.data.return_all()}")
        #     return

    #QikKenzz & Raksa
    elif temporary_data_global[f"{call.message.chat.id}"]["command"] == "type":
        
        # Create return back button 
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('<< Return', callback_data = 'return'))

        if call.data == "return":
            list_machines(call.message, [call.message.chat.id, call.message.message_id])
        else:
            machineID = call.data
            machineValue = temporary_data_global[f"{call.message.chat.id}"]["machines"][machineID]
            
            query = f"SELECT * FROM UserMachineDetail_Tbl WHERE machineID = '{machineID.strip('FA_')}';"
            machine_detail = db_con.execute_query(query, "select")
            
            # Return cache Machine Type and Description from UserMachineDetail_Tbl if exists
            if machine_detail and machine_detail[0][2]:
                machine_type = machine_detail[0][2]
                description = html.unescape(machine_detail[0][4])
            else:
                # If the "type" column does not have a value, calculate the the type of the machine
                alphabet = eval(machineValue.alphabet)
                delta = machineValue.transition_function
                
                # Check if the alphabet contains the symbol "eps"
                if "eps" in alphabet:
                    machine_type = "NFA"
                    description = text.eps
                else:
                    # If not, then check if |δ| = |Q| x |Σ|
                    if len(delta) == len(eval(machineValue.states)) * len(alphabet):
                        for key, value in delta.items():
                            if isinstance(value, list):
                                machine_type = "NFA"
                                description = text.nfa_set_of_state
                                break
                            else:
                                machine_type = "DFA"
                                description = text.dfa
                    else:
                        machine_type = "NFA"
                        description = text.nfa_transition(len(eval(machineValue.states)), len(alphabet))
                        
                # Update the "type" in the UserMachineDetail_Tbl
                query = f"UPDATE UserMachineDetail_Tbl SET type = '{machine_type}', description = '{html.escape(description)}'  WHERE machineID = {machineID.strip('FA_')};"
                machine_detail = db_con.execute_query(query, "update")
                    
            bot.edit_message_text(chat_id = call.message.chat.id, message_id=call.message.message_id, text = f"Your Machine: <b>{machineID}</b>:\n<pre>{to_table_QikKenzz(machineValue)}</pre>\n\nYour Machine is <b>{machine_type}</b>\n{description}", parse_mode = 'HTML', reply_markup=keyboard)
    
    elif temporary_data_global[f"{call.message.chat.id}"]["command"] == "convert":
        
        # Create return back button 
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('<< Return', callback_data = 'return'))

        if call.data == "return":
            get_machines(call.message, [call.message.chat.id, call.message.message_id])
        else:
            machineID = call.data
            machineValue = temporary_data_global[f"{call.message.chat.id}"]["machines"][machineID]
            
            query = f"SELECT * FROM UserMachineDetail_Tbl WHERE machineID = '{machineID.strip('FA_')}';"
            machine_detail = db_con.execute_query(query, "select")
            
            fa_machine = nfa_to_dfa(eval(machineValue.states), eval(machineValue.alphabet), tr_helper.get_transition_function(
                machineValue.transition_function), machineValue.initial_state, eval(machineValue.final_states))
             
            bot.edit_message_text(chat_id = call.message.chat.id, message_id=call.message.message_id, text = f"Your <b>NFA</b> Machine: <b>{machineID}</b>\n<pre>{to_table_QikKenzz(machineValue)}</pre>\n\nAfter conversion to <b>DFA</b>:\n<pre>{to_table_QikKenzz(fa_machine)}</pre>", parse_mode = 'HTML', reply_markup=keyboard)

#SAMEDY

#---------------------------------------------------------------------------------------------------------------
def input_string(message, selected_machines: list):
    end_result = ''
    
    for s in selected_machines:
        end_result += process_string(message, s)
        
    bot.send_message(message.chat.id, end_result, parse_mode = 'HTML')
#---------------------------------------------------------------------------------------------------------------

def process_string(message, machine_key):
    global my_fa_controller
    global selected_machines
    my_string: str = message.text
    my_list_of_string: list = my_string.split(',')
    
    # print(f"processing with: {my_list_of_string}")
    m: fa.FiniteAutomaton = my_fa_controller.get_finite_automata()[f'{machine_key}']
    x = set(eval(m.alphabet))
    
    print(f"--> alphabet = {x}")
    
    result = ''
    for s in my_list_of_string:
        my_fa_controller.clear_final_states_calculated()  # clear the calculated final states
        s = s.strip() # remove both left and right white spaces
        
        # TODO: check if the input is the valid string over the alphabet (DONE)
        invalid_str = False
        for c in s:
            tmp_set = set(c)
            print(f"--> tmp_set = {tmp_set}")
            print(f"--> intersection: {x.intersection(tmp_set)}")
            if (x.intersection(tmp_set) == set()):
                result += f"  . Error while processing the string '{s}', the '{c}' symbol does not exist in the alphabet {x}\n"
                invalid_str = True
                break
        
        if (invalid_str): continue        
        
        is_accepted = my_fa_controller.is_str_accepted(my_fa_controller.get_finite_automata()[f'{machine_key}'], s)
    
        if (is_accepted): 
            result += f"  . '{s}' is accepted\n"
        else:               
            result += f"  . '{s}' is rejected\n"
    
    return f"<b>Machine {machine_key}</b>:\n{result}\n"
#---------------------------------------------------------------------------------------------------------------
      
#---------------------------------------------------------------------------------------------------------------
# display the transition function in the tabular form
def to_table(machine: fa.FiniteAutomaton):
    delta = machine.transition_function
    
    headers = ['']
    tabular_data = []
    
    for symbol in eval(machine.alphabet):
        headers.append(symbol)
    
    for state in eval(machine.states):
        row = [state]
        if (state == machine.initial_state and list(eval(machine.final_states)).count(state)):
            row = [f"-> * {state}"]
        elif (state == machine.initial_state):
            row = [f"-> {state}"]
        elif (list(eval(machine.final_states)).count(state)):
            row = [f"* {state}"]
        
        for symbol in headers:
            transit_output = {}
            if (headers.index(symbol) == 0):
                continue
            
            if (delta.get((state, symbol))):
                transit_output = set(delta[(state, symbol)])

            row.append(transit_output)
            
        tabular_data.append(row)
    return tabulate(tabular_data, headers = headers, tablefmt = "grid")  
#---------------------------------------------------------------------------------------------------------------



@bot.message_handler(commands = ['check_strings', 'check_string'])
def check_string(message):

    global temporary_data_global

    temporary_data_global[f"{message.chat.id}"] = dict()

    temporary_data_global[f"{message.chat.id}"]["command"] = "check_string"

    # access the global fa controller and initialize the chatID of the user
    global my_fa_controller # access the global fa controller
    my_fa_controller = fa_controller.FAController(message.chat.id) # initialize the chatID of the user
    finite_automata = my_fa_controller.get_finite_automata() # retrieve user's machines
    global selected_machines
    selected_machines = list()
    
    # check if the user has any machines
    if (finite_automata == {}):
        bot.send_message(
            message.chat.id, 
            f"You do not have any machine. Please use /design to create a new machine."
        )
        return
    
    keyboard = types.InlineKeyboardMarkup()
    for key in finite_automata: # key format: 'FA_#'
        keyboard.add(types.InlineKeyboardButton(f"{key}", callback_data = f"select_{key}"), 
                     types.InlineKeyboardButton("View", callback_data = f"just_view_{key}"))
        
    # TODO: check the given strings with all machines (DONE)
    keyboard.add(types.InlineKeyboardButton(text = 'Check With All Machines', callback_data = 'process with all machines'))
    
    bot.send_message(chat_id = message.chat.id, text = 'Please choose machine(s):', reply_markup = keyboard)
    bot.send_message(chat_id = message.chat.id, text = "&lt<i>Your viewed machine</i>&gt", parse_mode = 'HTML')
    bot.send_message(chat_id = message.chat.id, text = f"Machine(s) you selected:\n\n")




# dfa minimization
#---------------------------------------------------------------------------------------------------------------
@bot.message_handler(commands = ['minimize_dfa'])
def minimize_dfa(message):
    global temporary_data_global

    temporary_data_global[f"{message.chat.id}"] = dict()

    temporary_data_global[f"{message.chat.id}"]["command"] = "check_string"

    global my_fa_controller # access the global fa controller
    my_fa_controller = fa_controller.FAController(message.chat.id) # initialize the chatID of the user
    finite_automata = my_fa_controller.get_finite_automata() # retrieve user's machines
    # global selected_machines
    # selected_machines = list()
    
    # check if the user has any machines
    if (finite_automata == {}):
        bot.send_message(
            message.chat.id, 
            f"You do not have any machine. Please use /design to create a new machine."
        )
        return
    
    keyboard = types.InlineKeyboardMarkup()
    for key in finite_automata: # key format: 'FA_#'
        if (is_dfa(my_fa_controller.get_finite_automata()[key])):
            keyboard.add(types.InlineKeyboardButton(f"{key}", callback_data = f"minimize_{key}"), 
                        types.InlineKeyboardButton("View", callback_data = f"just_view_{key}"))
    
    bot.send_message(chat_id = message.chat.id, text = 'Please choose a DFA:', reply_markup = keyboard)
    bot.send_message(chat_id = message.chat.id, text = "&lt<i>Your viewed machine</i>&gt", parse_mode = 'HTML')
    return
#---------------------------------------------------------------------------------------------------------------



# display the transition function in the tabular form
def dfa_to_table(machine: fa.FiniteAutomaton):
    delta = machine.transition_function
    
    headers = ['']
    tabular_data = []
    
    for symbol in sorted(machine.alphabet):
        headers.append(symbol)
    
    for state in sorted(machine.states):
        row = [state]
        if (state == machine.initial_state and list(machine.final_states).count(state)):
            row = [f"-> * {state}"]
        elif (state == machine.initial_state):
            row = [f"-> {state}"]
        elif (list(machine.final_states).count(state)):
            row = [f"* {state}"]
        
        for symbol in headers:
            transit_output = {}
            if (headers.index(symbol) == 0):
                continue
            
            if (delta.get((state, symbol))):
                transit_output = delta[(state, symbol)]

            row.append(transit_output)
            
        tabular_data.append(row)
    return tabulate(tabular_data, headers = headers, tablefmt = "grid")  
#---------------------------------------------------------------------------------------------------------------


# get type
def is_dfa(fa: fa.FiniteAutomaton):
    alphabet = fa.alphabet
    delta = fa.transition_function
    machine_type = ''

    if "eps" in alphabet:
        machine_type
        machine_type = "NFA"
    else:
        # If not, then check if |δ| = |Q| x |Σ|
        if len(delta) == len(eval(fa.states)) * len(eval(alphabet)):
            for key, value in delta.items():
                if len(value) > 1:
                    machine_type = "NFA"
                    break
                else:
                    machine_type = "DFA"
        else:
            machine_type = "NFA"
    return machine_type == "DFA"
#---------------------------------------------------------------------------------------------------------------


def get_dfa_delta(delta: dict):
    for key in delta:
        delta[key] = delta[key][0]

 



# QikKenzz and Raksa
# Handler for TYPE
@bot.message_handler(commands=['type'])
def list_machines(message, source=None):
    machines = dict()
    machines = db_con.get_machine_of_user(message.chat.id, machines, 'all_type')

    if "error" in machines:
        bot.send_message(message.chat.id, machines["error"])

    else:
        global temporary_data_global
        temporary_data_global[f"{message.chat.id}"] = dict()
        temporary_data_global[f"{message.chat.id}"]["command"] = "type"

        keyboard = types.InlineKeyboardMarkup()
        for key, value in machines.items():
            if value.type == 'None':                
                machineType = '____'
            else: machineType = value.type
            keyboard.add(types.InlineKeyboardButton(text=f"{key}: {machineType}", callback_data=f"{key}"))

        temporary_data_global[f"{message.chat.id}"]["machines"] = machines
        
        if source is None:
            bot.send_message(
                message.chat.id, "Choose a <b>machine</b> to check:", reply_markup=keyboard, parse_mode='html')
        else:
            bot.edit_message_text(
                chat_id=source[0], message_id=source[1], text="Choose a machine to check:", reply_markup=keyboard)


def to_table_QikKenzz(machine: fa.FiniteAutomaton):
    delta = machine.transition_function
    headers = ['']
    tabular_data = []
    
    for symbol in eval(machine.alphabet):
        headers.append(symbol)
    
    for state in eval(machine.states):
        row = [state]
        if (state == machine.initial_state and list(eval(machine.final_states)).count(state)):
            row = [f"-> * {state}"]
        elif (state == machine.initial_state):
            row = [f"-> {state}"]
        elif (list(eval(machine.final_states)).count(state)):
            row = [f"* {state}"]
        
        for symbol in headers:
            transit_output = {}
            if (headers.index(symbol) == 0):
                continue
                
            transit_output = delta.get((state, symbol))

            row.append(transit_output)
            
        tabular_data.append(row)    
        
    # Replace eps in header with 'ε'
    if 'eps' in headers:
        headers[headers.index('eps')] = 'ε'
    
    # Replace Empty set with 'Ø'
    for i in range(len(tabular_data)):
        for j in range(len(tabular_data[i])):
            if tabular_data[i][j] is None:
                tabular_data[i][j] = "Ø"
 
    return tabulate(tabular_data, headers = headers, tablefmt = "grid", colalign=("right",))

def epsilon_closure(states, delta):
    # Save Given States in @e_closure
    print(f'states: {states}')
    e_closure = set(states)
    stack = list(states)
    print(f'{e_closure} move to Epsilon Closure')
    
    # Recursive states to get next Epsilon Closure
    while stack:
        state = stack.pop()
        # Save all next state of the Transition that have 'ε'
        e_states = delta.get((state, 'eps'), [])
        
        # Loop Every Epsilon Next State
        for e_state in e_states:
            # If Epislon state is not in Given States, add it to @e_closure then recursive remaining state in @e_closure
            if e_state not in e_closure:
                e_closure.add(e_state)
                stack.append(e_state)
    print(f'\t => RETURN{e_closure}\n')
    return frozenset(e_closure)

def nfa_to_dfa(states, alphabet, delta, start_state, final_states):
    # Initialize
    dfa_states = set()
    dfa_delta = {}
    dfa_start_state = epsilon_closure([start_state], delta)
    dfa_final_states = set()
    stack = [dfa_start_state]
    
    # Recursive each State on Given Alphabet
    while stack:
        state_set = stack.pop()
        dfa_states.add(state_set)
        print(f'======>dfa_states: {dfa_states}')
        for symbol in alphabet:
            print(f'{state_set} on {symbol}: ')
            if symbol == 'eps':
                continue
            next_states = set()
            for state in state_set:
                next_states |= set(delta.get((state, symbol), ['Ø']))   # Get Reject State when no Transition
            if not next_states:
                continue
            print(f'=> next_states: {next_states}\n')
            # 
            next_state_set = epsilon_closure(next_states, delta)
            dfa_delta[(state_set, symbol)] = next_state_set
            # 
            if next_state_set not in dfa_states:
                stack.append(next_state_set)
                
        #  Check if any of the states in the current set of states of @state_set is a final state. if so, add it to dfa_final_states
        if any(state in final_states for state in state_set):
            dfa_final_states.add(state_set)
    
    # RENAME STATE ----------------------------------------------------------
    state_dict = {}
    count = 0
    for state in dfa_states:
        state_dict[f"q{count}\'"] = list(state)
        count += 1
        
    # Replace state names in dfa_states, dfa_delta, dfa_start_state, and dfa_final_states
    new_dfa_states = set()
    new_dfa_delta = {}
    new_dfa_start_state = None
    new_dfa_final_states = set()
    for state_set in dfa_states:
        new_state_set = frozenset([f"q{i}'" for i in range(len(state_dict) + 1) if state_dict.get(f"q{i}'") == list(state_set)])
        new_dfa_states.add(new_state_set)
        if state_set == dfa_start_state:
            new_dfa_start_state = new_state_set
        if state_set in dfa_final_states:
            new_dfa_final_states.add(new_state_set)
        for symbol in alphabet:
            next_state_set = dfa_delta.get((state_set, symbol), None)
            if next_state_set is not None:
                new_next_state_set = frozenset([f"q{i}'" for i in range(len(state_dict) + 1) if state_dict.get(f"q{i}'") == (list(next_state_set))])
                new_dfa_delta[(new_state_set, symbol)] = set(sorted(new_next_state_set))
  
    dfa_delta_dict = {}
    for key, value in new_dfa_delta.items():
        dfa_delta_dict[tuple(sorted(list(key[0]))), key[1]] = sorted(list(value))
    new_dfa_delta = {(''.join(state), symbol): ''.join(next_state) 
            for (state, symbol), next_state in dfa_delta_dict.items()}

    dfa_states = [list(state)[0] for state in new_dfa_states]
    dfa_delta = new_dfa_delta    
    dfa_start_state = list(new_dfa_start_state)[0]
    dfa_final_states = [list(state)[0] for state in new_dfa_final_states]
    # ------------------------------------------------------------------------
    
    return FiniteAutomaton.FiniteAutomaton(str(sorted(dfa_states).copy()), str([symbol for symbol in alphabet if symbol != 'eps']), dfa_delta, str(dfa_start_state), str(dfa_final_states))

@bot.message_handler(commands=['nfa_to_dfa'])
def get_machines(message, source=None):    
    machines = dict()
    machines = db_con.get_machine_of_user(message.chat.id, machines, 'nfa')

    if "error" in machines:
        bot.send_message(message.chat.id, machines["error"])
    elif machines == {}:
        bot.send_message(message.chat.id, text='Not every Machine is checked yet. Please use /type to check your remaining Machine.')

    else:
        global temporary_data_global
        temporary_data_global[f"{message.chat.id}"] = dict()
        temporary_data_global[f"{message.chat.id}"]["command"] = "convert"

        keyboard = types.InlineKeyboardMarkup()
        temp_list_of_machine = list()

        for key, value in machines.items():
            temp_list_of_machine.append(types.InlineKeyboardButton(f"{key}", callback_data=f"{key}"))

        temporary_data_global[f"{message.chat.id}"]["machines"] = machines

        for button in temp_list_of_machine:
            keyboard.add(button)

        if source is None:
            bot.send_message(
                message.chat.id, "Your <b>NFA</b> Machines:", reply_markup=keyboard, parse_mode='HTML')
        else:
            bot.edit_message_text(
                chat_id=source[0], message_id=source[1], text="Choose a machine to convert to DFA:", reply_markup=keyboard)


# Start the bot
bot.infinity_polling()
