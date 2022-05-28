# Setup

1. Make sure system has python 3 installed
2. Clone repo using `git clone`
3. Make sure to add the submodules for the data `git submodule update --init`
4. Setup a virtual enviornment (optional)
5. `pip -r requirements.txt`
6. Run away `python3 atp_wta_consistency.py`

# TODOs
- [ ] Make an input json file for the analysis, or some better way of passing in inputs
- [ ] Clean up the plot generation functions a bit (some reuse code)
- [ ] Is there a better way than QF,SF,F to determine how far "top 10 players are making it"
- [ ] Count top 10s in the tournaments and try to filter there
# Thanks

Big thanks to https://www.tennisabstract.com/ for there free databases found here:

* https://github.com/JeffSackmann/tennis_atp
* https://github.com/JeffSackmann/tennis_wta