"""Test 5th lab"""

import os
import sys

from L5 import main


def test(code, success, debug=False):
    """Run test withing isolated from output environment"""
    output = sys.stdout
    if not debug:
        sys.stdout = open(os.devnull, "w")

    result = main(code)
    # come back default output environment
    sys.stdout = output

    if success == result:
        print(f'SUCCES: {code}\n')
    else:
        print(f'FAILED: {code}\n')


if __name__ == '__main__':
    test('if (a > b) then begin for i := 1 to n + 4 do begin a := b; end; end;', True) # OK, default
    test('if (a > b then begin for i := 1 to n + 4 do begin a := b; end; end;', False) # miss bracket
    test('if a > b) then begin for i := 1 to n + 4 do begin a := b; end; end;', False) # miss bracket
    test('if (a > b) then begin for i := 1 to n + 4abc do begin a := b; end; end;', False) # wrong var name(starts with number)
    test('if (a > b) then begin for i := 1 to n + 4 do begin a := b; end;', False)# miss end
    test('if (a > b) then begin for i := 1 to n + 4 do begin a := b; end end;', True) # OK, miss semicolon
    test('if (a > b) then begin for i := 1 to n + 4 do begin a := b end; end;', True) # OK, miss semicolon
    test('if () then begin for i := 1 to n + 4 do begin a := b; end; end;', False) # empty logic statement
    test('if (a  b) then begin for i := 1 to n + 4 do begin a := b; end; end;', False) # miss operator
    test('if (a > b) then begin for i = 1 to n + 4 do begin a := b; end; end;', False) # = instead of ;= within for
    test('if (a > b) then begin for i := 1 to true + 4 do begin a := b; end; end;', False) # logic expression instead of math
    test('if (a > b) than begin for i := 1 to n + 4 do begin a := b; end; end;', False) # wrong then
    test('if (a > b) then begin for i := 1 to n + 4 do do begin a := b; end; end;', False) # odd do
    test('if (a > b) then begin for i := 1 to n + 4 do begin begin a := b; end; end;', False) # odd begin
    test('if (a > b) then begin for i := 1 to n + + 4 do begin a := b; end; end;', False) # miss operand
    test('if (a > b) then begin for i := 1 to n + 4 do begin a := b 32; end; end;', False) # miss operator
    test('(a > b) then begin for i := 1 to n + 4 do begin a := b; end; end;', False) # miss if
