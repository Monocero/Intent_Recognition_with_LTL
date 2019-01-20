import vrep
import math
from flloat.parser.ltlf import LTLfParser
from flloat.base.Symbol import Symbol
from flloat.semantics.ldlf import FiniteTrace
from pythomata.base.Simulator import DFASimulator

import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages') #<------per importare correttamente cv2
import cv2

import numpy as np
import matplotlib.pyplot as plt
from math import fabs
import functions2 as func

vrep.simxFinish(-1)
####SIMBOLI
# right, center, left
# get_close, arrest, get_far
# interaction_area
########################### inizialization
#                       "G(F interaction_area)",
                                             #Interact                                                                                                         
formulas = [ ["G(F (center & get_close))", "get_close U (F(G(stop & interaction_area)))"] , \
             ["G ( F get_far )", "G(F(right | left))"] ]
#                                             #not interact
#                      "G((get_close & right | left) U get_far)"
 
#nuove formule
#AvvicinandoU(F(Fermo e Vicino))
#(DestraUSinistra)v(SinistraUDestra)v(CentroU(Desta v Sinistra)

simboliFormule = [ [frozenset({'get_close', 'center'}), frozenset({'get_close', 'stop', 'interaction_area'})] , \
                   [frozenset({'get_far'}), frozenset({'right', 'left'})] ]

parser = LTLfParser()
automatons = [ [parser(formula).to_automaton(determinize=True) for formula in formulas[0]] , [parser(formula).to_automaton(determinize=True) for formula in formulas[1]] ]


images = [[],[]]

for goal in range(2):
  for i, dfa in enumerate(automatons[goal]):
   images[goal].append(dfa.to_dot())
   #cv2.imwrite("goal{},number{}.png".format(goal,i),dfa.to_dot() )
   #cv2.waitKey()


simulators = [ [DFASimulator(a) for a in automatons[0]] , [DFASimulator(a) for a in automatons[1]] ]


levelsDictionary = [ [dfa.levels_to_accepting_states() for dfa in automatons[0]] , [dfa.levels_to_accepting_states() for dfa in automatons[1]] ]


print(levelsDictionary[0])
print(levelsDictionary[1])
#              (                    d                    ,            dmax                      )
distances = [ [[ levelsDictionary[0][i][a.initial_state] , max(levelsDictionary[0][i].values()) ] for i,a in enumerate(automatons[0])] \
               , [[ levelsDictionary[1][i][a.initial_state] , max(levelsDictionary[1][i].values()) ] for i,a in enumerate(automatons[1])] \
            ] #<---------------[gpal 1 , goal 2 ]

print("distancesG1")
print(distances[0])
print("distancesG2")
print(distances[1])

fig, axes = plt.subplots(len(formulas[0]) + 1, 2, figsize=(8, 8))
probabilities = func.computeProbability(distances)

func.plot(fig, axes, formulas, images, probabilities)
print("probabilities")
print(probabilities)


#fig = plt.figure()
########################### CONNECTION TO VREP
clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
if clientID!= -1:
    print("Connected to remote server")
else:
    print('Connection not successful')
    sys.exit('Could not connect')

############################ HANDLES
errorcode, Pio =vrep.simxGetObjectHandle(clientID,'Bill',vrep.simx_opmode_oneshot_wait)
errorcode, Nao =vrep.simxGetObjectHandle(clientID,'Nao',vrep.simx_opmode_oneshot_wait)

err, vecchiaPioPos = vrep.simxGetObjectPosition(clientID, Pio, Nao, vrep.simx_opmode_oneshot_wait)
####################### MAIN LOOP

while (vrep.simxGetConnectionId(clientID) != -1 ):
################################################################# calcolo azioni svolte
    actionSet = set()
    #posa del Pio rispetto al Nao
    err, PioPos = vrep.simxGetObjectPosition(clientID, Pio, Nao, vrep.simx_opmode_oneshot_wait)
    #err, ori = vrep.simxGetObjectOrientation(clientID, Pio, -1, vrep.simx_opmode_oneshot_wait)

    #determino se sta a destra o a sinistra
    if PioPos[0] < - 1:
       actionSet.add('right')
    elif PioPos[0] > 1:
       actionSet.add('left')
    else:
       actionSet.add('center')

    # determino se si sta avvicinando o allontanando
    if fabs(PioPos[1]) < fabs(vecchiaPioPos[1]) - 0.01:
       actionSet.add('get_close')
    elif fabs(PioPos[1]) > fabs(vecchiaPioPos[1]) + 0.01:
       actionSet.add('get_far')
    else:
       actionSet.add('stop')

    # detremino se è nell'interaction area oppure no
    if math.sqrt(PioPos[0]**2 + PioPos[1]**2) < 1:
       actionSet.add('interaction_area')

    vecchiaPioPos = PioPos    
    actionSet = frozenset(actionSet)

################################################################ calcolo probabilita

    for goal in range(2):
     for i,s in enumerate(simulators[goal]):
      #print(s.dfa.alphabet.symbols)
      print("#####{}#####".format(i))
      print("current state")
      print(s.cur_state)
      action = actionSet.intersection(simboliFormule[goal][i])

      print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! AZIONE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1')
      print(actionSet)

      for symbol in s.dfa.alphabet.symbols:
        m = symbol._members()
        if m == frozenset({}):
          empty = symbol
          print("TROVATO EMPTY")

        if m == action:
          trovato = True
          print("trovato!!")
          actionToDo = symbol		 

      if not trovato:
        actionToDo = empty

      print('actionSet')  
      print(actionSet)      
      print('action')   
      print(action)          
      print('actionToDo')  
      print(actionToDo) 
        
      s.make_transition(actionToDo)
      levels =levelsDictionary[goal][i]
      cur_level=levels[s.cur_state]
      print(cur_level)
      distances[goal][i][0] = cur_level

      images[goal][i] = s.dfa.to_dot()
      #cv2.imshow("automa {}".format(i),s.dfa.to_dot() )
      #cv2.waitkey(10)


    probabilities = func.computeProbability(distances)
    print("probabilities")
    print(probabilities)  

    ##plottare GRAFI + ISTOGRAMMA
    func.plot(fig, axes, formulas, images, probabilities)

  

vrep.simxFinish(clientID)
sys.exit()


