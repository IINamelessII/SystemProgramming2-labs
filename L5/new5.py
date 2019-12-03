"""Amazing Pascal Parser and Lexer by Oleh Serikov"""

import re


class LexixError(Exception):
    def __init__(self, reason, token):
        self.reason = reason
        self.token = token
    
    def __str__(self):
        return f'{self.reason} at {self.token[1]} position: {self.token[2]}'


def log(func):
    def wrapper(*args, **kwargs):
        # res = 
        print(f'Function: {func.__name__}')
        print(f'Args: {args}')
        print('\n')
        return func(*args, **kwargs)
    return wrapper


def is_operator(part):
    return part in {'+', '-', '/', '*'}


def is_logical_operator(part):
    return part in {'<', '<=', '>', '>=', '<>', '!=', '='}


def is_bracket(part):
    return part in {'(', ')', '[', ']', '{', '}'}


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


def identify(part, idx):
    if is_operator(part):
        tokens.append(('operator', part, idx))
    elif is_logical_operator(part):
        tokens.append(('logic_op', part, idx))
    elif part == ':=':
        tokens.append(('assign', part, idx))
    elif is_bracket(part):
        tokens.append(('bracket', part, idx))
    elif part == ';':
        tokens.append(('semicolon', part, idx))
    elif part.lower() == 'if':
        tokens.append(('if', part, idx))
    elif part.lower() == 'then':
        tokens.append(('then', part, idx))
    elif part.lower() == 'else':
        tokens.append(('else', part, idx))
    elif part.lower() == 'begin':
        tokens.append(('begin', part, idx))
    elif part.lower() == 'end':
        tokens.append(('end', part, idx))
    elif part.lower() == 'for':
        tokens.append(('for', part, idx))
    elif part.lower() == 'to':
        tokens.append(('to', part, idx))
    elif part.lower() == 'do':
        tokens.append(('do', part, idx))
    elif is_num(part):
        tokens.append(('num', part, idx))
    elif is_var(part):
        tokens.append(('var', part, idx))
    elif part != '':
        print(f'Syntax Error with token {part} at position {idx}')
        raise SyntaxError()


@log
def find_logic(tokens):
    """
    find pair of brackets and split their content from other tokens

    >>> [(, token1, token2, token3, ), token4, token5]
        [token1, token2, token3], [token4, token5]
    """
    if tokens[0][1] != '(':
        raise LexixError('Missing (', tokens[0])

    idx = 1
    opening, closing = 1, 0
    while opening != closing and idx < len(tokens):
        if tokens[idx][1] == ')':
            idx += 1
            closing += 1
            continue

        if tokens[idx][1] == '(':
            idx += 1
            opening += 1
            continue

        idx += 1

    if opening != closing:
        raise LexixError('missing )', tokens[idx])
    
    return tokens[1:idx - 1], tokens[idx:]


@log
def parse_logic(tokens, n):
    """
    build tree for logic expression from tokens
    """
    return None


@log
def find_end(tokens, end_semicolon):
    """
    find end and split content before end from other tokens

    >>> [token1, token2, token3, 'end', ';', token4, token5], True
        [token1, token2, token3], [token4, token5]
    >>> [token1, token2, token3, 'end', token4, token5], False
        [token1, token2, token3], [token4, token5]
    >>> [token1, token2, token3, 'end', ';', token4, token5], False
        [token1, token2, token3], [token4, token5]
    """

    idx = 0
    opening, closing = 1, 0 #begin and end counts
    while opening != closing and idx < len(tokens):
        if tokens[idx][0] == 'end':
            closing += 1
            idx += 1
            continue

        if tokens[idx][0] == 'begin':
            opening += 1
            idx += 1
            continue

        idx += 1

    if opening != closing:
        raise LexixError('Missing end', tokens[idx])

    if end_semicolon and tokens[idx][0] != 'semicolon':
        raise LexixError('Missing semicolon', tokens[idx])

    right = idx
    if tokens[idx][0] == 'semicolon':
        right += 1

    return tokens[:idx - 1], tokens[right:]


@log
def parse(tokens, n, end_semicolon=True):
    """
    build tree from tokens
    """
    if len(tokens) == 0:
        return
    token = tokens.pop(0)
    # if -> logic_expr -> then -> tokens
    if token[0] == 'if':
        # if
        tree[n] = 'if'
        # logic_expr
        logic, less = find_logic(tokens)
        parse_logic(logic, 2 * n + 1)
        # then
        token = less.pop(0)
        if token[0] != 'then':
            raise LexixError('Missing then', token)
        # tokens
        parse(less, 2 * n + 2)
    
    # begin -> tokens -> end [; #if end_semicolon] [new_tokens]
    elif token[0] == 'begin':
        # begin
        tree[n] = 'begin'
        # tokens
        inside_tokens, less = find_end(tokens, end_semicolon)
        parse(inside_tokens, 2 * n + 1, False)
        # new_tokens
        parse(less, 2 * n + 2)
    
    # for -> assign -> to -> math_expr -> do -> new_tokens
    elif token[0] == 'for':
        # for
        tree[n] = 'for'
        # assign
        assign, ex_assign = find_to(tokens)
        parse_assign(assign, 4 * n + 3)
        tree[2 * n + 1] = 'to'
        # math_expr
        math, new_tokens = find_do(ex_assign)
        parse_math(math, 4 * n + 4)
        # new_tokens
        parse(new_tokens, 2 * n + 2, end_semicolon)
    else:
        parse_assign([token] + tokens, 2 * n + 1)


@log
def find_to(tokens):
    """
    find to and split content before from other tokens

    >>> [assign1, assign2, assign3, to, math1, math2, token1]
        [assign1, assign2, assign3], [math1, math2, token1]
    """
    idx = 0
    while tokens[idx][0] != 'to' and idx < len(tokens):
        idx += 1
    if idx == len(tokens):
        raise LexixError('Missing to', tokens[idx - 1])

    return tokens[:idx], tokens[idx + 1:]


@log
def parse_assign(tokens, n):
    """
    build tree from tokens only within assign statement
    """
    if tokens[0][0] != 'var':
        raise LexixError('Missing var', tokens[0])
    if tokens[1][0] != 'assign':
        raise LexixError('Missing assign', tokens[1])
    tree[n] = 'assign'
    tree[2 * n + 1] = tokens[0][1]
    parse_logic(tokens[2:], 2 * n + 2)


@log
def find_do(tokens):
    """
    find do and split content before from other tokens

    >>> [math1, math2, math3, do, token1, token2, token3]
        [math1, math2, math3], [token1, token2, token3]
    """
    idx = 0
    while tokens[idx][0] != 'do' and idx < len(tokens):
        idx += 1
    if idx == len(tokens):
        raise LexixError('Missing do', tokens[idx - 1])

    return tokens[:idx], tokens[idx + 1:]


@log
def parse_math(tokens, n):
    """
    build tree from tokens only within math statement
    """
    return None



code = 'if (a > b) then begin for i := 1 to n do begin a := b; end; end;'

tokens = []
curr = ''
idx = -1
try:
    while idx + 1 < len(code):
        idx += 1
        if code[idx].isspace():
            identify(curr, idx - 1)
            curr = ''
            continue

        if code[idx] == ';' or is_bracket(code[idx]) or is_operator(code[idx]):
            identify(curr, idx - 1)
            identify(code[idx], idx)
            curr = ''
            continue

        curr += code[idx]
        if curr == ':=' or is_logical_operator(curr):
            identify(curr, idx)
            curr = ''
            continue
    
    identify(curr, idx)
    print(*tokens, sep='\n')
    print('\n')
    
    tree = dict()
    parse(tokens, 0)
    print('SUCCESSFULL END OF PARSING')
    from pprint import pprint
    pprint(tree)
    
    
except SyntaxError:
    pass
except LexixError as e:
    print(e)
