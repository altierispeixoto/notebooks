# -*- coding: utf-8 -*-

"""
Spyder Editor

http://archive.ics.uci.edu/ml/datasets/Dorothea
http://archive.ics.uci.edu/ml/datasets/Arcene
http://clopinet.com/isabelle/Projects/NIPS2003/

http://www.pykriging.com/
http://deeplearning.net/datasets/
http://www.facom.ufu.br/~backes/pgc204/Aula10-SelecaoAtributos.pdf
https://medium.com/@fabiolenine/como-selecionar-atributos-para-resolver-a-maldi%C3%A7%C3%A3o-da-dimensionalidade-5c810bc8449f

Este é um arquivo de script temporário.
"""  

import pylab
from random import *
import pandas as pd
import numpy as np
import inspyred
from inspyred import ec
from sklearn.metrics import accuracy_score, f1_score
from sklearn import svm
from sklearn.neural_network import MLPClassifier
import time
from time import time
import math

X_dataset = pd.read_csv('arcene_train.data.txt', sep=' ',header=None).iloc[:, 0:10000]
Y_dataset = pd.read_csv('arcene_train.labels.txt',header=None)

X_test = pd.read_csv('arcene_valid.data.txt', sep=' ',header=None).iloc[:, 0:10000]
Y_test = pd.read_csv('arcene_valid.labels.txt',header=None)

#r = Random()
#r.seed(42)

r = Random()
r.seed(int(time()))

randbinlist = lambda n: [randint(0, 1) for b in range(1, n + 1)]


def file_observer(population, num_generations, num_evaluations, args):

    log_file = args['log_file']
    statistics_file = open(log_file+'-statistics-file.csv', 'a+')


    stats = inspyred.ec.analysis.fitness_statistics(population)
    worst_fit = stats['worst']
    best_fit = stats['best']
    avg_fit = stats['mean']
    med_fit = stats['median']
    std_fit = stats['std']

    population.sort(reverse=True)
    n_feat = np.count_nonzero(population[0].candidate)

    candidate = population[0].candidate
    col_positions =[]
    for i in range(len(candidate)):
        if candidate[i] == 1:
            col_positions.append(i)

    train = X_dataset.iloc[:, col_positions]
    test = X_test.iloc[:, col_positions]

    clf = svm.SVC(kernel="linear")
    model = clf.fit(train, np.ravel(Y_dataset))
    predictions = model.predict(test)

    accuracy = accuracy_score(np.ravel(Y_test), predictions)

    statistics_file.write(
        '{0}, {1}, {2}, {3}, {4}, {5}, {6},{7}, {8}\n'.format(num_generations, len(population),n_feat,accuracy, worst_fit, best_fit, med_fit,avg_fit, std_fit))
    statistics_file.flush()




def generate_candidates(random, args):
    bits = args.get('num_bits', 8)
    return [random.choice([0, 1]) for i in range(bits)]


def my_constraint_function(candidate,args):

    """ train and return fscore from model trained """
    avaliation_method = args.get('avaliation_method', f1_score)
    ml_classifier = args.get('ml_classifier', f1_score)

    col_positions =[]
    for i in range(len(candidate)):
        if candidate[i] == 1:
            col_positions.append(i)

    train = X_dataset.iloc[:, col_positions]
    test = X_test.iloc[:, col_positions]


    model = ml_classifier.fit(train, np.ravel(Y_dataset))
    predictions = model.predict(test)

    #print("{} {} ".format(candidate, accuracy_score(Y_test, predictions)))
    alpha = 0.37
    feat_norm = 1 - ((np.count_nonzero(candidate)-1)/(10000-1))
    acc = avaliation_method(np.ravel(Y_test), predictions)
    #return ((acc + feat_norm) / 2)
    #return (acc + (feat_norm + (math.pow(feat_norm,2) )))
    #return (acc + (math.pow(feat_norm,2) ))
    #return ((1 - alpha) * acc ) + ((1 + alpha) * feat_norm)
    return acc + math.exp(feat_norm)

def my_evaluator(candidates, args):
    fitness = []
    for c in candidates:
        """ append f1_score on fitness trained """
        fitness.append(my_constraint_function(c,args))
    return fitness



def ga_feat_selection(display=False):
    import time
    start_time = time.time()

    myga = inspyred.ec.GA(r)
    myga.observer = [ ec.observers.stats_observer,file_observer] #inspyred.ec.observers.plot_observer,
    myga.replacer = inspyred.ec.replacers.plus_replacement #inspyred.ec.replacers.plus_replacement
    myga.terminator = inspyred.ec.terminators.generation_termination #inspyred.ec.terminators.evaluation_termination
    #myga.selector   = inspyred.ec.selectors.tournament_selection
    myga.variator = [inspyred.ec.variators.bit_flip_mutation,inspyred.ec.variators.n_point_crossover]
    #myga.evaluator = ec.evaluators.parallel_evaluation_mp
    #myga.analysis = ec.analysis.allele_plot,ec.analysis.generation_plot

    final_pop = myga.evolve(generator=generate_candidates,
                      evaluator=inspyred.ec.evaluators.parallel_evaluation_mp,
                      mp_evaluator=my_evaluator,
                      mp_nprocs=8,
                      pop_size=110,
                      maximize=True,
                      num_elites=3,
                      mutation_rate=0.001,
                      crossover_rate=0.9,
                      max_generations=20000,
                      num_bits=X_dataset.shape[1],
                      ml_classifier= svm.SVC(kernel="linear"),
                      avaliation_method = accuracy_score,
                      num_crossover_points=1,
                      log_file="svc_classifier_euler_20000")

    final_pop.sort(reverse=True)
    print('Terminated due to {0}.'.format(myga.termination_cause))

    print(final_pop[0])

    print(np.count_nonzero(final_pop[0].candidate))

    candidate = final_pop[0].candidate
    col_positions =[]
    for i in range(len(candidate)):
        if candidate[i] == 1:
            col_positions.append(i)

    train = X_dataset.iloc[:, col_positions]
    test = X_test.iloc[:, col_positions]

    clf = svm.SVC(kernel="linear")
    model = clf.fit(train, np.ravel(Y_dataset))
    predictions = model.predict(test)

    print("Fitness {}".format(final_pop[0].fitness))
    print("Chromossome normalized factor {}".format(1 - (np.count_nonzero(candidate)-1)/(10000-1)))
    print("Accuracy {}".format(accuracy_score(np.ravel(Y_test), predictions)))

    print("Feature reduction {}%".format(((10000-np.count_nonzero(final_pop[0].candidate))/10000)*100))

    e = int(time.time() - start_time)
    print('{:02d}:{:02d}:{:02d}'.format(e // 3600, (e % 3600 // 60), e % 60))


if __name__ == '__main__':
    ga_feat_selection(display=True)
