from functools import wraps


class Util(object):
    '''
        Utilities class for helper classes in this module
    '''

    @staticmethod
    def doDouble(value: str) -> float:
        '''
            parses a string to float

            params:
                value: str

            returns: float
        '''
        newValue = '.'.join([value[:-2], value[-2:]])
        return float(newValue)

    @staticmethod
    def validateTrama(trama: str, length: int) -> list:
        '''
            validate trama arg type and the given length
            should be gte

            params:
                trama: str
                length: int

            returns: bool
        '''
        return trama != None and len(trama) >= length

    @staticmethod
    def doAllDouble(collection: list) -> list:
        '''
            given a collection it will parse all the str items
            to respective double value

            params:
                collection: [str]

            returns: [float]
        '''
        return [*map(Util.doDouble, collection)]

    @staticmethod
    def tramaValidator(length: int = 0) -> object:
        '''
            it secures the class instance and validates
            the trama args to have the indicated length

            params:
                length: int
        '''
        def classDecorator(originalClass):
            wraps(originalClass)

            def decorateClass(trama):
                try:
                    if Util.validateTrama(trama, length):
                        return originalClass(trama)
                    else:
                        return 
                except Exception as e:
                    return
            return decorateClass
        return classDecorator

    @staticmethod
    def splitAndExpectLength(trama: str, expectedLength: int, splitChar: str = chr(0x0A)) -> list:
        '''
            split a str in the given character and validates the
            expected length, if fails raises Exception

            params:
                trama: str
                expectedLength: int
                splitChain: str = "chr(0x0A)"

            return [str]
        '''
        splitedText = trama.split(splitChar) if type(trama) == str else []
        if len(splitedText) >= expectedLength:
            return splitedText
        raise Exception('no enough params in trama chain')

    @staticmethod
    def splitExpectAndDoDouble(*args, **kwargs) -> list:
        '''
            wrap the splitAndExpectLength and the doAllDouble methods
            same params as splitAndExpectLength
            same return as doAllDouble
        '''
        collection = Util.splitAndExpectLength(*args, **kwargs)
        return Util.doAllDouble(collection)
