import pandas as pd
import numpy as np
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator

def get_token():
    response = requests.post(
                        url = 'https://www.strava.com/oauth/token',
                        data = {
                                'client_id': '[YOUR_CLIENT_ID]',
                                'client_secret': '[YOUR_CLIENT_SECRET]',
                                'refresh_token': '[YOUR_REFRESH_TOKEN]',
                                'code': '[YOUR_AUTHORIZATION_CODE]',
                                'grant_type': 'refresh_token'
                                }
                    )
    access_token = response.json()['access_token']
    print(access_token)
    return access_token

def get_activities(access_token, from_date, to_date):
    url = f'https://www.strava.com/api/v3/athlete/activities?after={from_date}&before={to_date}&page=1&per_page=200'
    payload={}
    headers = {
        'Authorization': 'Bearer ' + access_token
        }
    response = requests.request("GET", url, headers=headers, data=payload)
    activities = response.json()
    return activities

def get_kudos(access_token, activity_id):
    url = f'https://www.strava.com/api/v3/activities/{activity_id}/kudos?page=1&per_page=200'
    payload={}
    headers = {
        'Authorization': 'Bearer ' + access_token
        }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    return data

def transform(access_token, activities):
    for act in activities:
        if act["private"] == False:
            activity_id = act['id']
            nb_kudos = act['kudos_count']
            kudos_list = [item['firstname'] + ' ' + item['lastname']  for item in get_kudos(access_token, activity_id)]
            distance = act['distance']
            moving_time = act['moving_time']
            sport_type = act['sport_type']

            stats = {
                'activity_id' : activity_id,
                'nb_kudos' : nb_kudos,
                'kudos_list': kudos_list,
                'distance': distance,
                'moving_time': moving_time,
                'sport_type': sport_type
            }
            statlist.append(stats)
    return

def to_1D(series):
    return pd.Series([x for list in series for x in list]) #series of lists to list of elements

def bar_plot(data):
    # Setup plot size
    fig, ax = plt.subplots(figsize=(13.33,7.5), dpi = 96)

    # Plot data
    sns.barplot(x=data.index, y=data.values, palette='magma', zorder=2)

    # Create grid 
    ax.grid(which="major", axis='x', color='#DAD8D7', alpha=0.5, zorder=1)
    ax.grid(which="major", axis='y', color='#DAD8D7', alpha=0.5, zorder=1)

    # Remove splines
    ax.spines[['top','right','bottom']].set_visible(False)

    # Make left spine slightly thicker
    ax.spines['left'].set_linewidth(1.1)

    # Add label on top of each bar
    rects = ax.patches
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height + 1, int(height), ha='center', va='bottom', size=10)  

    # Add in red line and rectangle on top
    ax.plot([0.12, .9],                  # Set width of line
        [.98, .98],                  # Set height of line
        transform=fig.transFigure,   # Set location relative to plot
        clip_on=False, 
        color='#E3120B', 
        linewidth=.6)
    ax.add_patch(plt.Rectangle((0.12,.98),                 # Set location of rectangle by lower left corder
                        0.04,                       # Width of rectangle
                        -0.02,                      # Height of rectangle. Negative so it goes down.
                        facecolor='#E3120B', 
                        transform=fig.transFigure, 
                        clip_on=False, 
                        linewidth = 0))

    # Reformat x-axis tick labels
    ax.xaxis.set_tick_params(labelsize=12)        # Set tick label size
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

    # Reformat yaxis
    ax.yaxis.set_major_formatter(lambda s, i : f'{s:,.0f} kudos')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_tick_params(pad=-2,             # Pad tick labels so they don't go over y-axis
                        labeltop=True,      # Put x-axis labels on top
                        labelbottom=False,  # Set no x-axis labels on bottom
                        bottom=False,       # Set no ticks on bottom
                        labelsize=12)       # Set tick label size                  

    # Add in title and subtitle
    ax.text(x=0.12, y=.93, s="Strava Kudoers", transform=fig.transFigure, ha='left', fontsize=14, weight='bold', alpha=.8)
    ax.text(x=0.12, y=.90, s="Number of kudos given from 01/01/2022 to 24/10/2022", transform=fig.transFigure, ha='left', fontsize=12, alpha=.8)
    
    
    plt.subplots_adjust(left=None, bottom=0.2, right=None, top=0.85, wspace=None, hspace=None)
    
    # Export plot as high resolution PNG
    plt.savefig('strava_kudos.png', bbox_inches="tight", facecolor='white', pad_inches=0.5)
    
    plt.show()

    return

def scatter_plot(df):
    # Setup plot size
    fig, ax = plt.subplots(figsize=(13.33,7.5), dpi = 96)

    # Plot data
    df = df[df['sport_type'] == 'Run']
    sns.scatterplot(x=df['distance'], y=df['nb_kudos'], color='purple', s = 70)
    
    # Fit a straight line to highlight the trend
    a, b = np.polyfit(df['distance'], df['nb_kudos'], 1)
    x = np.linspace(min(df['distance']), max(df['distance']), num=100)
    plt.plot(x, a*x+b, color='black', linestyle='--', linewidth=2) #'--k'=black dashed line

    # Create grid 
    ax.grid(which="major", axis='x', color='#DAD8D7', alpha=0.5, zorder=1)
    ax.grid(which="major", axis='y', color='#DAD8D7', alpha=0.5, zorder=1)

    # Remove splines
    ax.spines[['top','right','bottom']].set_visible(False)

    # Make left spine slightly thicker
    ax.spines['left'].set_linewidth(1.1)

    # Add in red line and rectangle on top
    ax.plot([0.12, .9],                  # Set width of line
        [.98, .98],                  # Set height of line
        transform=fig.transFigure,   # Set location relative to plot
        clip_on=False, 
        color='#E3120B', 
        linewidth=.6)
    ax.add_patch(plt.Rectangle((0.12,.98),                 # Set location of rectangle by lower left corder
                        0.04,                       # Width of rectangle
                        -0.02,                      # Height of rectangle. Negative so it goes down.
                        facecolor='#E3120B', 
                        transform=fig.transFigure, 
                        clip_on=False, 
                        linewidth = 0))

    
    # Reformat xaxis
    ax.set_xlabel('Distance (km)', size = 12)
    ax.xaxis.set_major_formatter(lambda s, i : f'{s/1e3:,.0f}')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.set_tick_params(pad=-2,             # Pad tick labels so they don't go over y-axis
                        labeltop=False,      # Put x-axis labels on top
                        labelbottom=True,  # Set no x-axis labels on bottom
                        bottom=False,       # Set no ticks on bottom
                        labelsize=12)       # Set tick label size      

    # Reformat yaxis
    ax.set_ylabel('')
    ax.yaxis.set_major_formatter(lambda s, i : f'{s:,.0f} kudos')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_tick_params(pad=-2,             # Pad tick labels so they don't go over y-axis
                        labeltop=True,      # Put x-axis labels on top
                        labelbottom=False,  # Set no x-axis labels on bottom
                        bottom=False,       # Set no ticks on bottom
                        labelsize=12)       # Set tick label size                  

    # Add in title and subtitle
    ax.text(x=0.12, y=.93, s="Strava Kudos in Runs", transform=fig.transFigure, ha='left', fontsize=14, weight='bold', alpha=.8)
    ax.text(x=0.12, y=.90, s="Number of kudos given from 01/01/2022 to 24/10/2022 in running activities only", transform=fig.transFigure, ha='left', fontsize=12, alpha=.8)
    
    # Adjust the spaces and margins of the plots
    plt.subplots_adjust(left=None, bottom=0.2, right=None, top=0.85, wspace=None, hspace=None)
    
    # Export plot as high resolution PNG
    plt.savefig('strava_kudos_runs.png', bbox_inches="tight", facecolor='white', pad_inches=0.5)
    
    plt.show()

    return


# Get access token
access_token = get_token()

# Define the from date and to date
from_date = datetime(2022, 1, 1) #datetime(year, month, day)
from_date = int(from_date.timestamp()) #epoch of from_date
to_date = datetime(2022, 10, 24) #datetime(year, month, day)
to_date = int(to_date.timestamp()) #epoch of to_date

# Get activities in scope
activities = get_activities(access_token, from_date, to_date)

# Put the relevant data in a Dataframe
statlist = []
transform(access_token, activities)
df = pd.DataFrame(statlist)
print(df.head())

# Get the number of activities in the period
nb_activities = df['nb_kudos'].count()
print(f'number of activities : {nb_activities}')

# Get the number of kudos in the period
nb_kudos = df['nb_kudos'].sum()
print(f'number of kudos : {nb_kudos}')

# Calculate the average number of kudos per activity
avg_kudos_per_activity = round(df['nb_kudos'].mean(),2)
print(f'average kudos per activity : {avg_kudos_per_activity}')

# Average kudos per activity type
print(f'run kudos : {round(df[df["sport_type"] == "Run"]["nb_kudos"].mean(),2)}')
print(f'ride kudos : {round(df[df["sport_type"] == "Ride"]["nb_kudos"].mean(),2)}')
print(f'hike kudos : {round(df[df["sport_type"] == "Hike"]["nb_kudos"].mean(),2)}')

# From the Dataframe get the list of top kudoers
kudos = to_1D(df['kudos_list']).value_counts()

# Plot the kudos and run distances on a scatter plot
scatter_plot(df)

# Plot the kudoers on a bar chart
bar_plot(kudos)