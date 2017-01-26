"""This module provides an interface to run ngspice in server mode and get back the simulation
output.

When ngspice runs in server mode, it writes on the standard output an header and then the simulation
output in binary format.  At the end of the simulation, it writes on the standard error a line of
the form:

    .. code::

        @@@ \d+ \d+

where the second number is the number of points of the simulation.  Due to the iterative and
adaptive nature of a transient simulation, the number of points is only known at the end.

Any line starting with "Error" in the standard output indicates an error in the simulation process.
The line "run simulation(s) aborted" in the standard error indicates the simulation aborted.

Any line starting with *Warning* in the standard error indicates non critical error in the
simulation process.

"""

####################################################################################################

import logging
import re
import os
import numpy as np

####################################################################################################

from PySpice.Spice.RawFile import RawFile, Variable
from PySpice.Spice.Server import SpiceServer

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class LtSpiceServerXVII(SpiceServer):

    """This class wraps the execution of ngspice in server mode and convert the output to a Python data
    structure.

    Example of usage::

      spice_server = SpiceServer(spice_command='/path/to/ngspice')
      raw_file = spice_server(spice_input)

    It returns a :obj:`PySpice.Spice.RawFile` instance.

    """

    _logger = _module_logger.getChild('LTSpiceServer')

    ##############################################
    def __init__(self, spice_command='XVIIx64.exe'): 
      
        self._spice_command = spice_command

    def _parse_log(self, logName):

        """Parse logfile for warnings and return the number of points."""

         #Read in log file and check for errors
        file = open(logName,"r")
        log_lines = file.readlines()
        
        for line in log_lines:               
            if 'Warning' in line:
                self._logger.warning(line[len('Warning :'):])
            elif "Error" in line:
                raise NameError("Simulation aborted\n" + line)
        file.close()
    def _decode_number_of_points(self, line):

        """Decode the number of points in the given line."""

        match = re.match(r'No. Points: +(\d+)', line)
        if match is not None:
            return int(match.group(1))
        else:
            raise NameError("Cannot decode the number of points")

    def _parse_stdout(self, stdout):

        """Parse stdout for errors."""

        # self._logger.debug('\n' + stdout)
        number_of_points = None
        error_found = False
        # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc0 in position 870: invalid start byte
        # lines = stdout.decode('utf-8').splitlines()
        lines = stdout.splitlines()
        for line_index, line in enumerate(lines):
            #print(line)
            if line.startswith(b'\x00'):
                line = line[1:]
            #print(line.decode('utf-16'))
            line = line.decode('utf-16').encode('utf-8')
            if line.startswith(b'Error '):
                error_found = True
                self._logger.error('\n' + line.decode('utf-8') + '\n' + lines[line_index+1].decode('utf-8'))
            if line.startswith(b'No. Points:'):
                number_of_points = self._decode_number_of_points(line.decode('utf-8'))
            if line.startswith(b'Binary:'):
                break 
        if error_found:
            raise NameError("Errors was found by Spice")
        return number_of_points
    ############################################## 
    def __call__(self, spice_input):

        """Run SPICE in server mode as a subprocess for the given input and return a
        :obj:`PySpice.RawFile.RawFile` instance.

        """

        self._logger.info("Start the ltspice subprocess")
        
        file= open('temp.net','w')
        file.write(str(spice_input))
        file.close()

        #command = "{} -b -ascii {}".format(self._spice_command,'temp.net')
        command = "{} -b {}".format(self._spice_command,'temp.net')
        self._logger.info("Command is "+command)
        os.system(command)

        self._parse_log('temp.log')

        file = open ('temp.raw','rb')
        stdout = file.read()
        number_of_points =self._parse_stdout(stdout)
                
        if number_of_points is None:
            raise NameError("The number of points was not found in the standard error buffer,"
                            " ngspice returned:\n" +
                            stdout)
        
        return LtRawFile(stdout, number_of_points)

class LtRawFile(RawFile):
     def __init__(self, stdout, number_of_points):
         super().__init__(stdout, number_of_points)
     def _read_header(self, stdout):

        """ Parse the header """
        
        binary_line = 'Binary:\n'.encode('utf-16')
        binary_line = binary_line[2:]
        binary_location = stdout.find(binary_line)
        if binary_location < 0:
            raise NameError('Cannot locate binary data')
        raw_data_start = binary_location + len(binary_line)
        # self._logger.debug('\n' + stdout[:raw_data_start].decode('utf-8'))
        header_lines = stdout[:binary_location].decode('utf-16').encode('utf-8').splitlines()
        raw_data = stdout[raw_data_start:]
        header_line_iterator = iter(header_lines)
        
        ##Todo esto esta en el .log PDTE
        #self.circuit = self._read_header_field_line(header_line_iterator, 'Circuit')
        #self.temperature = self._read_header_line(header_line_iterator, 'Doing analysis at TEMP')
        #self.warnings = [self._read_header_field_line(header_line_iterator, 'Warning')
        #                 for i in range(stdout.count(b'Warning'))]
        #for warning in self.warnings:
        #    self._logger.warn(warning)

        self.title = self._read_header_field_line(header_line_iterator, 'Title')
        self.date = self._read_header_field_line(header_line_iterator, 'Date')
        self.plot_name = self._read_header_field_line(header_line_iterator, 'Plotname')
        self.flags = self._read_header_field_line(header_line_iterator, 'Flags')
        self.number_of_variables = int(self._read_header_field_line(header_line_iterator, 'No. Variables'))
        self._read_header_field_line(header_line_iterator, 'No. Points')
        self._read_header_field_line(header_line_iterator, 'Offset')
        self._read_header_field_line(header_line_iterator, 'Command')
        self._read_header_field_line(header_line_iterator, 'Variables', has_value=False)
        
        self.variables = {}
        for i in range(self.number_of_variables):
            line = (next(header_line_iterator)).decode('utf-8')
            self._logger.debug(line)
            items = [x.strip() for x in line.split('\t') if x]
            # 0 frequency frequency grid=3
            index, name, unit = items[:3]
            name=str(name).lower()
            self.variables[name] = Variable(index, name, unit)
        # self._read_header_field_line(header_line_iterator, 'Binary', has_value=False)
        
        return raw_data
    
     def _read_variable_data(self, raw_data):

        """ Read the raw data and set the variable values. """

        if('real' in self.flags):
            number_of_columns = self.number_of_variables
        elif('complex' in self.flags):
            number_of_columns = 2*self.number_of_variables
        else:
            raise NotImplementedError

        if('Transient' in self.plot_name): #Tran
            number_of_columns = self.number_of_variables+1
            input_data = np.fromstring(raw_data, count=number_of_columns*self.number_of_points, dtype='float32')
            input_data = input_data.reshape((self.number_of_points, number_of_columns))
            input_data = input_data.transpose()
            time = input_data [0:2]
            tmpdata= time.transpose().flatten().tostring()
            time=np.fromstring(tmpdata, count=self.number_of_points, dtype='float64')
            time=np.absolute(time)
            input_data = input_data [1:]
            input_data[0]=time
        else:
            input_data = np.fromstring(raw_data, count=number_of_columns*self.number_of_points, dtype='float64')
            input_data = input_data.reshape((self.number_of_points, number_of_columns))
            input_data = input_data.transpose()
        #input_data = input_data [1:]
        #np.savetxt('raw.txt', input_data)
        if 'complex' in self.flags:
            raw_data = input_data
            input_data = np.array(raw_data[0::2], dtype='complex64')
            input_data.imag = raw_data[1::2]
        for variable in self.variables.values():
            variable.data = input_data[variable.index]

     def _read_variable_data_assci(self, raw_data):

        """ Read the raw data and set the variable values. """

        if('real' in self.flags):
            number_of_columns = self.number_of_variables+1
        elif('complex' in self.flags):
            number_of_columns = 2*self.number_of_variables+1
        else:
            raise NotImplementedError
        print (np.version.version)
        tmpdata=raw_data.replace(b'\r\n',b'\t')
        tmpdata=tmpdata.replace(b'\t\t',b'\t')
        tmpdata=tmpdata.replace(b',',b'\t')

        input_data = np.fromstring(tmpdata.decode('utf-8'), count=number_of_columns*self.number_of_points, dtype='f8',sep='\t')
        input_data = input_data.reshape((self.number_of_points, number_of_columns))
        input_data = input_data.transpose()
        input_data = input_data [1:]
        np.savetxt('raw.txt', input_data)
        if 'complex' in self.flags:
            raw_data = input_data
            input_data = np.array(raw_data[0::2], dtype='complex64')
            input_data.imag = raw_data[1::2]
        for variable in self.variables.values():
            variable.data = input_data[variable.index]

#"c:\\Program Files (x86)\\LTC\\LTspiceIV\\scad3.exe"
# c:\\tmp\\EWB\\LTSpcieIV\\scad3.exe
def enableLtSpiceServerXVII(simulator, spice_command='"c:\\Program Files\\LTC\\LTspiceXVII\\XVIIx64.exe"'):
    simulator._options.pop('filetype')
    simulator._options.pop('NOINIT')
    simulator._spice_server= LtSpiceServerXVII(spice_command=spice_command)