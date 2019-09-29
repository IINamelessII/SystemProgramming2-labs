transitions = [
    {'dlm': 1, 'cfr': 1},
    {'dlm': 2, 'cfr': 2},
    {'dlm': 6, 'cfr': 3},
    {'dlm': 4, 'cfr': 4},
    {'dlm': 5, 'cfr': 1},
    {'dlm': 6, 'cfr': 6},
    {},
]
state = 0
signals = input().split()

if not signals:
    print('No signals, staying at S1')
else:
    res = f'S{state + 1}'
    for signal in signals: 
        state = transitions[state].get(signal, state)
        res += f' ({signal}) -> S{state + 1}'
    print(res)
