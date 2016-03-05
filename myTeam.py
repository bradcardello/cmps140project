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


class OffensiveAlphaBetaAgent(AlphaBetaCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """

  def chooseAction(self, gameState):
    distances = gameState.getAgentDistances()
    print "distances: ", observation
    # for i in range(len(distances)):
    #     print "Agent ", i, " has probaability ", gameState.getDistanceProb(i)

    if

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
        print "Offensive MAX"
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
        print "Offensive MIN"
        agentIndex = random.choice(remainingAgents)
        print "Index to be popped: ", agentIndex
        remainingAgents.remove(agentIndex)
        print "remaining agents after being popped: ", remainingAgents
        for a in gameState.getLegalActions(agentIndex):
            evaluation = self.evaluate(gameState, a)
            if agentIndex in self.opponents:
                v = min(v, minValue(gameState.generateSuccessor(agentIndex, a), depth - 1, evaluation, remainingAgents, alpha, beta))
                print gameState.generateSuccessor(agentIndex, a)
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
    print "myTeam: ", self.myTeam

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
        print "Defensive MAX"
        agentIndex = random.choice(remainingAgents)
        print "Index to be popped: ", agentIndex
        remainingAgents.remove(agentIndex)
        print "remaining agents after being popped: ", remainingAgents
        for a in gameState.getLegalActions(agentIndex):
            evaluation = self.evaluate(gameState, a)
            if agentIndex in self.opponents:
                v = max(v, maxValue(gameState.generateSuccessor(agentIndex, a), depth - 1, evaluation, remainingAgents, alpha, beta))
            elif agentIndex in self.myTeam:
                v = max(v, minValue(gameState.generateSuccessor(agentIndex, a), depth - 1, evaluation, remainingAgents, alpha, beta))

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
        print "Defensive MIN"
        agentIndex = random.choice(remainingAgents)
        print "Index to be popped: ", agentIndex
        remainingAgents.remove(agentIndex)
        print "remaining agents after being popped: ", remainingAgents
        for a in gameState.getLegalActions(agentIndex):
            # # print "agentIndex = ", agentIndex
            evaluation = self.evaluate(gameState, a)
            if agentIndex in self.opponents:
                v = min(v, maxValue(gameState.generateSuccessor(agentIndex, a), depth - 1, evaluation, remainingAgents, alpha, beta))
            elif agentIndex in self.myTeam:
                v = min(v, minValue(gameState.generateSuccessor(agentIndex, a), depth - 1, evaluation, remainingAgents, alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)

        return v

    # subtract 1 to exclude Pacman
    optimalAction = Directions.STOP # what Pacman thinks the best action is at the beginning
    utility = alpha = -(float("inf"))
    beta = float("inf")
    for a in gameState.getLegalActions(self.index):
        remainingAgents = self.agentIndices
        remainingAgents.remove(self.index)
        nextState = gameState.generateSuccessor(self.index, a)
        lastScore = utility
        evaluation = self.evaluate(gameState, a)
        # Recursively determine the minimum utility possible
        utility = min(utility, maxValue(nextState, self.treeDepth, evaluation, remainingAgents, alpha, beta))
        if utility < lastScore:
            optimalAction = a

        if utility >= beta: # MIGHT FUCK SHIT UP
            return optimalAction

    return optimalAction

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
