import argparse
import string
import sys
from math import exp, sqrt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

###### Parameters for ranking system
StartingRank = 1000.0
KfactorBase = 40 # adjusts speed ranking updates
KfactorCoef = (1.5, 1) # % of key factor base. K1 - new players, K2 - old players
KfactorCriteria = 5 # if =< x games, Kfactor1 applies, else k2
CDFSigma = 100
### Initialize global variables
pl = {} # define dict for player class instances
sampledb = pd.DataFrame(columns=('Team1','Team2','Score'))
playerList = []
### read external scores file. file format: csv: Team1,Team2,Score. Score:1 or 0 for Team1
scoredb = pd.read_csv('scores.csv')
print(scoredb.head())
print("Some scores read! Length of score file: {}".format(len(scoredb.index)))

# Trying to adjust two score system to one score. Currently without any success
def to_single_score(score1, score2):
    if score1 > score2:
        score = 0.5
    else:
        score = 0

    return  score + (float(score1) / float(score1 + score2)) * 0.5


for i in scoredb.index:
    scoredb.ix[i, 'Score'] = to_single_score(
        scoredb.iloc[i].Score1,
        scoredb.iloc[i].Score2,
    )

print(scoredb.head())

class player:
#    global StartingRank
    def __init__(self, name):
#        self.rank = 1111
        self.name = name
        self.rank = StartingRank
        self.gamesPlayed = 0
        self.KfactorCoef = KfactorCoef[0] # Kfactor coef for next game. Initialized for new players as 1
        self.stats = pd.DataFrame(columns=('GameNumber','Rank','Pwin')) # GameNumber = scoresDB index
        # Pwin - win probability
        # GameNumber - game ID whole system
        # Rank - Elo score. Servers as player rank

        # By default rank is StartingRank
        self.stats.set_value(0,'Rank',self.rank) 
        self.stats.set_value(0,'GameNumber',0)

    def update(self, newrank, ind, pwin):
        self.rank = newrank
        self.gamesPlayed += 1

        self.stats.set_value(ind + 1,'Rank', self.rank)
        self.stats.set_value(ind + 1,'Pwin', pwin)
        self.stats.set_value(ind + 1,'GameNumber', ind + 1)

        if self.gamesPlayed > KfactorCriteria:
            self.KfactorCoef = KfactorCoef[1]

# complementary function for Gaussian CDF:
def erfcc(x):
    z = abs(x)
    t = 1. / (1. + 0.5 * z) # Normal dist.
    r = t * exp(-z*z-1.26551223+t*(1.00002368+t*(.37409196+
    	t*(.09678418+t*(-.18628806+t*(.27886807+
    	t*(-1.13520398+t*(1.48851587+t*(-.82215223+
    	t*.17087277))))))))) 

    if (x >= 0.):
        return r
    else:
        return 2. - r

# Gaussian(normal) CDF:
def normcdf(x, mu, sigma):
    t = x-mu;
    y = 0.5*erfcc(-t/(sigma*sqrt(2.0)));
    if y>1.0:
        y = 1.0;

    return y

# Lognormal CDF. !!! Currently for whatever mathematical peculiarity interprets inputs as discrete integers of CDFsigma:
def logcdf(x,mu,sigma):
    res = 1/(1+exp(-(float(x)-mu)/sigma))
    return res

# Update unique players from scorefile. scoredb DataFrame as input:
def updateUnique(db):
    global playerList
    print("db type read: ", type(db))
    playerList =  sorted(np.unique(db[['Team1','Team2']]).tolist())
    print("unique players: ", playerList)


#Returns epxected score of player one as a function 2 ranks.:
def expectedScore(rank1,rank2):
        return logcdf((rank1-rank2),0,CDFSigma)


# updates player1 and player2 objects. Additional inputs: score for player1, game index in scoredb:
def game(p1,p2,score,ind,verbose):
# inputs are: player1 object, player2 object, score as real. Validation of inputs would be nice
    # Score given for team1. Score for team2= team1-1
    escore = expectedScore(p1.rank,p2.rank)
    deltarank1 = (score-escore)*KfactorBase*p1.KfactorCoef
    deltarank2 = (score-escore)*KfactorBase*p2.KfactorCoef
    p1.update(p1.rank+deltarank1,ind,escore)
    p2.update(p2.rank-deltarank2,ind,1-escore)

    if verbose :
        print("-" * 80)
        print("Game number: ", ind)
        print("The game is on!")
        print("Inputs are given:"
              " team1={} ,team2={} ,score={}: ".format(p1.name, p2.name, score))

        print("Rank difference", p1.name, " - ",p2.name," = ", (p1.rank -
            p2.rank))
        print("Expected probability of ", p1.name, " winning: ", round(escore, 5))
        print("Actual score for ", p1.name," is ", score)
        print("Games played by ", p1.name, p1.gamesPlayed)
        print("Games played by ", p2.name, p2.gamesPlayed)
        print("Rank update with Kfactor base", KfactorBase, " and KfactorCoef ",
                p1.KfactorCoef, " for ", p1.name, "is", deltarank1, ", for ",
                p2.name, " with KfactorCoef of ", p2.KfactorCoef," is ",
                -deltarank2, "new rank of ", p1.name, " is ", p1.rank, ", of ",
                p2.name, " ", p2.rank)


# Create player objects from players class. Names from playerList function. Namespace for addressing players pl['name'] pl=PL:
def createPlayers(playerListLocal):
    for name in playerListLocal:
        print("creating player ", name)
        pl[name] = player(name)


# Iterate over games in scoredb and run game function over each game:
def updateScores(db, verbose):
    for i in db.index:
        game(
            pl[db.iloc[i].Team1],
            pl[db.iloc[i].Team2],
            db.iloc[i].Score,
            i,
            verbose,
        )


# Draw dynamics of player ELO score:
def drawRankDynamics():
    for zz in playerList:
        plt.plot(pl[zz].stats['GameNumber'],pl[zz].stats['Rank'],label=pl[zz].name)

    plt.xlabel('Spelu skaits')
    plt.ylabel('Elo skoors')
    plt.title('Ranking dynamics.CDFSigma: '+str(CDFSigma)+', Kfactor: '+str(KfactorBase))
    plt.grid()
    plt.legend()
    plt.show()


# Misceallaneous analytics:
def analytics():
    print("----- Some analytics below ----")

    avgscore = 0.0
    for zz in pl:
        avgscore= avgscore + pl[zz].rank
#    print "Average score at the end: ",avgscore/len(pl)
#    print "Average score above 1000 means we have some score inflation. Some inflation is ok."
#    print "Current ranks are:"
#    for key in sorted(list(pl.keys())):
#        print pl[key].name, " : ", pl[key].rank
    print("Average Pwin: ",pl['a'].stats.mean(axis=0)[2])
    print("Stdev of Pwin: ", pl['a'].stats.std(0)[2])
    print("STDev/avg: ",pl['a'].stats.std(0)[2]/pl['a'].stats.mean(axis=0)[2])


# Print latest ELO scores and rank:
def latestRanking():
    ranks = pd.DataFrame()
    for name in playerList:
        ranks.set_value(name,'CurrentElo', round(pl[name].rank,0))
        ranks.set_value(name,'GamesPlayed',pl[name].gamesPlayed)
    ranks.sort(['CurrentElo'], ascending=False,inplace=True)
    ranks['CurrentRank'] = range(1,len(ranks)+1,1)
    print(ranks)


# Table for people to understand what they might gain or loose by playing a particular opponent:
def latestMutualGains():
    displayTable = pd.DataFrame(columns=playerList, index=playerList)
    for a in playerList:
        for b in playerList:
            deltarank2 = (1-expectedScore(pl[b].rank,pl[a].rank))*KfactorBase*pl[b].KfactorCoef
            deltarank1 = (1-expectedScore(pl[a].rank,pl[a].rank))*KfactorBase*pl[a].KfactorCoef
            displayTable[b][a]= str(round(deltarank2,0))+"|"+ str(round(-deltarank1,0))

    print("Table describes current potential Gains & Losses from next game")
    print("Read dis by rows. [X | Y] - X=points gained when row player wins, "
           " Y=points lost when col player loses")
    print(displayTable)

#Make sample games DataFrame called scoredb:
def makeSampleGames(numPlayers,numGames):
    global sampledb
    playerNamesList = pd.Series(index=list(string.ascii_lowercase),name='skill')
    samplePlayers = playerNamesList[0:numPlayers]
    for n in samplePlayers.index:
        samplePlayers[n] = np.random.random()
    print("Sample players created with following skill levels")
    print(samplePlayers)

    for i in range(numGames):
        Team1=list(samplePlayers.index)[int(np.random.random()*numPlayers)]  # select team1
        Team2= Team1
        while Team1==Team2:
            Team2=list(samplePlayers.index)[int(np.random.random()*numPlayers)]  # select team2
        score=0
        if samplePlayers[Team1] > np.random.random()*(samplePlayers[Team1]+samplePlayers[Team2]):
            score =1
        else:
            score =0
        sampledb.set_value(i,'Team1',Team1)
        sampledb.set_value(i,'Team2',Team2)
        sampledb.set_value(i,'Score',score)
    print("SampleDB created:", sampledb)


def run(db,verbose):
    makeSampleGames(2, 100)
    updateUnique(db)
    createPlayers(playerList)
    updateScores(db,verbose)

    analytics()
    latestRanking()
    drawRankDynamics()


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Verbose script output',
    )
    parser.add_argument(
        '-i',
        '--input',
        help='Score CSV file.',
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()

    if not args.input:
        _score_db = sampledb
    else:
        _score_db = scoredb

    sys.exit(run(_score_db, verbose=args.verbose))
