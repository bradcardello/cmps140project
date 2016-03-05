# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveAlphaBetaAgent', second = 'DefensiveAlphaBetaAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  # # print "firstIndex: ", firstIndex
  # # print "secondIndex: ", secondIndex
  # # print "isRed: ", isRed
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class AlphaBetaCaptureAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    # self.evaluationFunction = util.lookup('evaluate', globals())
    self.evaluationFunction = gameState.getScore()
    self.myTeam = self.getTeam(gameState)
    self.opponents = self.getOpponents(gameState)
    print "Opponents for agent ", self.index, "are ", self.opponents
    self.agentIndices = sorted(self.myTeam + self.opponents)
    self.treeDepth = 2 # int('1') didn't break either


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    return random.choice(actions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def findAlphaBetaAction(self, gameState):
      # called recursively in minValue()
      def maxValue(gameState, depth, evaluation, remainingAgents, alpha, beta):
          # depth == 0 means the bottom of the tree (just a reminder to myself)
          isTerminal = (depth == 0 or gameState.isOver())

          # if you've reached a terminal state, calculate score
          if isTerminal:
              # # print "HELLO"
              return evaluation

          # v = -infinity
          v = -(float("inf"))

          # for each action, recursively determine the max value of the associated state
          #     For the top of the tree, compare -infinity to the value that MIN chooses
          # First parameter for generateSuccessor() is 0 because 0 represents Pacman (MAX)
          #legalActions = gameState.getLegalActions(0)
          print "MAX"
          agentIndex = random.choice(remainingAgents)
          print "Index to be popped: ", agentIndex
          remainingAgents.remove(agentIndex)
          print "remaining agents after being popped: ", remainingAgents
          for a in gameState.getLegalActions(agentIndex):
              evaluation = self.evaluate(gameState, a)
              if agentIndex in self.opponents:
                  v = max(v, minValue(gameState.generateSuccessor(agentIndex, a), depth - 1, evaluation, remainingAgents, alpha, beta))
              elif agentIndex in self.myTeam:
                  v = max(v, maxValue(gameState.generateSuccessor(agentIndex, a), depth - 1, evaluation, remainingAgents, alpha, beta))
              if v >= beta:
                  return v
              alpha = max(alpha, v)

          return v

      # called recursively in maxValue()
      def minValue(gameState, depth, evaluation, remainingAgents, alpha, beta):
          # depth == 0 means the bottom of the tree
          isTerminal = (depth == 0 or gameState.isOver())

          # if you've reached a terminal state, calculate score
          if isTerminal:
              return evaluation

          # v = infinity
          v = float("inf")

          # Now we loop over the set of legal actions we can take for this state
          # for each action, recursively determine the max value of the associated state
          #     For the top of the tree, compare -infinity to the value that MIN chooses
          print "MIN"
          agentIndex = random.choice(remainingAgents)
          print "Index to be popped: ", agentIndex
          remainingAgents.remove(agentIndex)
          print "remaining agents after being popped: ", remainingAgents
          for a in gameState.getLegalActions(agentIndex):
              evaluation = self.evaluate(gameState, a)
              if agentIndex in self.opponents:
                  v = min(v, minValue(gameState.generateSuccessor(agentIndex, a), depth - 1, evaluation, remainingAgents, alpha, beta))
                  # print gameState.generateSuccessor(agentIndex, a)
              elif agentIndex in self.myTeam:
                  v = min(v, maxValue(gameState.generateSuccessor(agentIndex, a), depth - 1, evaluation, remainingAgents, alpha, beta))
              if v <= alpha:
                  return v
              beta = min(beta, v)

          return v

      optimalAction = Directions.STOP # what Pacman thinks the best action is at the beginning
      utility = alpha = -(float("inf"))
      beta = float("inf")
      for a in gameState.getLegalActions(self.index):
          remainingAgents = self.agentIndices
          remainingAgents.pop(self.index)
          nextState = gameState.generateSuccessor(self.index, a)
          lastScore = utility
          # Recursively determine the maximimum utility possible for Pacman!
          evaluation = self.evaluate(gameState, a)
          utility = max(utility, minValue(nextState, self.treeDepth, evaluation, remainingAgents, alpha, beta))
          if utility > lastScore:
              optimalAction = a

          if utility >= beta:
              return optimalAction

      return optimalAction

  def findReflexAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    return random.choice(bestActions)

class EnemyState:
  """
  A GameState specifies the full game state, including the food, capsules,
  agent configurations and score changes.

  GameStates are used by the Game object to capture the actual state of the game and
  can be used by agents to reason about the game.

  Much of the information in a GameState is stored in a GameStateData object.  We
  strongly suggest that you access that data via the accessor methods below rather
  than referring to the GameStateData object directly.
  """

  ####################################################
  # Accessor methods: use these to access state data #
  ####################################################

  def getLegalActions( self, agentIndex=0 ):
    """
    Returns the legal actions for the agent specified.
    """
    return AgentRules.getLegalActions( self, agentIndex )

  def generateSuccessor( self, agentIndex, action):
    """
    Returns the successor state (a GameState object) after the specified agent takes the action.
    """
    # Copy current state
    state = EnemyState(self)

    # Find appropriate rules for the agent
    AgentRules.applyAction( state, action, agentIndex )
    AgentRules.checkDeath(state, agentIndex)
    AgentRules.decrementTimer(state.data.agentStates[agentIndex])

    # Book keeping
    state.data._agentMoved = agentIndex
    state.data.score += state.data.scoreChange
    state.data.timeleft = self.data.timeleft - 1
    return state

  def getAgentState(self, index):
    return self.data.agentStates[index]

  def getAgentPosition(self, index):
    """
    Returns a location tuple if the agent with the given index is observable;
    if the agent is unobservable, returns None.
    """
    agentState = self.data.agentStates[index]
    ret = agentState.getPosition()
    if ret:
      return tuple(int(x) for x in ret)
    return ret

  def getNumAgents( self ):
    return len( self.data.agentStates )

  def getScore( self ):
    """
    Returns a number corresponding to the current score.
    """
    return self.data.score

class OffensiveAlphaBetaAgent(AlphaBetaCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """

  def chooseAction(self, gameState):
    # Compute whether enemy is close or not
    noisyDistances = gameState.getAgentDistances()
    enemyNear = False
    prob = 0
    dist = 0
    for i in range(len(noisyDistances)): # 0 to 3
        # print "opponents for index ", i, "are: ", self.opponents
        if i in self.opponents:
            # print "i = ", i
            # for trueDistance in range(noisyDistances[i] - 6, noisyDistances[i] + 7): # if 0, range is [-6, 6]
            #     prob = gameState.getDistanceProb(trueDistance, noisyDistances[i])
            #     print "i = ", i
            #     print "my team:", self.myTeam
            #     print "distance = ", noisyDistances[i]
            #     print "true distance = ", trueDistance
            #     print "prob = ", prob
            #     if prob == 1:
            #         noisyDistances[i] = trueDistance
            #         print "I found it ya bish"
            #         break
            if noisyDistances[i] <= 7:
                dist = noisyDistances[i]
                enemyNear = True
                print "ENEMY NEAR YOU FUCK"
                break

    # Create set of possible positions for enemies (PUT IN ENEMYSTATE LATER)
    possiblePositions = []
    myPos = gameState.getAgentPosition(self.index)
    isEven = (dist % 2 == 0)
    i = 0
    j = dist
    if isEven:
        # Loop forwards from 0 to dist/2, while looping backwards from dist to dist/2
        # By doing this, we make sure to include all possible (x,y) coordinates
        while (i <= dist / 2) and (j >= dist / 2) :
            possiblePositions += (self.setUpPositions(gameState, i, j, myPos[0], myPos[1]))
            i += 1
            j -= 1
    else:
        # A little different if your distance is an odd number, but same concept
        while (i <= dist / 2) and (j >= dist / 2 + 1):
            possiblePositions += (self.setUpPositions(gameState, i, j, myPos[0], myPos[1]))
            i += 1
            j -= 1

    # print "dist = ", dist
    # print "possiblePositions: ", possiblePositions
    # print "possiblePositions length: ", len(possiblePositions)

    # Compute best action if in danger, otherwise, use simple reflex agent action
    action = None
    if enemyNear:
        action = self.findAlphaBetaAction(gameState)
    else:
        action = self.findReflexAction(gameState)
    return action

  def setUpPositions(self, gameState, i, j, x, y):
      possiblePositions = []
      possiblePositions.append( (x + i, y + j) )
      possiblePositions.append( (x + j, y + i) )
      possiblePositions.append( (x + i, y - j) )
      possiblePositions.append( (x - i, y + j) )
      if (i != 0 and j != 0) and (i != j):
          possiblePositions.append( (x + j, y - i) )
          possiblePositions.append( (x - j, y + i) )
          possiblePositions.append( (x - i, y - j) )
          possiblePositions.append( (x - j, y - i) )
      # print "actions are", possiblePositions
      for pos in possiblePositions:
          if gameState.hasWall(pos[0], pos[1]):
              possiblePositions.remove(pos)
      return possiblePositions

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1}


class DefensiveAlphaBetaAgent(AlphaBetaCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def chooseAction(self, gameState):
    return self.findReflexAction(gameState)


  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
