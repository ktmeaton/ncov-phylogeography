import sqlite3
import os

def identify_nucleotide_samples():
    """ Parse the sqlite database to identify the nucleotide accessions."""
    sample_list = []
    sqlite_db_path = os.path.join(results_dir,"sqlite_db",config["sqlite_db"])
    max_datasets = config["max_datasets_nucleotide"]

    conn = sqlite3.connect(sqlite_db_path)
    cur = conn.cursor()
    accessions = cur.execute(config["sqlite_select_command_nuc"]).fetchall()
    cur.close()

    for acc in accessions:
        sample_list.append(acc[0])
    sample_list = sample_list[0:max_datasets]

    return sample_list
