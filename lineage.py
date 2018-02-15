#!usr/bin/env python3

import sys
import re

'''
  Title: lineage.py
  Date: 2018-02-15
  Author: Nazeefa Fatima

Description:
  The script parses taxononmy data based on arbitrary number which in this case is taxonomy ID and retains lineage path.

List of function(s):
  searchData

List of "non-standard" modules:
	None.
  
Procedure:
	  . Download taxonomy data (file name: taxonomy.data) via FTP: https://www.ebi.ac.uk/ena/browse/taxonomy-download
	  . Run the script (see usage).
How it works (summary):
	  . Stores IDs, parent IDs, rank names, and scientific names to dictionaries
	  . Stores each dictionary to a list
	  . Searches database using parent ID as an ID for a next entry.
	  . Checks that a parent ID for a rank name and a scientific name are same to ensure correct names are printed

Usage:
	./lineage.py taxonomy.dat
''' 

bashInput = sys.argv
# To make sure bash input has the correct amount of variables
if len(bashInput) is not 2:
  print("Wrong bash input")
  sys.exit()
taxonomy_file = open(bashInput[1], 'r')

class tax_data:
# Properties of class: setting up initial values of data (for taxonomy entries) to empty
  ID = 0
  ParentID = 0
  Rank = ""
  ScientificName = ""

# Creating an array of dictionaries:
# List of dictionaries that will contain ID as keys and its parent ID as values
list_ids_pids = []
# List of dictionaries that will contain parent ID as keys and rank name (e.g. family) as values
list_pids_rank=[]
# List of dictionaries that will contain parent ID as keys and scientific names (defined here as "scinames") as values.
list_pids_scinames=[]
# The following list will contain all the individual entries stored in a taxonomy database (see properties of class)
AllTaxonomies = []

# A prompt asking user to enter taxonomy ID
user_tax_id = input("Enter taxonomy ID: ")
print("Searching for taxonomy ID "+ user_tax_id +" in the database...\n")

'''
searchData is a function with argument/paremeter i.e. taxonomy ID entered by a user (userTID) that will be called by the function
tax_data: Treating class as an object (named "entry_found"), empty parentheses means initialise values

In lines below the for loop:
	1. ".split(":",1)[1].strip" means line in data file will be split at position where colon is located 
	picking up an element located at index 1 and, finally, line breaks will be removed.
	2. Rank names are added to entry_found.Rank excluding the entries with no rank given in a database
	3. Scientific names are added to entry_found.ScientificName only for the entries with ranks
	4. list_ids_pids contains ID as keys and its parent ID as values
	5. list_pids_ranks contains parent IDs (keys) and rank names (values), corresponding to IDs stored before
	6. list_pids_scinames contains parent IDs (keys) and scientific names (values), corresponding to IDs stored before
	7. Function is called with parentID of previous entry that, when goes in function, is considered as an ID of next entry.
'''
def searchData(userTID):
	entry_found = tax_data()
	taxonomy_file = open(bashInput[1], 'r')
	for line in taxonomy_file:
		if ("ID" in line) and not ("PARENT" in line) and not ("GC" in line) and not ("MGC" in line):
			tax_id = line.split(":",1)[1].strip()
			if userTID == tax_id:
				entry_found.ID = tax_id
		if(entry_found.ID != 0):
				if "PARENT ID" in line:
					parent_id = line.split(":",1)[1].strip()
					entry_found.ParentID = parent_id
				if "RANK" in line:
					id_rank = line.split(":",1)[1].strip()
					if not id_rank == "no rank":
						entry_found.Rank = id_rank
				if "SCIENTIFIC NAME" in line:
					if not entry_found.Rank == "":
						id_sci_name = line.split(":",1)[1].strip()
						entry_found.ScientificName = id_sci_name 
		if "//" in line:
				if(entry_found.ID != 0):
					AllTaxonomies.append(entry_found)
					list_ids_pids.append({entry_found.ID:entry_found.ParentID})
					if not entry_found.Rank == "":
					  list_pids_rank.append({entry_found.ParentID:entry_found.Rank})
					if not entry_found.ScientificName == "":
					  list_pids_scinames.append({entry_found.ParentID:entry_found.ScientificName})
					searchData(entry_found.ParentID)
					return

# Calling function by passing the taxonomy ID entered by the user
searchData(user_tax_id)

# print("\n list of parentID for a rank:rank name")

# for dict_rank_names in list_pids_rank:
#   print(dict_rank_names) # <-- prints dictionary stored in a list of ranks

# print("\n list of parentID for a scientific_name:scientific_name")

# for dict_scientific_names in list_pids_scinames:
#   print(dict_scientific_names) # <-- prints dictionary stored in a list of scientific names

'''
In first four lines: 
index of list is being passed, through the for loop, which could be several or one dictionary; dict_rank_names == i is working as a storage (memory)
rank_keys_set & sci_names_keys_set is created for obtaining all keys i.e. parent IDs for ranks and scientific names, respectively from the dictionary. 
Since, in this case, there is only one key, it is safe to use set otherwise tuple or list are recommended to access index

In subsequent lines of code (see "if" condition), following approach is used:
1. If parent IDs are same for both rank and scientific name then it means this data can be safely retained from database/file
2. Change a set of keys to list e.g. list(rank_keys_set)
	  - Since each dictionary has only one key:value, therefore list of set has one key i.e. parent ID for a rank from {parentID:rank}
	  and parent ID for a scientific name from {parentID:ScientificName}
	  - That one key at position 0 of the list is obtained for both rank_keys_set and sci_names_keys_set
5. Values for those keys i.e. {rank name: scientific name} are obtained, and stored to a dictionary that will be used as data for a list of lineage
'''
# Basically, what is being appended to lineage list is: {dict_rank_names["32"]:dict_scientific_names["32"]} where 32 (parent ID) is a key
# This returns values e.g. "species":"Myxcocous fulvus for a key i.e. parent ID: 32 found in both dictionaries)"
lineage = []
for dict_rank_names in list_pids_rank:
	rank_keys_set = set(dict_rank_names.keys())
	for dict_scientific_names in list_pids_scinames:
		sci_names_keys_set = set(dict_scientific_names.keys())
		if rank_keys_set == sci_names_keys_set:
			pid_for_rank = list(rank_keys_set)[0]
			pid_for_sci_names = list(sci_names_keys_set)[0]
			dict_for_lineage_list = {dict_rank_names[pid_for_rank]:dict_scientific_names[pid_for_sci_names]}
			lineage.append(dict_for_lineage_list)
print("\nLineage:",re.sub(r'[\{\[\]\'\}]', '', str(lineage)).replace(",",";"))
