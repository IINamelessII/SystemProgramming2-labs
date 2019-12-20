import re


def debug(x):
    pass
    # print('DEBUG: ', x)


def is_f_type(part):
    return part in {'double', 'float'}


def is_d_type(part):
    return part in {'short', 'int', 'lonh', 'unsigned'}


def is_num(part):
    """
    >>> '2.33'
        True
    >>> '11'
        True
    >>> '11.'
        False
    >>> '.22'
        False
    """
    return re.fullmatch(r'[0-9]+(\.[0-9]+)?', part)


def is_var(part):
    """
    >>> '_abc_123_'
        True
    >>> '2abc_123'
        False
    """
    return re.fullmatch(r'[a-zA-Z\_]+[a-zA-Z0-9\_]*', part)


def is_array(part):
    return re.fullmatch(r'[a-zA-Z\_]+[a-zA-Z0-9\_]*\[\-?[0-9]+\]', part)


def main(code):

    def get_var(name):
        for v in vars:
            if v['name'] == name:
                return v

    def parse(expr):
        orig_expr = expr
        
        for op_set in [{'<', '<=', '>', '>=', '!=', '=='}, {'||', '&&'}, {'+', '-', '/', '*', '%'}]:
            for op in op_set:
                expr = expr.replace(op, '`')
        
        tokens = expr.split('`')
        if '' in tokens:
            return f'Error: Wrong Expression {orig_expr}'
    
        # debug(tokens)
        tp = 'd'

        for tok in tokens:
            if not is_var(tok) and not is_array(tok) and not is_num(tok):
                if tok.endswith('['):
                    return f'Error: Negative index while trying to access {tok[:-1]}'
                return f'Error: Illegal variable {tok}'
            
            if is_array(tok):
                l, r = tok.index('['), tok.index(']')
                name = tok[:l]
                idx = int(tok[l+1:r])
                if idx < 0:
                    return f'Error: Negative index {tok}'
                var = get_var(name)
                if not var:
                    return f'Error: Undefined Variable {name}'
                
                if not var['arr']:
                    return f'Error: Trying to access by index to static variable {name}'
    
                if idx > var['len']:
                    return f'Error: Index out of range {tok}'

                if var['type'] == 'f':
                    tp = 'f'
                continue

            elif is_num(tok):
                if '.' in tok:
                    tp = 'f'
                continue

            # tok is variable
            var = get_var(tok)
            if not var:
                return f'Error: Undefined Variable {tok}'
            if var['type'] == 'f':
                tp = 'f'

        return tp

    if code.count('(') > code.count(')'):
        print('Error: Missing )')
        return
    elif code.count(')') > code.count('('):
        print('Error: Missing (')
        return
    
    code = code.replace('(', '').replace(')', '')

    expressions = list(filter(lambda x: len(x) > 0, code.split(';')))
    expressions = list(map(lambda x: x.strip(), expressions))
    # debug(expressions)
    vars = [] # I dont need vars() built-in function

    for ex in expressions:
        curr_tp = None
        for tp in TYPES:
            # if ex is declaration
            if ex.startswith(tp):
                ex = ex[len(tp):].strip()
                # if fpu
                if is_f_type(tp):
                    curr_tp = 'f'
                else:
                    curr_tp = 'd'
        # if declaration
        if curr_tp:
            # debug(ex)
            vs = list(map(lambda x: x.strip(), ex.split(',')))
            # debug(vs)
            for v in vs:
                if v in list(map(lambda x: x['name'], vars)):
                    print(f'Error: Redeclaration variable {v}')
                    return
                if is_array(v):
                    l, r = v.index('['), v.index(']')
                    lng = int(v[l+1:r])
                    if lng < 0:
                        print(f'Error: Negative length {v}')
                        return
                    vars.append({'name': v[:l], 'type': curr_tp, 'arr': True, 'len': lng})
                    continue
                elif is_var(v):
                    vars.append({'name': v, 'type': curr_tp, 'arr': False, 'len': 0})
                    continue
                else:
                    print(f'Error: Wrong Declaration Format {v}')
                    return
            continue
        # if ex is not declaration (operations olny)
        # debug(ex)
        # var = calc_expr ONLY
        if ex.count('=') != 1:
            if ex.count('=') == 0:
                print(f'Error: Missing = at expression {ex}')
                return
            print(f'Error: Unexpected = at expression {ex}')
            return
        temp = ex.split('=')
        # debug(temp[0])
        if is_array(temp[0]):
            l,r = temp[0].index('['), temp[0].index(']')
            name = temp[0][:l]
            ln = int(temp[0][l+1:r])
            var = get_var(name)
            if not var:
                print(f'Error: Undefined Variable {name}')
                return
            if ln > var['len']:
                print(f'Error: Index out of range {temp[0]}')
            left_t = var['type']
        
        elif is_num(temp[0]):
            print(f'Error: Trying to assign to number {temp[0]}')
        
        #left part is var
        elif temp[0] not in list(map(lambda x: x['name'], vars)):
            print(f'Error: Undefined Variable {temp[0]}')
            return
        else:
        
        # debug(vars)
            var = get_var(temp[0])
            left_t = var['type']

        right_t = parse(temp[1])
        if len(right_t) != 1:
            print(right_t)
            return
        if left_t == 'd' and right_t == 'f':
            print(f'Error: Trying assign floating-pointed number to {temp[0]}')    
            return
        
    print('OK')   
        


TYPES = {'double', 'float', 'int', 'long', 'short', 'unsigned'}

OPERATOS = {'+', '-', '/', '*', '%'}.union({'||', '&&'}).union({'<', '<=', '>', '>=', '!=', '=='})


if __name__ == "__main__":
    code = 'double b, a[3];  long n; n=n-1; b=c<a; b=2*a[2];' # Error: Undefined Variable c
    # code = 'double b, a[3];  long n; n=n-1; b=3<a; b=2*a[2];' # OK
    # code = 'double b a[3];  long n; n=n-1; b=3<a; b=2*a[2];' # Error: Wrong Declaration Format b a[3]
    # code = 'double b, a[3];  long n; n=n-1; b=3<a; n=2*a[2];' # Error: Trying assign floating-pointed number to n
    # code = 'double b, a[3];  long n; n=n-1; b=3<a; b=2*a[22];' # Error: Index out of range a[22]
    # code = 'double b, a[3];  long n; n=n--1; b=3<a; b=2*a[2];' # Error: Wrong Expression n--1
    # code = 'double b, a[3];  long n; n=n-1; b=n<a; b=2*a[2];' # OK
    # code = 'double b, a[-3];  long n; n=n-1; b=3<a; b=2*a[2];' # Error: Negative length a[-3]
    # code = 'double b, a[3];  long n; n=n-1; b=3<a; b=2*a[-2];' # Error: Negative index while trying to access a
    # code = 'double b, a[3];  long n; n=n-1; b=3<a b=2*a[2];' # Unexpected = at expression b=3<a b=2*a[2]
    # code = 'double b, a[3];  long n; n=n-1; b=3<a; b=2a[2];' # Illegal variable 2a[2]
    # code = 'double b, a[3];  long n; n=n-1; b=3<a; b=2*a[(2)];' # OK
    # code = 'double b, a[3];  long n; n=n-1; b=3<a; b=2*a[2];' # OK
    main(code)
