"""Amazing Pascal Parser and Lexer by Oleh Serikov"""

import re


def main(code):
    class LexixError(Exception):
        def __init__(self, reason, token=None):
            self.reason = reason
            self.token = token
        
        def __str__(self):
            if self.token is None:
                return self.reason

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
        return part in {'+', '-', '/', '*', '%'}


    def is_rel_operator(part):
        return part in {'<', '<=', '>', '>=', '<>', '='}


    def is_logic_operator(part):
        return part in {'and', 'or'}


    def is_bracket(part):
        return part in {'(', ')'} # , '[', ']', '{', '}'


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


    def is_boolean(part):
        return part in {'true', 'false'}


    def identify(part, idx):
        if is_operator(part):
            tokens.append(('operator', part, idx))
        elif is_rel_operator(part):
            tokens.append(('rel_op', part, idx))
        elif part == ':=':
            tokens.append(('assign', part, idx))
        elif is_bracket(part):
            tokens.append(('bracket', part, idx))
        elif part == ';':
            tokens.append(('semicolon', part, idx))
        elif is_logic_operator(part.lower()):
            tokens.append(('logic_op', part, idx))
        elif is_boolean(part):
            tokens.append(('boolean', part, idx))
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
    def find_brackets(tokens):
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

        print(opening, closing, opening != closing)
        if opening != closing:
            raise LexixError('missing )', tokens[idx - 1])
        
        return tokens[1:idx - 1], tokens[idx:]


    @log
    def parse_mix(tokens, n):
        """
        build tree for logic/math expression from tokens

        correct examples:
            [logic] -> boolean
            [math] -> math
        """
        try:
            parse_math(tokens, n)
        except LexixError:
            parse_logic(tokens, n)
        

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

        # INFO: idx is index of next token after END

        if opening != closing:
            raise LexixError('Missing end', tokens[idx - 1])

        if end_semicolon and (idx == len(tokens) or tokens[idx][0] != 'semicolon'):
            raise LexixError('Missing semicolon', tokens[idx])
        
        right = idx
        if idx < len(tokens) and tokens[idx][0] == 'semicolon':
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
            logic, less = find_brackets(tokens)
            if len(logic) == 0:
                raise LexixError('Missing boolean expression', tokens[0])
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
            if len(tokens) == 0:
                raise LexixError('Wrong for statement', token)
            assign, ex_assign = find_to(tokens)
            parse_assign(assign, 4 * n + 3, False, True) #no ;
            tree[2 * n + 1] = 'to'
            # math_expr
            math, new_tokens = find_do(ex_assign)
            parse_math(math, 4 * n + 4)
            # new_tokens
            parse(new_tokens, 2 * n + 2, end_semicolon)
        else:
            if len(tokens) == 0:
                raise LexixError('Wrong statement', token)
            parse_assign([token] + tokens, 2 * n + 1, end_semicolon, False)


    @log
    def parse_logic(tokens, n):
        """
        build tree for logic expression from tokens

        correct examples:
            [(, logic, )]
            [logic, logic_op, logic]
            [boolean]
            [math, rel_op, math]
        """

        def parse_operator(op):
            """
            parse expression, using given op as top-level operator
            """
            if op not in values:
                return

            idx = values.index(op)
            if idx in (0, len(tokens)):
                raise LexixError('Missed operand for operator', tokens[idx])

            tree[n] = tokens[idx][1]
            parse_logic(tokens[:idx], 2 * n + 1)
            parse_logic(tokens[:idx + 1], 2 * n + 2)

        if len(tokens) in (0, 2):
            raise LexixError('Wrong expression')
        
        # boolean
        if len(tokens) == 1:
            # if tokens[0][0] != 'boolean':
            if tokens[0][0] not in ('boolean', 'var', 'num'): # 5th lab, ignore types
                # raise LexixError('Wrong boolean expression', tokens[0]) #5th lab, ignore types
                raise LexixError('Wrong expression', tokens[0])
            tree[n] = tokens[0][1]
            return
        
        #( logic ) [logic_op logic]
        if tokens[0][1] == '(':
            expression, less = find_brackets(tokens)

            if len(less) == 1:
                # raise LexixError('Wrong boolean expression', tokens[0]) #5th lab, ignore types
                raise LexixError('Wrong expression', less[0])
            if len(less) > 0 and less[0][0] != 'logic_op':
                # raise LexixError('Wrong boolean expression', tokens[0]) #5th lab, ignore types
                raise LexixError('Wrong expression', less[0])

            if len(less) == 0:
                tree[n] = 'brackets'
                parse_logic(expression, 2 * n + 1)
                return

            tree[n] = less[0][1]
            tree[2 * n + 1] = 'brackets'
            parse_logic(expression, 4 * n + 3)
            parse_logic(less[1:], 2 * n + 2)
            
            return
        # parsing [math, rel_op, math] and [logic(don't starts with a bracket), logic_op, logic]
        # 5th lab, ignore types
        # mix rel_op|logic_op mix
        values = [i[1] for i in tokens]
        if '(' in values:
            idx = values.index('(')
            if tokens[idx - 1][0] not in ('operator', 'logic_op', 'rel_op'): # 5th lab, ignore types
                raise LexixError('Missing operator', tokens[idx - 1])
            tree[n] = tokens[idx - 1][1]
            parse_logic(tokens[:idx - 1], 2 * n + 1)
            expr, less = find_brackets(tokens[:idx])
            if less == 0:
                parse_logic(expr, 2 * n + 2)
                return
            
            if len(less) == 1 or less[0][1] not in ('operator', 'logic_op', 'rel_op'): # 5th lab, ignore types
                raise LexixError('Missing operator', less[0])
            
            tree[2 * n + 2] = less[0][1]
            parse_logic(expr, 4 * n + 3)
            parse_logic(less[1:], 4 * n + 4)
            return

        # parse expression with operators in operator meaning descending # 5th lab, ignore types
        operators = ['and', 'or', '*', '/', '%', '+', '-', '<', '<=', '>', '>=', '<>', '=']
        map(lambda op: parse_operator(op), operators)


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
        if idx == 0:
            raise LexixError('Missing base expression', tokens[0])
        if idx == len(tokens):
            raise LexixError('Missing to', tokens[idx - 1])

        return tokens[:idx], tokens[idx + 1:]


    @log
    def parse_assign(tokens, n, end_semicolon=True, no_semicolon=False):
        """
        build tree from tokens only within assign statement
        end_semicolon ==:
            True, False -> ; has to be
            False, True -> ; has to don't be
            True, True -> impossible
            False, False -> ; can be
        """
        if tokens[0][0] != 'var':
            raise LexixError('Missing var', tokens[0])
        if tokens[1][0] != 'assign':
            raise LexixError('Missing assign', tokens[1])
        if len(tokens) < 3:
            raise LexixError('Wrong assign statement', tokens[1])
        if no_semicolon and tokens[-1][0] == 'semicolon':
            raise LexixError('Unexpected semicolon', tokens[-1])
        tree[n] = 'assign'
        tree[2 * n + 1] = tokens[0][1]
        if tokens[-1][0] == 'semicolon':
            parse_mix(tokens[2:-1], 2 * n + 2)
            return

        parse_mix(tokens[2:], 2 * n + 2)


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

        correct examples:
            [(, math, )]
            [(, math, ), operator, math]
            [var | num, [operator, math]]
        """
        if len(tokens) in (0, 2):
            raise LexixError('Wrong expression')
        if tokens[0][1] != '(' and tokens[0][0] not in ('var', 'num'):
            raise LexixError('Wrong math expression', tokens[0])
        
        # ( math ) [operator math]
        if tokens[0][1] == '(':
            expression, less = find_brackets(tokens)

            if len(less) == 1:
                raise LexixError('Wrong math expression', less[0])
            if len(less) > 0 and less[0][0] != 'operator':
                raise LexixError('Wrong math operator', less[0])

            if len(less) == 0:
                tree[n] = 'brackets'
                parse_math(expression, 2 * n + 1)
                return

            tree[n] = less[0][1]
            tree[2 * n + 1] = 'brackets'
            parse_math(expression, 4 * n + 3)
            parse_math(less[1:], 2 * n + 2)
            
            return
        # var|num 
        if len(tokens) > 1 and (len(tokens) == 2 or tokens[1][0] != 'operator'):
            raise LexixError('Wrong math expression', tokens[1])

        if len(tokens) == 1:
            tree[n] = tokens[0][1]
            return
        
        tree[n] = tokens[1][1]
        tree[2 * n + 1] = tokens[0][1]
        parse_math(tokens[2:], 2 * n + 2)


    # START HERE
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
            if curr == ':=' or is_rel_operator(curr):
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

        return True # Successfully finish
        
    except SyntaxError:
        pass
        return False # Error
    except LexixError as e:
        print(e)
        return False # Error


if __name__ == '__main__':
    code = 'if (a > b) then begin for i := 1 to n + 4 do begin a := b; end; end;'
    main(code)
