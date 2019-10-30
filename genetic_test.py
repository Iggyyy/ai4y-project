from genetic_calculator import *
from tensorflow import keras

def normalize(array):
    return (array - array.min(0)) / array.ptp(0)

raw_data = np.load("capresults.npy", allow_pickle=True)

# del datapoints with empty vectors
mask = np.ones(len(raw_data), dtype=bool)
data = np.zeros((len(raw_data), 13), dtype='O')

for i, dp in enumerate(raw_data):
    if (dp[3].size is 0 or dp[5].size is 0):
        mask[i] = False
    
    flattened = np.concatenate([[*dp[0], *dp[1], *dp[2]], dp[3], [dp[4]], dp[5]], axis=0).astype('float32')
    if flattened.shape[0] is data.shape[1]:
        data[i] = flattened
del raw_data

data = data[mask, ...]

# split into training and testing sets
mask = np.random.choice([True, False], len(data), p=[0.75, 0.25])

training_data = data[mask, ...][:, 2:]
training_labels = data[mask, ...][:, :2]

mask = ~mask

testing_data = data[mask, ...][:, 2:]
testing_labels = data[mask, ...][:, :2]

norm_training_data = normalize(training_data)
norm_training_labels = normalize(training_labels)

del data

def model_fitness(tpl):
    global training_data, training_labels, norm_training_data, norm_training_labels, testing_data, testing_labels

    model = keras.Sequential()
    model.add(keras.Input(shape=(11,), name='data'))

    for layer in tpl.layers:
        model.add(keras.layers.Dense(layer[0], activation=layer[1]))

    model.add(keras.layers.Dense(2, activation=tpl.out_ac, name='output'))

    model.compile(optimizer='adam', loss='mean_absolute_error')

    if tpl.norm:
        model.fit(norm_training_data, norm_training_labels, epochs=tpl.epochs)
    else:
        model.fit(training_data, training_labels, epochs=tpl.epochs)

    return model.evaluate(testing_data, testing_labels, verbose=0)

# initial population??

gen_calc = GeneticCalculator(pop, model_fitness)