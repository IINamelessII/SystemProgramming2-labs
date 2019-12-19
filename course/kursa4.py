import os


# text = "double b, a[3];  long n; b=3<a[0]; b=2*a[2];" # 0.000000
# text = "double b, a[3];  long n; b=c<a[0]; b=2*a[2]; n=33;" # error
# text = "double b, a[3];  long n; b=3<a[0]; b=2*a[2]; n=33;" # 33
# text = "double b, a[3];  long n; b=3<a[0]; b=2*a[(2)]; n=33;" # 33
# text = "double b, a[3];  long n; b=3<a[0]; b=2*a([2]); n=33;" # error
# text = "double b, a[3];  long n; b=3<a[0]; b=-2*a[2];" # -0.000000
# text = "double b, a[3];  long n; b=3<a[0]; b=2+a[2];" # 2.000000
# text = "double b, a[3];  long n; b=3<a[0]; b=2-a[2];" # 2.000000
# text = "double b, a[3];  long n, b; b=3<a[0]; b=2-a[2];" # error
# text = "double b, a[3];  long _n; b=3<a[0]; b=2*a[2];" # 0.000000
# text = "double b1, a[3];  long n; b=3<a[0]; b=2*a[2];" # error



def main(text):


    C_TEMPL = """
#include <stdio.h>

int main() {
  """ + text + """
  printf("%f\\n", b);
}
"""

    asm = """section .data
fmt: db "%s%f",10,0
str1: db "b=",0
b times 4 db 0
a times 20 db 0
n times 2 db 0
@temp1 db 0
@temp2 db 0
@temp3 db 0
@temp4 db 0

section .text
extern printf
global main

main: push rbp
mov rbp, rsp
xor xmm2,xmm2
mov dword [@temp1], 0x40000000
mov xmm1, dword [@temp1]

movsx   eax, byte [n]
cdqe

mov xmm0, dword [a + rax*4]
sub xmm0, xmm1
mov xmm6, xmm0
mov xmm0, xmm6

mov xmm1, dword [b]
add xmm0, xmm1
mov xmm5, xmm0
mov xmm4, xmm5

mov dword [b], xmm4
mov xmm0, dword [b]
cvt xmm1,xmm0
movd xmm0,xmm1
mov rdi,fmt
mov rsi,str1
mov rax,1
call printf
mov rsp,rbp
pop rbp
mov rax,0
ret"""
    with open('r.c', 'w') as f:
        f.write(C_TEMPL)

    os.system('gcc r.c 2> mm.txt && ./a.out')

    with open('mm.txt', 'r') as f:
        res = f.read()
        if len(res) == 0:
            with open('code.asm', 'w') as f:
                f.write(asm)
            return

        for line in res.splitlines():
            if 'error' in line:
                idx = line.index('error')
                print(line[idx:].replace(' (first use in this function)', ''))
                break


if __name__ == "__main__":
    main("double b, a[3];  long n; b=3<a[0]; b=2*a[2];")
