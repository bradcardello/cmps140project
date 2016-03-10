# myTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def chooseAction(self, gameState):
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

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = successor.getAgentState(self.index).getPosition()
    features['successorScore'] = self.getScore(successor)

    # Computes whether we're on defense (1) or offense (0)
    # features['onDefense'] = 1
    # if myState.isPacman: features['onDefense'] = 0

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    defenders = [a for a in enemies if not a.isPacman and myState.isPacman and a.getPosition() != None]
    # print enemies[0], "       ", enemies[1]
    features['numDefenders'] = len(defenders)
    if len(defenders) > 0 and features['onDefense'] == 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
      features['defenderDistance'] = min(dists)


    # scaredDefenders = [a for a in enemies if not a.isPacman and a.scaredTimer == 0 and a.getPosition() != None]
    # features['numDefenders'] = -1 * len(defenders)
    # if len(scaredDefenders) > 0 and features['onDefense'] == 0:
    #   scaredDists = [self.getMazeDistance(myPos, a.getPosition()) for a in scaredDefenders]
    #   features['defenderDistance'] = -1 * min(scaredDists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    # capsuleList = []
    # features['distToCapsule'] = 0
    # if (gameState.isOnRedTeam(self.index)):
    #     capsuleList = gameState.getBlueCapsules()
    # else:
    #     capsuleList = gameState.getRedCapsules()
    # print "Capsules: ", capsuleList
    # if len(capsuleList) > 0:
    #     distToCapsule = min((self.getMazeDistance(myPos, capsule) for capsule in capsuleList))
    #     features['distToCapsule'] = distToCapsule

    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'defenderDistance': 1, 'numDefenders': -1000, 'stop': -100, 'reverse': -2}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

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
    # print enemies[0], "       ", enemies[1]
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

  def findAlphaBetaAction(self, gameState, enemyState):
      # called recursively in minValue()
      def maxValue(gameState, enemyState, depth, evaluation, remainingAgents, alpha, beta):
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


          if agentIndex in self.opponents:
              for a in enemyState.getPossibleActions(gameState, enemyState, enemyState.getAgentPosition(agentIndex)):
                  evaluation = self.evaluate(gameState, a)
                  v = max(v, minValue(enemyState.generateSuccessor(agentIndex, a), enemyState, depth - 1, evaluation, remainingAgents, alpha, beta))
                  if v >= beta:
                      return v
                  alpha = max(alpha, v)
          elif agentIndex in self.myTeam:
              for a in gameState.getLegalActions(agentIndex):
                  evaluation = self.evaluate(gameState, a)
                  v = max(v, maxValue(gameState.generateSuccessor(agentIndex, a), enemyState, depth - 1, evaluation, remainingAgents, alpha, beta))
                  if v >= beta:
                      return v
                  alpha = max(alpha, v)



        #   for a in gameState.getLegalActions(agentIndex):
        #       evaluation = self.evaluate(gameState, a)
        #       if agentIndex in self.opponents:
        #           v = max(v, minValue(enemyState.generateSuccessor(agentIndex, a), enemyState, depth - 1, evaluation, remainingAgents, alpha, beta))
        #       elif agentIndex in self.myTeam:
        #           v = max(v, maxValue(gameState.generateSuccessor(agentIndex, a), enemyState, depth - 1, evaluation, remainingAgents, alpha, beta))
        #       if v >= beta:
        #           return v
        #       alpha = max(alpha, v)

          return v

      # called recursively in maxValue()
      def minValue(gameState, enemyState, depth, evaluation, remainingAgents, alpha, beta):
          # if you've reached a terminal state, calculate score
          isTerminal = (depth == 0 or gameState.isOver())
          if isTerminal:
              return evaluation
          v = float("inf")

          # Now we loop over the set of legal actions we can take for this state
          # for each action, recursively determine the max value of the associated state
          #     For the top of the tree, compare -infinity to the value that MIN chooses
          print "MIN"
          agentIndex = random.choice(remainingAgents)
          print "Index to be popped: ", agentIndex
          remainingAgents.remove(agentIndex)
          print "remaining agents after being popped: ", remainingAgents
          print "Enemy position is ", enemyState.getAgentPosition(agentIndex)

          if agentIndex in self.opponents:
              for a in enemyState.getPossibleActions(gameState, enemyState, enemyState.getAgentPosition(agentIndex)):
                  evaluation = self.evaluate(gameState, a)
                  v = min(v, minValue(enemyState.generateSuccessor(agentIndex, a), enemyState, depth - 1, evaluation, remainingAgents, alpha, beta))
                  if v <= alpha:
                      return v
                  beta = min(beta, v)
          elif agentIndex in self.myTeam:
              for a in gameState.getLegalActions(agentIndex):
                  evaluation = self.evaluate(gameState, a)
                  v = min(v, maxValue(gameState.generateSuccessor(agentIndex, a), enemyState, depth - 1, evaluation, remainingAgents, alpha, beta))
                  if v <= alpha:
                      return v
                  beta = min(beta, v)


        # for a in enemyState.getPossibleActions(gameState, enemyState, enemyState.getAgentPosition(agentIndex)):
        #       evaluation = self.evaluate(gameState, a)
        #       if agentIndex in self.opponents:
        #           v = min(v, minValue(enemyState.generateSuccessor(agentIndex, a), enemyState, depth - 1, evaluation, remainingAgents, alpha, beta))
        #           # print gameState.generateSuccessor(agentIndex, a)
        #       elif agentIndex in self.myTeam:
        #           v = min(v, maxValue(gameState.generateSuccessor(agentIndex, a), enemyState, depth - 1, evaluation, remainingAgents, alpha, beta))
        #       if v <= alpha:
        #           return v
        #       beta = min(beta, v)

          return v

      optimalAction = Directions.STOP # what Pacman thinks the best action is at the beginning
      utility = alpha = -(float("inf"))
      beta = float("inf")
      for a in gameState.getLegalActions(self.index):
          remainingAgents = self.agentIndices # pass this in as list of defenders
          remainingAgents.pop(self.index)
          nextState = gameState.generateSuccessor(self.index, a)
          lastScore = utility
          # Recursively determine the maximimum utility possible for Pacman!
          evaluation = self.evaluate(gameState, a)
          utility = max(utility, minValue(nextState, enemyState, self.treeDepth, evaluation, remainingAgents, alpha, beta))
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

class OffensiveAlphaBetaAgent(AlphaBetaCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """

  def chooseAction(self, gameState):
    enemies = util.Counter()
    enemyPositions = util.Counter()
    defenders = []
    # link enemy indices to their AgentStates
    for i in self.getOpponents(gameState):
        print "Enemy index is ", i
        enemies[i] = gameState.getAgentState(i)
        if not enemies[i].isPacman and enemies[i].getPosition() != None:
            enemyPositions[i] = enemies[i].getPosition()
            defenders.append(enemies[i])
    # for i in self.getOpponents(gameState)):
        # if not enemies[i].isPacman and enemies[i].getPosition() != None:
        #     defenders.append(enemies[i])
    print "Defenders are ", defenders

    # enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    # defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]

    # Compute best action if in danger, otherwise, use simple reflex agent action
    action = None
    if len(defenders) > 0:
      myAgentState = gameState.getAgentState(self.index)
      myPos = myAgentState.getPosition()
      defenderDists = util.Counter()
      for a in defenders:
        defenderDists[a] = self.getMazeDistance(myPos, a.getPosition())
      print "DOING AlphaBeta"
      enemyState = EnemyState(gameState, a.getPosition(), defenders, defenderDists, enemyPositions)
      "The enemy state is ", enemyState
      action = self.findAlphaBetaAction(gameState, enemyState)
      print "FINISHED AlphaBeta"
      print "Defenders distances are ", dists
    else:
      action = self.findReflexAction(gameState)
    return action

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

    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    if len(defenders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
      features['defenderDistance'] = min(dists)
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'defenderDistance': -10}


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

  def __init__( self, gameState, myPos, enemies, enemyDists, enemyPositions ):
    self.gameState = gameState
    self.myPos = myPos
    self.enemies = enemies # Counter with (agentIndex, AgentState) pairs
    self.enemyDists = enemyDists # Counter with (AgentState, distFromMyPos) pairs
    self.enemyPositions = enemyPositions # Counter with (agentIndex, position) pairs


  def setUpPossibleActions(self, gameState, possiblePositions):
      possibleActionsFromPos = util.Counter()
      for pos in possiblePositions:
          possibleActionsFromPos[pos] = self.getPossibleActions(gameState, pos)
          print "From position ", pos, " you can move ", possibleActionsFromPos[pos]
      return possibleActionsFromPos

  def getPossibleActions(gameState, enemyState, config):
    possible = []
    print "config = ", config
    x = config[0]
    y = config[1]
    x_int, y_int = int(x + 0.5), int(y + 0.5)

    # In between grid points, all agents must continue straight
    if (abs(x - x_int) + abs(y - y_int)  > .001):
      return [config.getDirection()]

    for dir, vec in Actions._directionsAsList:
      dx, dy = vec
      next_y = y_int + dy
      next_x = x_int + dx
      if not gameState.hasWall(next_x, next_y): possible.append(dir)

    return possible

  getPossibleActions = staticmethod(getPossibleActions)

  def generateSuccessor( self, agentIndex, action):
    """
    Returns the successor state (an EnemyState object) after the specified agent takes the action.
    """
    # Copy current state
    state = EnemyState(self.gameState, self.myPos, self.enemies, self.enemyDists, self.enemyPositions  )

    # Find appropriate rules for the agent
    # AgentRules.applyAction( state, action, agentIndex )
    # AgentRules.checkDeath(state, agentIndex)

    # Book keeping
    # state.data._agentMoved = agentIndex
    # state.data.score += state.data.scoreChange
    # state.data.timeleft = self.data.timeleft - 1
    return state

  def getAgentState(self, index):
    return self.enemies[index]

  def getAgentPosition(self, index):
    return self.enemyPositions[index]

  def getNumAgents( self ):
    return len( self.data.agentStates )

  def getScore( self ):
    """
    Returns a number corresponding to the current score.
    """
    return self.data.score
