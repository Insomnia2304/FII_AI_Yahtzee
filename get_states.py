NUM_DICES = 5
NUM_SIDES = 6

init_state = [1,1,1,1,1]

states = set()

while init_state != [6,6,6,6,6]:
    states.add(tuple(sorted(init_state)))
    for i in range(NUM_DICES-1, -1, -1):
        if init_state[i] == NUM_SIDES:
            init_state[i] = 1
        else:
            init_state[i] += 1
            break
states.add(tuple(sorted(init_state)))

print(len(states))