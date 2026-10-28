#!/bin/bash
DB="/Users/michaelryan/Developer/michaelr-xyz/GeigerLog/data/michaelr_xyz.logdb"
# Delete any row where CPM1st is the overflow spike (32768) or the -1 placeholder
sqlite3 "$DB" "DELETE FROM data WHERE CPM1st > 20000 OR CPM1st = -1;"
