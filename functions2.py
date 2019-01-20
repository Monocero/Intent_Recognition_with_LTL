#cambiare i nomi dei simboli in inglese (V)
#aggiungere interaction_area (quando sta dentro a un cerciho di un certo raggio) (V)
#mettere gli agenti su vrep più carini
#mettere formula di probabilità nuova

'''
def computeProbability(distances):
    print(distances)
    s = sum(d for d in distances if d >= 0)
    probabilities = []
    for d in distances:
      if s == 0:
        return [1/len(distances) for i in range(len(distances))]
      if d < 0:
        probabilities.append(0)
      else:
        probabilities.append(1 - d/s)
    return probabilities    
'''
def computeProbability(distances):

  goals = 2
  p = [[] for g in range(goals)]
  for g in range(goals):
    #i = 0
    for d, dmax in distances[g]:
          if d >= 0:
            p[g].append((dmax - d)/dmax)
          else:
            p[g].append(0) #<-----------------------caso stato non raggiungibile
          #i += 1
  ss = [sum(pp) for pp in p]	
  s = sum(ss)
	
  pGoals = []

  for g in range(goals):
    if ss[g] == 0:
      pGoals.append(0)
    else:
      pGoals.append(ss[g] / s)

  print(pGoals)

  return pGoals


def plot(fig, axes, formulas, imageGraph, probabilities):
  print(len(imageGraph))
  print(len(imageGraph[0]))
  print(len(imageGraph[1]))
  for goal in range(len(probabilities)):
    for i in range(len(formulas[goal])):
      axes[i, goal].set_title(formulas[goal][i])
      axes[i, goal].rect = []
      axes[i, goal].imshow(imageGraph[goal][i], aspect=1)
      axes[i, goal].set_xticks([])
      axes[i, goal].set_yticks([])

    axes[i+1, goal].clear()
    if goal == 0:
      axes[i+1, goal].set_title("P(user goal = INTERACT)")
    else:
      axes[i+1, goal].set_title("P(user goal = NOT INTERACT)")
    axes[i+1, goal].set_ylim(0,1)
    axes[i+1, goal].bar(0.4, probabilities[goal])
    axes[i+1, goal].set_xticks([])
    
    fig.tight_layout()
    fig.show()
    fig.canvas.draw()

