# adventofcode-2022

My solutions to the Advent Of Code puzzles from 2022. The solutions aren't "engineered" by any means - mostly just enough to get the answer in the minial amount of effort!

# Environment Setup

Solutions were written in Python 3.11, with just a couple of external libraries.

```
# Check installed python version
$ python --version
Python 3.11.1

# Create and activate venv
$ python -m venv .venv
$ source .venv/bin/activate

# Install libraries
$ pip install -r requirements.txt
```

# Cookie file

All input files have been downloaded and cached in `inputs/`, but during the competition a cookie file is needed to auto-download the input files. To enable this, create a file `inputs/cookie.txt` with the contents of your sessions cookie (should look like a long hex string).

# Executing

Each day's solution is a standalone script file. Execute by running `python day_xx.py`.

To run on different input (such as the test input if available), you need to modify the script so that `Day()` takes a filename parameter. Most scripts have this already present but commented out.
