#!/usr/bin/env python3
import enum

class hex_recordtype(enum.Enum):
    Empty = 1
    Header = 2
    Data = 3
    Reserved = 4
    Count = 5
    StartAddress = 6
    StartSegmentAddress = 7
    StartLinearAddress = 8
    ExtendedSegmentAddress = 9
    ExtendedLinearAddress = 10

class hex_filetype(enum.Enum):
    Empty = 1
    SRecord = 2
    IntelHex = 3
  
class hex_stream:

    def __init__(self, file_path=''):
        self.base_uri = file_path
        if file_path != '':
            self.hex_file = open(self.base_uri,'r')
        self.read()

    def __str__(self):
        return f'Record type: {self.record_type}\nByte count: {self.byte_count}\nAddress: {self.address}\nData: {self.data}\nChecksum: {self.checksum}'
    
    def readline(self):
        return self.hex_file.readline().strip()
    
    def get_file_type(self, line=''):
        if line == '':
            return hex_filetype.Empty
        elif line[:2] in ['S' + str(x) for x in range(10)]:
            return hex_filetype.SRecord
        elif line[0] == ':':
            return hex_filetype.IntelHex
        else:
            return hex_filetype.Empty

    def get_hex_recordtype(self, line=''):
        if self.hex_type == hex_filetype.SRecord:
            if line[:2] == 'S0':
                return hex_recordtype.Header
            elif line[:2] in ['S' + str(x) for x in range(1,4)]:
                return hex_recordtype.Data
            elif line[:2] == 'S4':
                return hex_recordtype.Reserved
            elif line[:2] in ['S5', 'S6']:
                return hex_recordtype.Count
            elif line[:2] in ['S' + str(x) for x in range(7,10)]:
                return hex_recordtype.StartAddress
            else:
                return hex_recordtype.Empty
        elif self.hex_type == hex_filetype.IntelHex:
            pass
        else:
            return hex_recordtype.Empty

    def get_hex_bytecount(self, line=''):
        if self.hex_type != hex_filetype.Empty:
            line_list = self.line_split(line)
            return int('0x'+line_list[1],16)
        else:
            return ''
        
    def get_hex_address_length(self, line=''):
        line_list = self.line_split(line)
        if self.hex_type == hex_filetype.IntelHex:
            return 2
        else:
            if line_list[0] in ['S0','S1','S5','S9']:
                return 2
            elif line_list[0] in ['S2','S6','S8']:
                return 3
            elif line_list[0] in ['S3','S7']:
                return 4
            else:
                return ''

    def get_hex_datacount(self, line=''):
        if line == '':
            pass
        line_list = self.line_split(line)
        if self.hex_type == hex_filetype.IntelHex:
            return self.get_hex_bytecount(line)
        else:
            address_length = self.get_hex_address_length(line)
            return self.get_hex_bytecount(line) - address_length - 1

    def get_hex_address(self, line=''):
        line_list = self.line_split(line)
        address_length = self.get_hex_address_length(line)
        return ''.join(line_list[2:2+address_length])

    def get_hex_data(self, line=''):
        line_list = self.line_split(line)
        data_count = self.get_hex_datacount(line)
        if self.hex_type == hex_filetype.IntelHex:
            return ''.join(line_list[5:5+data_count])
        else:
            address_length = self.get_hex_address_length(line)
            start_position = 2 + address_length
            return ''.join(line_list[start_position:start_position+data_count])

    def get_hex_checksum(self, line=''):
        line_list = self.line_split(line)
        return line_list[-1]
    
    def close(self):
        self.hex_file.close()

    def ones_complement(self, bin_value):
        out_value = '0b'
        for c in bin_value[2:].rjust(8,'0'):
            if c == '0':
                out_value += '1'
            else:
                out_value += '0'
        return out_value

    def twos_complement(self, bin_value):
        out_value = '0b'
        first_one_flag = False
        reversed_value = ''
        for c in bin_value[::-1][:-2].ljust(8,'0'):
            if c == '1' and first_one_flag == False:
                first_one_flag = True
                reversed_value += c
            elif first_one_flag == False:
                reversed_value += c
            elif first_one_flag == True:
                if c == '0':
                    reversed_value += '1'
                else:
                    reversed_value += '0'
        out_value += reversed_value[::-1]
        return out_value

    def line_split(self, line=''):
        if line == '' or len(line) < 2:
            return line
        elif self.hex_type == hex_filetype.IntelHex:
            line = line[1:]
            return [':']+[line[x:x+2] for x in range(0,len(line),2)]
        else:
            return [line[x:x+2] for x in range(0,len(line),2)]
                
    def checksum_calc(self, line=''):
        if self.hex_type == hex_filetype.SRecord:
            line_list = self.line_split(line)
            sum_data = 0
            for n in line_list[1:-1]:
                sum_data += int('0x'+ n,16)
            sum_hex = '0x' + hex(sum_data)[-2:]
            return hex(int(self.ones_complement(bin(int(sum_hex,16))),2))
        else:
            line_list = self.line_split(line)
            sum_data = 0
            for n in line_list[1:-1]:
                sum_data += int('0x'+ n,16)
            sum_hex = '0x' + hex(sum_data)[-2:]
            return hex(int(self.twos_complement(bin(int(sum_hex,16))),2))

    def read(self):
        try:
            self.line = self.readline()
            self.hex_type = self.get_file_type(self.line)
            self.line_list = self.line_split(self.line)
            self.record_type = self.get_hex_recordtype(self.line)
            self.byte_count = self.get_hex_bytecount(self.line)
            self.address = self.get_hex_address(self.line)
            self.data = self.get_hex_data(self.line)
            self.checksum = self.get_hex_checksum(self.line)
            return True
        except:
            return False
