import pandas as pd
import matplotlib.pyplot as plt

# Read data from csv into pandas dataframe
data = pd.read_csv('data.csv')[
    ['userid', 'From', 'To']]

# Display the first 10 rows of dataframe
print(data.head(10))

# Checking if there are NAN values
print("Presence of NAN values : \n", data.isnull().any())

# Function to remove letter from column data
def remove_letter(val):
    if (val[0] == 'F' or val[0] == 'T'):
        return val[1:]

# Use apply function to remove leter
data['From'] = data['From'].apply(remove_letter)
data['To'] = data['To'].apply(remove_letter)

# Check the data types of all columns
print(data.dtypes)

# Converting object datatype to int
data['From'] = data['From'].astype(str).astype(int)
data['To'] = data['To'].astype(str).astype(int)

# Remove duplicate user id
data.drop_duplicates('userid', inplace = True)

# Plotting Histograms
# 1) Histogram of 'To'column data
num_bins = 50
to_data = data['To']
legend = ['To']
plt.hist([to_data], bins=num_bins, color=['Orange'])
plt.xlabel("To data")
plt.ylabel("Frequency")
plt.legend(legend)
plt.show()

# 2) Histogram of 'From' column data
from_data = data['From']
legend = ['From']
plt.hist([from_data], bins=num_bins, color=['green'])
plt.xlabel("From data")
plt.ylabel("Frequency")
plt.legend(legend)
plt.show()

# 3) Histogram of 'userid' column data
userid_data = data['userid']
legend = ['userid']
plt.hist([userid_data], bins=num_bins, color=['Red'])
plt.xlabel("userid")
plt.ylabel("Frequency")
plt.legend(legend)
plt.show()

# Sorting data
print('Sorting...')

# Plotting boxplots
plt.boxplot(data['To'])
plt.boxplot(data['From'])

# Sort data according to userid
data = data.sort_values('userid')

# Adding values to region_rank to calculate rank
# Here the regions are divided by a distance of 15
# So the rank of the region with value 100 will be 0,
# 115 will be 1, 132 will be 2 and so on.
region_rank = []
for i in range(99, 210, 15):
    region_rank.append(i)

print(region_rank)

# mark_region function calculates the actual
# rank of the region of values
def mark_region(x):
    current_rank = -1 # As indices start from 0
    for i in region_rank:
        if (x > i):
            current_rank += 1
        else:
            return current_rank


# Apply the mark_region function
data['source_to'] = data['To'].apply(mark_region)
data['target_from'] = data['From'].apply(mark_region)

# Confirming the absence of NAN values
print("Presence of NAN values : \n", data.isnull().any())
data.head(100)

max_region = data['source_to'].max()
print(max_region)

# creating output dict
# This will help to keep track of all paths taken by users
output = dict()
output.update({'links_dict': dict()})

def update_source_target(src, t):
    try:
        print(src, t)
        # If this source is already in links_dict...
        if src in output['links_dict']:
            if t in output['links_dict'][src]:
                # Increment count of users with this source/target pair by 1,
                output['links_dict'][src][t]['unique_users'] += 1
            # but if the target is not already associated to this source...
            else:
                 # ...we create a new key for this target, for this source, and initiate it with 1 user and the time from source to target
                output['links_dict'][src].update({t:
                    dict(
                        {'unique_users': 1
                        })
                })
        # ...but if this source isn't already available in the links_dict, we create its key and the key of this source's target, and we initiate it with 1 user and the time from source to target
        else:
            output['links_dict'].update({src: dict({t: dict(
                {'unique_users': 1})})})

    except Exception as e:
        pass

data2 = data.apply(lambda x: update_source_target(x['source_to'], x['target_from']), axis = 1)

# Source and Target's unique combinations are printed here
for key, value in output['links_dict'].items():
    print(key, value)

# Making lists of labels, sources, targets and values
labels = []
sources = []
targets = []
values = []

for source_key, source_value in output['links_dict'].items():
    for target_key, target_value in output['links_dict'][source_key].items():
        sources.append(source_key)
        targets.append(target_key)
        values.append(target_value['unique_users'])

# Check if all users considered
sum = 0
for i in values:
    sum += i
num_rows = data.shape[0]
print(num_rows == sum)

# The 7 regions are assigned here need a multiple
# of same region as user can travel from and to any region
labels = ['Region One', 'Region Two', 'Region Three',
           'Region Four', 'Region Five', 'Region Six', 'Region Seven',
          'Region One', 'Region Two', 'Region Three', 'Region Four',
         'Region Five', 'Region Six', 'Region Seven']

# In Sankey, the source is always smaller than target parameter
# So we increment source if it is smaller than target but
# final region remains the same for it
n = len(sources)
for i in range(n):
    if sources[i] > targets[i]:
        targets[i]+=7

# Ignore sources and targets that are in same region
rem_indices = []
for i in range(n):
    if sources[i] == targets[i]:
        rem_indices.append(i)

updated_sources = []
updated_targets = []

for i in range(n):
    if i in rem_indices:
        continue
    else:
        updated_sources.append(sources[i])
        updated_targets.append(targets[i])

# Selecting colors in HEX format
palette = ['50BE97', 'E4655C', 'FCC865',
           'BFD6DE', '3E5066', '353A3E', 'E6E6E6']

#  Here, the colors are passed as HEX. This loop will convert from HEX to RGB:
for i, col in enumerate(palette):
    palette[i] = tuple(int(col[i:i+2], 16) for i in (0, 2, 4))
print(palette)

# The colors for the regions are repeated
palette = 2*palette
print(palette)
colors = []
for color in palette:
    colors.append('rgb' + str(color))

# Plotting the Sankey Chart
import plotly.graph_objects as go

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 5,
      thickness = 10,
      line = dict(color = "blue", width = 0.5),
      label = labels,
      color = colors
    ),
    link = dict(
      source = updated_sources,
      target = updated_targets,
      value = values,
      hovertemplate='%{value} unique users went from %{source.label} to %{target.label}.<br />'
  ))])

fig.update_layout(autosize=True, title_text="Customer Sankey Chart", font=dict(size=15), plot_bgcolor='white')
fig.show()