#!/usr/bin/python3

import os
import sys

from lxml import etree


def parser(file):
	parser = etree.XMLParser(encoding="UTF-8", recover=True)
	ntree = etree.parse(file, parser=parser)
	return ntree

def process(parse, path):
	for s in parse.iter('sentence'):
		sen = s.text.split()
	elements = parse.xpath("//node[@rel='mod']")
	mod_words = parse.xpath("//node[@rel='mod']/@word")
	begin_end = [(int(i),int(j)) for i,j in zip(parse.xpath("//node[@rel='mod']/@begin"), parse.xpath("//node[@rel='mod']/@end"))]
	mods = []
	sen_attrib = []
	for tup in begin_end:
		mod = " ".join(sen[tup[0]:tup[1]])
		mods.append(mod)
	for e,m in zip(elements, mods):
		element = e.attrib
		sen_attrib.append((m, element))
	return rules(sen, sen_attrib)
	

def rules(sentence, lst):
	del_mods = [] # makes a list for mods that are deletable
	for i in lst:
		mod = i[0]
		attributes = i[1]
		if attributes.get('begin') != None:
			if attributes.get('begin') != '0':
				if attributes.get('pb') != None:
					if attributes['pb'] == 'ArgM-DIS':
						del_mods.append(mod)
					elif attributes['pb'] == 'ArgM-LOC':
						if attributes.get('cat') != 'pp':
							del_mods.append(mod)
					elif attributes['pb'] == 'ArgM-TMP':
						if not mod.split()[0] == 'tijdens' and not mod.split()[0] == 'zelden':
							if attributes.get('cat') == None: # Checks if the modifier is a phrase
								del_mods.append(mod)
					elif attributes['pb'] == 'ArgM-ADV': # Only ArgM-ADV with length 1 are deletable as follows out of the form data
						if len(mod.split()) == 1 and mod.split()[0] != 'niet' :
							del_mods.append(mod)
						elif attributes.get('cat') == 'mwu':
							del_mods.append(mod)
					elif attributes['pb'] == 'ArgM-EXT':
						if attributes.get('cat') == None:
							del_mods.append(mod)
						elif attributes.get('cat') == 'pp' or attributes.get('cat') == 'mwu':# or attributes.get('cat') == 'ap':
							del_mods.append(mod)
					elif attributes['pb'] == 'ArgM-MNR':
						if attributes.get('cat') == None:
							if mod.split()[0] != 'verkeerd' and mod.split()[0] != 'goed' and mod.split()[0] != 'fout' and mod.split()[0] != 'juist': # Indicates negation so better to skip
								del_mods.append(mod)
				elif attributes.get('pt') != None:
					if attributes['pt'] == 'bw' and mod not in del_mods:
						if mod.split()[0] != 'zelden' and mod.split()[0] != 'te' and mod.split()[0] != 'niet' :
							del_mods.append(mod)
					elif attributes['pt'] == 'vnw' and attributes['postag'] == 'VNW(aanw,adv-pron,stan,red,3,getal)' or attributes['postag'] == 'VNW(aanw,det,stan,prenom,zonder,agr)':
						del_mods.append(mod)
					#elif attributes['pt'] == 'adj' and attributes['buiging'] == 'met-e' and attributes['postag'] == 'ADJ(prenom,basis,met-e,stan)':
					#	del_mods.append(mod)	# Filtering adjectives drops the accuracy too much
				#elif attributes.get('cat') != None:
					#if attributes.get('cat') == 'advp' and mod not in del_mods:
					#	del_mods.append(mod)
					#if attributes.get('cat') == 'mwu' and mod not in del_mods:
					#	del_mods.append(mod)
	return del_mods

def evaluate(original_sentence, new_sentence,  modifiers):
	new_modifiers = " ".join(modifiers).split() # To make it possible to delete modifiers of multiple words out of a sentence with list comprehension used below
	modified_sentence = [x for x in original_sentence if x not in new_modifiers]
	print("Gold standard sentence: ", " ".join(new_sentence), "Modified sentence: ", " ".join(modified_sentence))
	if " ".join(new_sentence) == " ".join(modified_sentence) and " ".join(original_sentence) != " ".join(modified_sentence): # True positive when sentence is correctly simplified
		return 'TP'
	elif " ".join(new_sentence) == " ".join(modified_sentence) and " ".join(original_sentence) == " ".join(modified_sentence): # True negative when sentence is correctly NOT simplified
		return 'TN'
	elif " ".join(new_sentence) != " ".join(modified_sentence) and " ".join(original_sentence) != " ".join(modified_sentence): # False positive when sentence is incorrectly simplified
		return 'FP'
	elif " ".join(new_sentence) != " ".join(modified_sentence) and " ".join(original_sentence) == " ".join(modified_sentence) : # False negative when sentence is incorrectly NOT simplified
		return 'FN'

def main():
	num = 0
	true_positive = 0
	true_negative = 0
	false_positive = 0
	false_negative = 0
	with open('100TRAINING.txt', 'r') as file1, open('TRAINGS.txt', 'r') as file2: # Change to 100TEST.txt and TESTGS.txt to run on test-set. 
		for line in zip(file1, file2):
			ori_sen = line[0].split()[:-1]
			path = line[0].split()[-1]
			new_sen = line[1].split()
			p = parser(path)
			mods = process(p, path) # Gets deletable modifiers
			check = evaluate(ori_sen, new_sen, mods)
			if check == 'TP':
				true_positive += 1
			elif check == 'TN':
				true_negative += 1
			elif check == 'FP':
				false_positive += 1
			elif check == 'FN':
				false_negative += 1
	print('Precision: ' + str((true_positive)/(true_positive+false_positive)))
	print('Recall: ' + str((true_positive)/(true_positive+false_negative)))
	print('Accuracy: ' + str((true_positive+true_negative)/(true_positive+true_negative+false_positive+false_negative)))
	print(true_positive, true_negative, false_positive, false_negative)
			

if __name__ == '__main__':
	main()


