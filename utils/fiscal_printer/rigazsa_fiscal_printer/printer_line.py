class PrinterLine(object):
    '''
        Line formatter helper
    '''
    def __init__(self, 
            sequence=chr(0x20), 
            command='', 
            fields={}, 
            parent=None, 
            limit:int=0,
            separator_ends=False
        ):
        self.sequence = sequence
        self.command = command
        self.fields = fields
        self._parent = parent
        self._limit = limit + 1 if limit else limit
        self.separator_ends = separator_ends

    @property
    def last_index(self) -> int:
        '''Get the max index of the fields'''
        return max(self.fields.keys())
    
    @property
    def next_index(self) -> int:
        '''Get next index over the max'''
        return self.last_index + 1

    @staticmethod
    def format_plain_fields(fields:list = [], limit:int=0) -> dict:
        '''Cast a given list of arguments to formatted fields'''
        return { 
            index + 1: fields[index]  
            for index in range(limit + 1 if limit else len(fields))
        }

    def send(self, *args, **kwargs) -> None:
        '''Send to the fiscal printer Queue'''
        self._parent.printer.SendCmd(self.join(*args, **kwargs))

    def add(self, command:str='', key:int=0) -> None:
        '''Add new command to the queue, raise if receive a index over the limit'''
        if key == 0:
            key = self.next_index
        
        if self._limit and key >= self._limit:
            raise ValueError("Adding values over the limit")

        self.fields.update({
            key: command
        })

    def validate_fields(self) -> None:
        '''Parse to a formatted dict if necessary'''
        if type(self.fields) == list:
            self.fields = PrinterLine.format_plain_fields(fields=self.fields)

        if self.fields:
            return [
                self.fields.get(index, '') 
                for index in range(1, self._limit or self.next_index)
            ]
        else:
            return ['']

    def join(self, separator=chr(0x1C)) -> str:
        '''Join al the command to send to the fiscal printer'''
        
        return self.sequence + self.command + separator \
            + separator.join(self.validate_fields()) \
            + (separator if self.separator_ends else '')
