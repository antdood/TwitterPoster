import pickle
import random
import pathlib

selection_history_file = "selectionHistory.txt"

def selectRandom(selection_set):
	weighted_selection_set = getSelectionWeights(selection_set)

	zeroed_selection_set = zeroNegativeWeights(weighted_selection_set)

	try:
		choice = random.choices(list(zeroed_selection_set.keys()), weights = list(zeroed_selection_set.values()))[0]
	except ValueError:
		choice = random.choice(selection_set)
		weighted_selection_set = {candidate : len(selection_set) for candidate in selection_set}

	adjusted_weights = adjustWeights(choice, weighted_selection_set)

	writeSelectionWeights(adjusted_weights)

	return choice

def getSelectionWeights(selection_set):
	selection_history = {}
	with open(getSelectionHistoryPath(), "rb") as file:
		selection_history = pickle.load(file)

	out = {}

	for candidate in selection_set:
		if(candidate in selection_history):
			out[candidate] = selection_history[candidate]
		else:
			out[candidate] = len(selection_set)

	return out

def zeroNegativeWeights(selection_weights):
	copy = {}
	for candidate in selection_weights:
		copy[candidate] = max(0,selection_weights[candidate])
	return copy

def adjustWeights(selection, selection_weights):
	selection_weights[selection] = int(len(selection_weights)/2) * -1

	for candidate in selection_weights:
		selection_weights[candidate] += 1

	return selection_weights

def writeSelectionWeights(selection_weights):
	with open(getSelectionHistoryPath(), "wb") as file:
		pickle.dump(selection_weights, file)

def getSelectionHistoryPath():
	return pathlib.Path(__file__).parent / selection_history_file
