import csv
import pandas as pd
import numpy as np
from collections import Counter


def read_csv(filename):
    lst = []
    
    with open(filename) as f:
        csv_reader = csv.reader(f)

        for row in csv_reader:
            lst.extend(map(float, row))
    
    return lst


def remove_outliers(data):
    data = np.sort(data)

    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)

    IQR = Q3 - Q1

    lower_bound = Q1 - (1.5 * IQR)
    upper_bound = Q3 + (1.5 * IQR)

    # find indices of outliers
    idx_outliers = np.argwhere((data < lower_bound) | (data > upper_bound))

    # remove outliers
    data = np.delete(data, idx_outliers)
    
    return data


def mmc(data):
    n = len(data)

    # number of classes
    K = np.ceil( 1 + (3.3 * np.log10(n)) )

    # class size
    h = max(data) / K 

    # generate classes
    initial_class = [0.0, h]
    classes = [initial_class]
    
    i = 1
    while len(classes) != K:
        new_class = [x + (i*h) for x in initial_class]
        classes.append(new_class)

        i += 1
    
    # absolute frequency
    lst = []
    for i in data:  # element in data
        for idx_c in range(len(classes)):  # index of class
            if i >= classes[idx_c][0] and i <= classes[idx_c][1]:
                lst.append(idx_c)  # store index
    
    # Store absolute Frequency in a Counter Dict
    abs_freq = Counter(lst)

    for key, value in abs_freq.items():
        abs_freq[key] = value / len(data)

    # comulative frequency
    c_freq = []
    aux = 0  # sum of frequencies
    for value in abs_freq.values():
        aux += value
        c_freq.append(aux)
    
    # generating intervals
    initial_interval = [0.0, c_freq[0]]
    intervals = [initial_interval]

    i = 1
    while len(intervals) != K:
        new_interval = []

        # get places after decimal point
        places = len(str(c_freq[i - 1]).split('.')[1])

        new_interval = [c_freq[i - 1] + 10**(-1 * places), c_freq[i]]

        intervals.append(new_interval)

        i += 1
    
    # create a pandas dataframe with relevant data
    df = pd.DataFrame({'Classes' : pd.Series(classes), 'Frequência': pd.Series(abs_freq),
                       'Frequência Acumulada': pd.Series(c_freq), 'Intervalo de Valores': pd.Series(intervals)})
    
    return df
