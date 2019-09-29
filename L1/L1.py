def match_lvl(s, key):
    return sum([min(s.count(i), key.count(i)) for i in set(key)])


if __name__ == "__main__":
    data = ['abcdefgh', 'AbCdeFGh', 'SimpleStringsS', 'HelloWorld', 'ZZZZzzzz']
    while True:
        key = input()
        if key == 'exit()':
            break
        matches = [match_lvl(string, key) for string in data]
        print(f'Max match level is {max(matches)}')
        if not max(matches):
            print('No matches!')
        else:
            print(*list(filter(lambda x: matches[data.index(x)] == max(matches), data)), sep='\n')
        