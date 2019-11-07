import re
from functools import reduce


class MySyntaxException(Exception): pass


def error(message, reason=None):
    print(message)
    raise MySyntaxException()


def extract_symbols(text):
    return list(filter(lambda x: text.count(x), SYMBOLS))


def extract_parts(text):
    return list(filter(lambda x: text.count(x), PARTS))


def is_service(text):
    return text in ['int', 'void', 'float', 'while', 'do', 'auto', 'double', 'goto', 'static', 'union', 'restrict',
                     'if', 'then', 'else', 'switch', 'case', 'char', 'enum', 'long', 'struct', 'unsigned',
                     'break', 'default', 'repeat', 'begin', 'const', 'extern', 'register', 'typedef', 'inline',
                     'end', 'until', 'return', 'sizeof', 'continue', 'for', 'short', 'signed', 'volatile']


def my_print(data, label):
    print(f'{label}: {", ".join(sorted(list(data)))}')


def analyse(source):
    try:
        symbols, services, variables, nums = {';'}, set(), set(), set()

        lines = map(lambda x: x.strip(), source.split(';'))
        for line in filter(lambda x: x, lines):
            _symbols = extract_symbols(line)
            symbols.update(_symbols)
            pre_operants = [line]
            for symb in _symbols:
                pre_operants = reduce(lambda a, b: a + b, [i.split(symb) for i in pre_operants])
            
            for pre_operant in filter(lambda x: x, pre_operants):
                _parts = extract_parts(pre_operant)
                symbols.update(_parts)
                operants = [pre_operant]
                for part in _parts:
                    operants = reduce(lambda a, b: a + b, [i.split(part) for i in operants])
                
                for operant in filter(lambda x: x, operants):
                    for piece in operant.split():
                        if is_service(piece):
                            services.add(piece)
                        elif piece.isdigit() or re.fullmatch(r'\d+\.\d+', piece):
                            nums.add(piece)
                        elif re.fullmatch(r'[a-zA-Z_]+[\w]*', piece):
                            variables.add(piece)
                        else:
                            error('Error!')
        
        print(f'Input was: {source}')
        my_print(symbols, 'Symbols')
        my_print(services, 'Service words')
        my_print(variables, 'Variables')
        my_print(nums, 'Numbers')
    except MySyntaxException:
        pass


SYMBOLS = ['...', ',', '!=', '==', '?', '<>', '^', '>>', '<<', '|=', '&&',
               '[', ']', '(', ')', '*', '!', '\'', '+=', '-=', '^=', '||',
               '{', '}', ':', '/', '\\', '*=', '/=', '<<=', '->', '<=',
               '--', '++', ':=', '"', '#', '%', '~', '%=', '&=', '>>=', '>=']

PARTS = ['>', '<', '+', '-', '=', '&', '|']


if __name__ == '__main__':
    analyse(r'switch(c){case 0: b&=a[n]; break; default: b|=(d >= 3)||(c < _myfunc(n));}')
