import re
from functools import reduce


def find_symbols(text):
    symbols = ['...', ',', '!=', '==', '?', '<>', '^', '>>', '<<', '|=', '&&',
               '[', ']', '(', ')', '*', '!', '\'', '_', '+=', '-=', '^=', '||',
               '{', '}', ':', ';', '.', '/', '\\', '*=', '/=', '<<=', '->', '<=',
               '--', '++', ':=', '"', '#', '%', '~', '%=', '&=', '>>=', '>=']
    return reduce(lambda a, x: a + x, [[i] * text.count(i) for i in symbols])


def find_parts(text):
    return reduce(lambda a, x: a + x, [[i] * text.count(i) for i in ['>', '<', '+', '-', '=', '.', '&', '|']])


def is_service(text):
    return text in ['int', 'void', 'float', 'while', 'do', 'auto', 'double', 'goto', 'static', 'union', 'restrict',
                     'if', 'then', 'else', 'switch', 'case', 'char', 'enum', 'long', 'struct', 'unsigned',
                     'break', 'default', 'repeat', 'begin', 'const', 'extern', 'register', 'typedef', 'inline',
                     'end', 'until', 'return', 'sizeof', 'continue', 'for', 'short', 'signed', 'volatile']


def compile_text(text):
    print(f'Input: {text}')

    if re.search('[а-яА-ЯёЁ]+', text) or re.search(r'[0-9]+[a-zA-Z]+', text):
        return print('Input has mistakes.')
    else:

        text_num = re.findall(r'[0-9]+\.[0-9]+', text) #floats
        for i in text_num:
            if not (re.search(r'[a-zA-Z]' + i ,text)):
                text = text.replace(i, '')
                
        text_num += re.findall(r'[0-9]+', text) #ints
        for i in text_num:
            if not (re.search(r'[a-zA-Z]' + i ,text)):
                text = text.replace(i, '')

        text_symb = find_symbols(text) #symbols except + - = < > . & |
        for i in text_symb:
            text = text.replace(i, ' ')
        
        parts = find_parts(text) #+ - = < > . & |
        for i in parts:
            text = text.replace(i, ' ')

        text_serv = list(filter(lambda x: is_service(x), text.split())) #service words
        text = list(filter(lambda x: not is_service(x), text.split()))

        text_var = sorted(list(set(text))) #variables
        text_var = list(filter(lambda x: not re.fullmatch(r'[0-9]+', x), text_var))
        text_symb = sorted(list(set(text_symb + parts)))

        return print(f"Service words: {', '.join(sorted(list(set(text_serv))))}\nVariables: {', '.join(text_var)}\nNums: {', '.join(sorted(list(set(text_num))))}\nSymbols: {' '.join(text_symb)}")


if __name__ == '__main__':
    test_case = 'ifca))))b=sin2*a);el se b=2*a;' #By Variant 22
    # test_case = 'repeat begin И:=b+a[n]; n:=n-1 end until n=0;' #With kirillic
    # test_case = 'switch(c){case 0: b=2.33*a[n]; break; default: b=d;}' #With float
    # test_case = 'do{--n;... if(b==a[n]) return n;}while(n); a=5*3;' #With ..., --(but without -) and with ==
    # test_case = 'switch(c){case 0: b&=a[n]; break; default: b|=(d >= 3)||(c < myfunc(n));}' #With logical operators
    # test_case = 'typedef struct {int somevar;short another;double last} RESULT;' #with some rare service words
    compile_text(test_case)
