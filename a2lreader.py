#!/usr/bin/env python3
import os
from a2lstream import *
from tkinter import *
from tkinter import filedialog
import cProfile
import pstats

def ini_global_vars():
    """Initialization of global variables"""
    global command_list, version, labels_list, encoding, input_text, input_text_default, input_prompt, elements_dict, elements_list
    command_list={} # The commands list is loaded from the commands.txt file
    version = '0.1'
    labels_list = []
    encoding = 'latin-1'
    input_text_default = 'A2LReader'
    input_prompt = '> '
    input_text = ''
    elements_dict = {}
    elements_list = {}

def load_a2l_dictionary():
    """Load a2l dictionary from a2ldict.txt"""
    global elements_dict, elements_list
    try:
        dict_file = open('a2ldict.txt','r')
        for line in dict_file:
            line_list = list(line.split(";"))
            elements_dict[line_list[0]]=line_list[1:-1]
            elements_list[line_list[0]]={}
        dict_file.close()
    except:
        print('Unable to load a2ldict.txt')

def load_commands():
    """Load software commands from commands.txt"""
    #current_path = os.getcwd()
    try:
        commands_file = open('commands.txt','r')
        for line in commands_file:
            line_list=list(line.split(";"))
            command_list[line_list[0]]={'index':int(line_list[1]),'help':line_list[2],'error':line_list[3]}
        commands_file.close()
    except:
        print("Unable to load commands.txt")

def input_text_builder(added_text=''):
    """Construct the text for the prompt"""
    global input_text
    input_text = input_text_default
    if added_text != '':
        input_text += '\\' + added_text
    input_text += input_prompt

def split_command(raw_input):
    """Split command line as it should be"""
    strip_raw_input = raw_input.strip()
    temp_string = ''
    quote_flag = False
    quote_chars = ['\"','\'']
    command = []
    
    for char in strip_raw_input:
        if char == ' ' and quote_flag == False:
            temp_string = temp_string.strip('\"')
            temp_string = temp_string.strip('\'')
            command.append(temp_string)
            temp_string = ''
        elif char == ' ' and quote_flag == True:
            temp_string += char
        elif char in quote_chars:
            quote_flag = not quote_flag
            temp_string += char
        else:
            temp_string += char

    temp_string = temp_string.strip('\"')
    temp_string = temp_string.strip('\'')
    command.append(temp_string)
    return command

def clear_screen():
    """Clear the console screen"""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def print_version():
    """Show current A2LReader version"""
    print('A2LReader version v{}'.format(version))

def help_a2l(command):
    """Show help text for a specific A2LReader command"""
    if len(command)<2:
        print('Help for A2LReader for Python - type help <command> for information about a specific command.')
    else:
        help_text = command_list.get(command[1],{}).get('help')
        if help_text != None:
            print(help_text)
        else:
            print('{} is not a valid command'.format(command[1]))

def open_a2l(file_name):
    """Open a A2L file"""
    try:
        a2l_file = a2l_stream(file_name, encoding)
        a2l_basename = os.path.basename(file_name)

        print('Please wait while loading',a2l_basename)
        global elements_dict, elements_list
        elements_list.clear()
        for e in elements_dict:
            elements_list[e] = {}
        while True:
            if a2l_file.read() == True:
                if a2l_file.node_type == a2l_nodetype.Element:
                    if a2l_file.name in elements_dict:
                        element_type = a2l_file.name
                        a2l_file.read()
                        element_name = a2l_file.node_value
                        elements_list[element_type][element_name] = {}
                        for e in elements_dict[element_type]:
                            a2l_file.read()
                            elements_list[element_type][element_name][e] = a2l_file.node_value
            else:
                break
        input_text_builder(a2l_basename)
        print(a2l_basename,'successfully loaded.')
        a2l_file.close()
    except:
        print('An error occured while loading {}.'.format(a2l_basename))

def a2l_filter(list_filter, filter_string):
    """Allows to filter a list of parameters in the style of INCA, using * as wildcard"""
    list_filter_string = filter_string.split('*')
    filtered_list = []
    for e in list_filter:
        e_lower = e.lower()
        found_pos = e_lower.find(list_filter_string[0].lower())
        if found_pos == 0:
            if len(list_filter_string) > 1:
                start_pos = len(list_filter_string[0])
                for fil_sub in list_filter_string[1:]:
                    found_pos = e_lower.find(fil_sub.lower(), start_pos)
                    if found_pos ==-1:
                        break
                    else:
                        start_pos += found_pos
                else:
                    filtered_list.append(e)
            else:
                filtered_list.append(e)
    return filtered_list



#main
ini_global_vars()
load_a2l_dictionary()
load_commands()
input_text_builder()
clear_screen()
print()
print_version()
print("Type clist to get the list of commands available,")
print("or exit to return to the command prompt.")
print()
while True:
    raw_input=input(input_text)
    command = split_command(raw_input)
    if command[0]!= '':
        i = command_list.get(command[0].lower(),{}).get('index')
        if i != None:
            if i==0:
                break
            elif i==1:
                help_a2l(command)
            elif i==2:
                if len(command)<2:
                    print(command_list.get(command[0].lower(),{}).get('error'))
                else:
                    if command[1] == '/gui':
                        a2l_window = Tk()
                        a2l_window.withdraw() # hide the background window in Tkinter to leave only the openfiledialog
                        a2l_file = filedialog.askopenfilename(title='Select a A2L file', filetypes=(("A2L file","*.a2l"),("All files","*.*")))
                        if a2l_file != '':
                            #profile = cProfile.Profile()
                            #profile.runctx('open_a2l(x)',{'x':a2l_file,'open_a2l':open_a2l},{})
                            #ps = pstats.Stats(profile)
                            #ps.print_stats()
                            open_a2l(a2l_file)
                        a2l_window.destroy()
                    else:
                        open_a2l(command[1])
            elif i==3:
                print('Commands available :')
                ord_list = list(command_list.keys())
                ord_list.sort()
                for key in ord_list:
                    print(key)
            elif i==4:
                print_version()
                #print(print_version.__doc__)
            elif i==5:
                clear_screen()
            elif i==6:
                a2l_window = Tk()
                a2l_window.title("A2LReader test window")
                a2l_window.geometry("500x400")
                label_test = Label(a2l_window,text="A2LReader graphical user interface test")
                button_test = Button(a2l_window,text="Close")
                label_test.grid(row=0,column=0)
                button_test.grid(row=1,column=0)
            elif i==7:
                text_param = 'CHARACTERISTIC'
                if command[0].lower() == 'meas':
                    text_param = 'MEASUREMENT'
                if len(command)<2:
                    print("List of labels inside A2L file:\n")
                    for label in sorted(elements_list[text_param]):
                        print(label,elements_list[text_param][label]['address'],sep=' - ')
                    print("\nNumber of labels:", len(elements_list[text_param]))
                else:
                    if command[1] == '/count':
                        print("Number of labels:", len(elements_list[text_param]))
                    elif command[1] == '/export':
                        if len(command)>2:
                            file_lab = open(command[2],"w")
                            file_lab.write("[LABEL]\n")
                            for label in elements_list[text_param]:
                                file_lab.write(label+'\n')
                            file_lab.close()
                    else:
                        filtered_labels = a2l_filter(elements_list[text_param].keys(),command[1])
                        print("List of labels inside A2L file with filter {}:\n".format(command[1]))
                        for label in sorted(filtered_labels):
                            print(label,elements_list[text_param][label]['description'],sep=' - ')
                        print("\nNumber of labels:", len(filtered_labels))
            elif i==8:
                if len(command)<2:
                    print("The current encoding is", encoding)
                else:
                    encoding = command[1]
                
        else:
            print('{} is not a valid command. Type clist to get the list of commands.'.format(command[0]))
        print()
