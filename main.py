#-------------------------------------------------------------------------------
# Name:        Smartest Mouse Ever
# Purpose:      Cisc 857
#
# Author:      Thomas Parker
#
# Created:     20/11/2019
# Copyright:   (c) Thomas Parker 2019
#-------------------------------------------------------------------------------
import random
import math

#store state as (height, relative_degree)

#cheating = open("cheating.txt","w") used to make sure that when we're "cheating" we actually aren't baiting the RL

radius = 30
degrees = 60
half_degrees = int((degrees/2) +1)
mouse_speed = 1
cat_speed = 3.6*mouse_speed

Qsa = {}
esa = {}
cat_degree = 0
mouse_degree = 50
relative_degree = 50
average = 0
count = 0
start_state = (0,0)
cat_movement = 0
cheated = False

def calculate_cat_move():
    global cat_movement
    circumference = 2 * math.pi * radius
    cat_movement = (cat_speed / circumference)*degrees


def canmakeit(state):
    if relative_degree <= degrees/2:
        if ((relative_degree)-1) > (radius - state[0]): #cheating
            return True
    else:
        if(((degrees - relative_degree)-1) > (radius - state[0])):
            return True
    return False

def floor_or_ceil(a_float):
    if random.random() < a_float%1: #chooses to ceil or float
        return math.ceil(a_float)
    else:
        return math.floor(a_float)
def writeQsa_and_esa_toFile(ep):
    f = open(str(ep) +"qsa.txt","w")
    for i in range(0,radius + 1):
        line = ""
        for j in range(0,half_degrees):
            line += str(i) +"," + str(j) + str(Qsa[(i,j)]) + "|"
        f.write(line)
    f.close()
    g = open(str(ep) +"esa.txt","w")
    for i in range(0,radius +1):
        line = ""
        for j in range(0,half_degrees):
            line += str(i) +"," + str(j) + str(esa[(i,j)]) + "|"
        g.write(line)
    g.close()

def traverse_Qsa(start_state = None): #follows "best" bath
    visited = [] #stores the path
    if start_state ==  None:
        state = (random.randint(1,radius/5), random.randint(0,degrees -1))
    else:
        state = start_state
    action = follow_path(state) #finds next action
    count = 0
    while state[0] != radius: #While not at G
        count +=1
        visited.append(state) #adds to path
        state = evaluate_mouse_movement(state,action)[1] #moves to next state
        state = evaluate_cat_movement(state)
        action = follow_path(state)
        if count > 1000:
            return -1
    visited.append(state)
    return visited #returns path

def follow_path(state): #used in traverse_Qsa to follow a policy
    actions = Qsa[(state[0],state[1])]
    return actions.index(max(actions))

def initialize_Qsa():
    global Qsa
    for i in range(0,radius +1): #Height (distance from center)
        for j in range(0,half_degrees): #Degrees
            Qsa[(i,j)] = [1,1,1,1] #increase height, decrease height, circle left, circle right

def initialize_esa():
    global esa
    for i in range(0,radius + 1): #Height
        for j in range(0,half_degrees): #Degrees
            esa[(i,j)] = [0,0,0,0]  #increase height, decrease height, circle left, circle right


def evaluate_mouse_movement(state,action):
    #returns reward, state_prime
    global mouse_degree
    if action <2 or action == 5: #up/down/cheating
        temp_mouse_speed = floor_or_ceil(mouse_speed)
        if temp_mouse_speed <1:
            print("error")
        if action == 0: #moving away from center, increasing height
            if state[0] + temp_mouse_speed >= radius: #Made it to edge
                if relative_degree >0:
                    print("YAY") #lives
                    return 10000, (state[0] + temp_mouse_speed, state[1])
                else:
                    print("Boo",state) #eaten
                    return -100000, (state[0] + temp_mouse_speed, state[1])
            else:
                return 100 if action ==5 else -1, (state[0] + temp_mouse_speed, state[1])

        if action == 1: #moving down towards center, decreasing height
            if state[0] - temp_mouse_speed <1:
                return 100 if action ==5 else -1,(1,state[1])
            else:
                return 100 if action ==5 else -1,(state[0] - temp_mouse_speed, state[1])
    else: #counterclockwise or clockwise movement
        circumference = 2 * math.pi * state[0]
        movement = mouse_speed / circumference
        degrees_moved = movement *degrees
        tempdegree = degrees_moved
        degrees_moved = floor_or_ceil(degrees_moved)
        #print(state[0],tempdegree,degrees_moved)
        if action == 2: #counterclockwise
            mouse_degree -= degrees_moved
            tempdegree = state[1] - degrees_moved

            if mouse_degree < 0:
                mouse_degree = degrees + mouse_degree
            if tempdegree < 0:
                tempdegree = degrees + tempdegree

        elif action == 3: #clockwise
            mouse_degree += degrees_moved
            tempdegree = state[1] + degrees_moved

            while mouse_degree > (degrees - 1):
                mouse_degree = mouse_degree - (degrees)
            while tempdegree > (degrees -1):
                tempdegree = tempdegree -(degrees)
        return 0,(state[0], tempdegree)

def update_relative_degree():
    global relative_degree
    if mouse_degree == cat_degree:
        relative_degree = 0
    elif mouse_degree > cat_degree:
        relative_degree = mouse_degree - cat_degree
    else:
        relative_degree = mouse_degree + (degrees ) - cat_degree
    foldinhalf() #halves statespace by folding space in half

def cat_move(direction): #1 is right, -1 is left
    global cat_degree,average,count

    degrees_moved = cat_movement
    degrees_moved = 1 #floor_or_ceil(degrees_moved)
    count+=1
    average = (float(average * (count-1)) + float(degrees_moved))/count
    #print(average)

    if (relative_degree <= degrees_moved) or (degrees-relative_degree) <= degrees_moved:
        temp_degree = mouse_degree
    else:
        temp_degree = cat_degree + (direction *degrees_moved)

        if temp_degree > (degrees -1):
            temp_degree = temp_degree - degrees
        elif temp_degree < 0:
            temp_degree = degrees + temp_degree

    cat_degree = temp_degree

def evaluate_cat_movement(state):
    global relative_degree
    update_relative_degree()
    if mouse_degree > cat_degree:
        if mouse_degree - cat_degree < degrees/2:
            #move right
            cat_move(1)
        else:
            cat_move(-1)
    else:
        if cat_degree - mouse_degree < degrees/2:
            cat_move(-1)
        else:
            cat_move(1)
    update_relative_degree()
    return (state[0], relative_degree)

def choose_a(state): #increase height, decrease height, circle left, circle right
    if (canmakeit(state)): #cheating
            return 0
    actions = Qsa[state[0],state[1]]
    if (random.random() < epsilon) or (actions[0] == actions[1] ==actions[2] == actions[3]) : #epsilon or empty
        return random.randint(0,3) #random
    else: #greedy
        return actions.index(max(actions)) #max

def foldinhalf(): #halves state space by considering vertical reflections as same space
    global relative_degree
    if relative_degree > degrees/2:
        relative_degree = int((degrees/2) - (relative_degree - degrees/2))
    return relative_degree

def smartest_mouse_ever(episodes,i_alpha,i_epsilon, i_gamma = 0.80, epsilon_decay = 0.997):
    global qsa, epsilon, gamma, esa, escaping, cat_degree,mouse_degree, start_state,relative_degree
    _lambda = 0.80
    gamma = i_gamma
    epsilon = i_epsilon
    alpha = i_alpha
    initialize_Qsa()
    initialize_esa()
    calculate_cat_move()
    print(cat_movement)
    cheated = False
    for e in range(episodes):
        #print(traverse_Qsa())
        #writeQsa_and_esa_toFile(e)
        #print(e)
        cat_degree = 15#random.randint(0,half_degrees)
        mouse_degree = 16 #random.randint(0,half_degrees)
        update_relative_degree()
        foldinhalf()
        state = (12, relative_degree) #random.randint(1,radius/5)
        start_state = state
        epsilon = epsilon * epsilon_decay
        #alpha = alpha
        action = choose_a(state)
        steps = 0
        while state[0] != radius:
            steps +=1
            if steps % 1000 == 0:
                print("1000 steps: " + str(steps/1000))
                #print(state)
            reward, state_prime = evaluate_mouse_movement(state,action)
            state_prime = evaluate_cat_movement(state_prime)
            foldinhalf()
            state_prime = (state_prime[0],relative_degree)
            action_prime = choose_a(state_prime)
            qsavalue = Qsa[state][action]

            delta = reward + (gamma*(Qsa[state_prime][action_prime]) - qsavalue)
            esa[state][action] +=1
            for i in range(0,radius):
                for j in range(0,half_degrees):
                    Temp_Qsa_Values = Qsa[(i,j)]
                    if delta != 0.0:
                        for val in range(4):
                            Temp_Qsa_Values[val] += alpha*(delta)*(esa[(i,j)][val]) #e(s,a)  calculatio
                    for val in range(4):
                        esa[(i,j)][val] = esa[(i,j)][val]*gamma*_lambda
                        if math.isnan(Temp_Qsa_Values[val]):
                            Temp_Qsa_Values[val] = 0
                    Qsa[(i,j)] = Temp_Qsa_Values
            state = state_prime
            action = action_prime
        print(start_state,mouse_degree, cat_degree,relative_degree,steps)

#secure = True
smartest_mouse_ever(100,0.9,0.1)
#paths = []

'''insecure = 0
for i in range(1,int(radius/2)): #Height (distance from center)
    for j in range(0,half_degrees): #Degrees
        mouse_degree = j
        cat_degree = 0
        update_relative_degree()
        teststate = (i,j)
        path = traverse_Qsa(teststate)
        if traverse_Qsa(teststate) == -1:
            paths.append(path)
        else:
            paths.append(path)
            insecure +=1
    if secure == False:
        break
print(paths)
paths_file = open("paths.txt","w")
for path in paths:
    paths_file.write(str(path) + "\n")
paths_file.close()

print(insecure)
#cheating.close()
print(average)'''
