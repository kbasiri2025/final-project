
# anfis_example.py
# Author: Khujasta Basiri
# CYSE 630 Final Exam Bonus - Simple ANFIS Example
# This script demonstrates how ANFIS can be used to learn fuzzy rules from data.

import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

# Example dataset: Input x, Output y
x = np.linspace(0, 10, 50)
y = np.sin(x) + np.random.normal(0, 0.1, 50)  # noisy sine wave

# Define fuzzy sets
x_range = np.linspace(0, 10, 100)
low = fuzz.trimf(x_range, [0, 0, 5])
medium = fuzz.trimf(x_range, [0, 5, 10])
high = fuzz.trimf(x_range, [5, 10, 10])

# Show membership functions
plt.figure()
plt.plot(x_range, low, label='Low')
plt.plot(x_range, medium, label='Medium')
plt.plot(x_range, high, label='High')
plt.title('Initial Fuzzy Membership Functions')
plt.legend()
plt.savefig('anfis_membership.png')

# For bonus points, explain in the report:
# - ANFIS can be trained to adjust these membership functions based on data
# - In this example, we only show initial fuzzy sets and how ANFIS would adapt them
# - Full ANFIS training requires a specialized library or custom code
