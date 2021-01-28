read -p "Notes: this clears out Blazegraph DB; set PGM_DIR in drop_test_prep.sh (Enter to continue, Ctrl-C abort) "

read -p "Step 1 of 12: Load two versions of IEEE 13-Bus Feeder, with Assets and with Houses (Enter to continue) "
./drop_test_prep.sh

read -p "Step 2 of 12: Solve both Feeder versions in OpenDSS and GridLAB-D (Enter to continue) "
./drop_test_sims.sh

read -p "Step 3 of 12: Drop the Asset-based Feeder (Enter to continue) "
python3 DropCircuit.py db.cfg _5B816B93-7A5F-B64C-8460-47C17D6E4B0F

read -p "Step 4 of 12: Solve the House version again; Asset-based version should fail (Enter to continue) "
./drop_test_sims.sh

read -p "Step 5 of 12: Drop the House-based Feeder (Enter to continue) "
python3 DropCircuit.py db.cfg _49AD8E07-3BF9-A4E2-CB8F-C3722F837B62

read -p "Step 6 of 12: Both versions should fail to solve (Enter to continue) "
./drop_test_sims.sh

read -p "Step 7 of 12: Reload both Feeder models (Enter to continue) "
./drop_test_prep.sh

read -p "Step 8 of 12: Drop the House-based Feeder (Enter to continue) "
python3 DropCircuit.py db.cfg _49AD8E07-3BF9-A4E2-CB8F-C3722F837B62

read -p "Step 9 of 12: Only the Asset-based Feeder model should solve (Enter to continue) "
./drop_test_sims.sh

read -p "Step 10 of 12: Drop the Asset-based Feeder (Enter to continue) "
python3 DropCircuit.py db.cfg _5B816B93-7A5F-B64C-8460-47C17D6E4B0F

read -p "Step 11 of 12: There should be 6 tuples left in Blazegraph now (Enter to continue) "
python3 SummarizeDB.py db.cfg

read -p "Step 12 of 12: Dropping those 6 tuples (Enter to Finish) "
python3 ClearDB.py db.cfg

