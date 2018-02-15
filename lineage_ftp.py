#!usr/bin/env python3
import sys
import urllib.request
import re

class tax_data:
  ID = 0
  ParentID = 0
  Rank = ""
  ScientificName = ""

list_ids_pids = []
list_pids_rank=[]
list_pids_scinames=[]
AllTaxonomies = []

user_tax_id = input("Enter taxonomy ID: ")
print("Searching for taxonomy ID "+ user_tax_id +" in the database...\n")

def searchData(userTID):
    entry_found = tax_data()
    web_data = urllib.request.urlopen('ftp://ftp.ebi.ac.uk/pub/databases/taxonomy/taxonomy.dat')
    for line in web_data:
        line = line.decode('utf-8').strip() # following line encodes bytes to string and removes new lines
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

searchData(user_tax_id)
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
