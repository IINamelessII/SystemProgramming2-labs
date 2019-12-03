import re
from functools import reduce


class MyException(Exception): pass


def error(message='Error!', reason=None):
    print(message)
    # print('OK')
    raise MyException()


def extract_symbols(text):
    return list(filter(lambda x: text.count(x), SYMBOLS))


def extract_parts(text):
    return list(filter(lambda x: text.count(x), PARTS))


def is_service(text):
    return text in ['int', 'void', 'float', 'while', 'do', 'auto', 'double', 'goto', 'static', 'union', 'restrict',
                     'if', 'then', 'else', 'switch', 'case', 'char', 'enum', 'long', 'struct', 'unsigned',
                     'break', 'default', 'repeat', 'begin', 'const', 'extern', 'register', 'typedef', 'inline',
                     'end', 'until', 'return', 'sizeof', 'continue', 'for', 'short', 'signed', 'volatile']


def index(s, subs, skip=0):
    try:
        return s.index(subs, skip)
    except ValueError:
        return 99999


def closing_index(s, opening):
    open_count = 0
    for i in range(len(s)):
        open_count += s[i] == opening
        open_count -= s[i] == BRACKETS[opening]
        if open_count < 0:
            return i
    return 99999


def check(text):
    if sum(map(lambda x: text.count(x), r'=;{}')):
        error()
    check_scopes(text)


def check_square(text):
    if sum(map(lambda x: text.count(x), r'=;')):
        error()
    check_scopes(text)


def check_figure(text):
    if text.count(';') < text.count('='):
        error()
    check_scopes(text)


def check_scopes(text):
    first = min(map(lambda x: index(text, x), '([{')) #Index of first opening bracket

    if sum(map(lambda x: text[:first].count(x), ')]}')): #If we met closing bracket before first opening
        error()
    
    if first < 99999:
        closing = closing_index(text[first + 1:], text[first]) + first + 1
        if text[first] == '[' and closing == first + 1: #If empty []
            error()

        analyse(text[:first])

        if text[first] == '(':
            check(text[first + 1:closing])
        elif text[first] == '[':
            check_square(text[first + 1:closing])
        else:
            check_figure(text[first + 1:closing])

        check_scopes(text[closing + 1:])
    else:
        analyse(text)


def main_check(source):
    print(f'Input was: {source}')
    if source.endswith('  '):
        print('Error!')
        return
    elif source.endswith(' '):
        print('OK')
        return
    
    try:
        if source.count('(') != source.count(')') or source.count('{') != source.count('}') or source.count('[') != source.count(']'):
            error()
        
        check_figure(source)
    except MyException:
       pass
    else:
        print('OK')
        # print('Error!')



def analyse(source):
    lines = map(lambda x: x.strip(), source.split(';'))
    for line in filter(lambda x: x, lines):
        _symbols = extract_symbols(line)
        pre_operants = [line]
        for symb in _symbols:
            pre_operants = reduce(lambda a, b: a + b, [i.split(symb) for i in pre_operants])
        
        for pre_operant in filter(lambda x: x, pre_operants):
            _parts = extract_parts(pre_operant)
            operants = [pre_operant]
            for part in _parts:
                operants = reduce(lambda a, b: a + b, [i.split(part) for i in operants])
            
            for operant in filter(lambda x: x, operants):
                for piece in operant.split():
                    if is_service(piece):
                        pass
                    elif piece.isdigit() or re.fullmatch(r'\d+\.\d+', piece):
                        pass
                    elif re.fullmatch(r'[a-zA-Z_]+[\w]*', piece):
                        pass
                    else:
                        error('Error!')
      

SYMBOLS = ['...', ',', '!=', '==', '?', '<>', '^', '>>', '<<', '|=', '&&',
               '*', '!', '\'', '+=', '-=', '^=', '||',
               ':', '/', '\\', '*=', '/=', '<<=', '->', '<=',
               '--', '++', ':=', '"', '#', '%', '~', '%=', '&=', '>>=', '>=']

PARTS = ['>', '<', '+', '-', '=', '&', '|']


BRACKETS = {'(': ')', '[': ']', '{': '}'}


if __name__ == '__main__':
    main_check(r'b=ca; b=sn[s2a]; b=2*a;')
