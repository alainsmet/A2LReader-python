#!/usr/bin/env python3
import enum
import pdb

class a2l_nodetype(enum.Enum):
    Empty = 1
    Element = 2
    Text = 3
    Comment = 4
    A2LDeclaration = 5
    EndElement = 6
    Whitespace = 7
    
class a2l_stream:
    
    start_tag = '/begin'
    end_tag = '/end'
    void_chars = [' ','\n','\t','\r']
    
    def __init__(self, file_path='', encoding='latin-1', white_space=False):
        """Initialise the A2L StreamReader"""
        self.base_uri = file_path
        if file_path != '':
            self.a2l_file = open(self.base_uri,'rb')
        self.name = ''
        self.node_type = a2l_nodetype.Empty
        self.node_value = ''
        self.return_white_space = white_space
        self.encoding = encoding
        self.stored_char = ''

    def __str__(self):
        return f'Name: {self.name}\nNode type: {self.node_type}\nNode value: {self.node_value}'

    def peek(self):
        #try:
            #next_char = unicode(self.a2l_file.peek(1)[:1],self.encoding)
        next_char = self.a2l_file.peek(1)[:1].decode(self.encoding)
        if next_char == '':
            next_char = None
        #except:
        #    next_char = None
        return next_char

    def readchar(self):
        #try:
            #char = unicode(self.a2l_file.read(1),self.encoding)
        char = self.a2l_file.read(1).decode(self.encoding)
        if char == '':
            char = None
        #except:
        #    char = None
        return char
        
    def close(self):
        self.a2l_file.close()

    def read(self):
        next_char = ''
        read_char = self.stored_char
        string_read = ''
        self.node_type = a2l_nodetype.Empty
        self.name = ''
        self.node_value = ''

        while True:
            if read_char == '':
                read_char = self.readchar()
            read_next_char_flag = False
            if read_char != None:
                if read_char in self.void_chars and self.node_type != a2l_nodetype.Comment:
                    if len(string_read) == 0:
                        self.node_type = a2l_nodetype.Whitespace
                        string_read += read_char
                        while True:
                            read_char = self.readchar()
                            if not read_char in self.void_chars and read_char != None:
                                if self.return_white_space == True:
                                    self.node_value = string_read
                                    self.stored_char = read_char
                                    return True
                                else:
                                    string_read = ''
                                    self.node_type = a2l_nodetype.Empty
                                    self.name = ''
                                    self.stored_char = read_char
                                    read_next_char_flag = False
                                    break
                            else:
                                if read_char == None:
                                    return False
                                else:
                                    string_read += read_char
                    else:
                        self.node_value = string_read
                        self.stored_char = read_char
                        return True
                else:
                    string_read += read_char
                    if string_read == '/*' or string_read == '//':
                        self.node_type = a2l_nodetype.Comment
                        if string_read == '/*':
                            while True:
                                read_char = self.readchar()
                                string_read += read_char
                                if string_read[-2:] == '*/':
                                    self.node_value = string_read
                                    self.stored_char = self.readchar()
                                    return True
                        else:
                            while True:
                                read_char = self.readchar()
                                string_read += read_char
                                if string_read[-1] == '\n':
                                    self.node_value = string_read[0:-1]
                                    self.stored_char = read_char
                                    return True
                        read_next_char_flag = True
                    elif string_read == self.start_tag or string_read == self.end_tag:
                        next_char = self.readchar()
                        if next_char in self.void_chars:
                            if string_read == self.start_tag:
                                self.node_type = a2l_nodetype.Element
                            else:
                                self.node_type = a2l_nodetype.EndElement
                            self.stored_char = ''
                            new_a2lstream = self
                            while new_a2lstream.node_type != a2l_nodetype.Text:
                                new_a2lstream.read()
                            self.name = new_a2lstream.node_value
                            self.node_value = string_read
                            if string_read == self.start_tag:
                                self.node_type = a2l_nodetype.Element
                            else:
                                self.node_type = a2l_nodetype.EndElement
                            return True
                        else:
                            string_read += next_char
                            read_next_char_flag = True
                    elif string_read == '"':
                        self.node_type = a2l_nodetype.Text
                        while True:
                            read_char = self.readchar()
                            string_read += read_char
                            if read_char == '"':
                                if string_read[-2:-1] != '\\':
                                    string_read = string_read[1:-1]
                                    string_read = string_read.replace('""','"')
                                    string_read = string_read.replace('\\"','"')
                                    self.node_value = string_read
                                    self.stored_char = self.readchar()
                                    return True
                    else:
                        self.node_type = a2l_nodetype.Text
                        read_next_char_flag = True
                            
                if read_next_char_flag == True:           
                    read_char = self.readchar()
            else:
                return False

    def debug(self,iter=10):
        """Output the values parsed for debugging purpose"""
        print("Debugger mode for A2LStreamReader. Type exit to end the debugging mode.")
        print(' '*7 +' - Node value - Node type')
        print('='*71)
        print()
        increment = 0
        while True:
            for i in range(iter):
                self.read()
                print(str(increment).ljust(7),self.node_value,self.name,self.node_type,sep=' - ')
                increment += 1
            debug_input = input("> ")
            if debug_input == 'exit':
                break

    def debug_full(self,param):
        """Output the values parsed for debugging purpose"""
        print("Debugger mode for A2LStreamReader. Type exit to end the debugging mode.")
        print(' '*7 +' - Node value - Node type')
        print('='*71)
        print()
        increment = 0
        while True:
            while True:
                self.read()
                if self.node_value == param:
                    print(str(increment).ljust(7),self.node_value,self.name,self.node_type,sep=' - ')
                    break
                increment += 1
            self.read()
            print(str(increment).ljust(7),self.node_value,self.name,self.node_type,sep=' - ')
            increment += 1
            debug_input = input("> ")
            if debug_input == 'exit':
                break



