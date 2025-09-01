""" 
utility functions for mariners statcast analysis:
- fetch batted balls for a team/date range
- sample last-n events
- fit logistic regression (p(hit) ~ ev + la)
- create ev x la prediction grid
- plot heatmap and scatter
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pybaseball import statcast