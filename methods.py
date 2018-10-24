import numpy as np
import pandas as pd
import dash_html_components as html

def MonthlyTotalUsers(month,completed_per_month):
    '''
    Returns the total number of users that completed and order in the current month.
    '''
    total=completed_per_month.get_group(month)['user_id'].unique()

    return total.shape[0],total

def MonthlyNewUsers(month,sorted_completed_months_keys,completed_per_month):
    '''
    Returns the total number of users that completed an order in the current month
    and never completed any order before.
    '''
    current_users= completed_per_month.get_group(month)['user_id'].unique()
    current_month_index = sorted_completed_months_keys.index(month)

    if current_month_index is not 0:
        past_users=[ completed_per_month.get_group(sorted_completed_months_keys[index])['user_id'].unique() \
                    for index in range(0,current_month_index)]

        past_users=np.concatenate(past_users)

        new_users = np.setdiff1d(current_users,past_users)
        return new_users.shape[0],new_users

    else:
        return current_users.shape[0],current_users
    
def MonthlyRepeatingUsers(month,sorted_completed_months_keys,completed_per_month):
    '''
    Returns the number of user that completed at least one order this month
    and also completed at least one order in the months before. 
    '''
    current_month_users= completed_per_month.get_group(month)['user_id'].unique()
    current_month_index = sorted_completed_months_keys.index(month)

    if current_month_index == 0:
        return 0.0,[]

    else:
        past_users=[ completed_per_month.get_group(sorted_completed_months_keys[index])['user_id'].unique() \
                    for index in range(0,current_month_index)]

        past_users=np.concatenate(past_users)
        repeated_users = np.intersect1d(current_month_users,past_users)

        return repeated_users.shape[0],repeated_users

def MonthlyRepeatingUsersStartEnd(start_month,end_month,sorted_completed_months_keys,completed_per_month):
    '''
    repeating users from end_month
    new users from start_month
    '''
    start_month_index=sorted_completed_months_keys.index(start_month)
    end_month_index=sorted_completed_months_keys.index(end_month)

    end_month_repeat=MonthlyRepeatingUsers(end_month,sorted_completed_months_keys,completed_per_month)[1]
    start_month_new_users=MonthlyNewUsers(start_month,sorted_completed_months_keys,completed_per_month)[1]
    #start_month_users=completed_per_month.get_group(sorted_completed_months_keys[start_month_index])['user_id'].unique()
    
    repeated_users = np.intersect1d(start_month_new_users,end_month_repeat)

    return repeated_users.shape[0],repeated_users



def WeeklyNewUsers(month,sorted_completed_months_keys,completed_per_month):
    '''
    Returns the users that completed an order during month and never completed an order before,
    splitted week by week.
    '''
    month_new_users=MonthlyNewUsers(month,sorted_completed_months_keys,completed_per_month)[1]
    month_group=completed_per_month.get_group(month)
    completed_per_week=month_group.groupby([month_group.completed_at.dt.week])

    week_keys= list(completed_per_week.groups.keys())
    week_keys.sort()

    new_user_per_week=[]

    for week in week_keys:
        week_group=completed_per_week.get_group(week)
        week_users=week_group['user_id'].unique()
        week_new_users=np.intersect1d(week_users,month_new_users)
        new_user_per_week.append(week_new_users)

    return week_keys, new_user_per_week


def WeeklyRepeatingUsers(month,sorted_completed_months_keys,completed_per_month):
    '''
    Returns the number of user that completed at least one order this month
    and also completed at least one order in the month before, split week by week. 
    '''
    month_repeated_users=MonthlyRepeatingUsers(month,sorted_completed_months_keys,completed_per_month)[1]
    month_group=completed_per_month.get_group(month)

    completed_per_week=month_group.groupby([month_group.completed_at.dt.week])
    week_keys= list(completed_per_week.groups.keys())
    week_keys.sort()

    repeated_user_per_week=[]
    for week in week_keys:
        week_group=completed_per_week.get_group(week)
        week_users=week_group['user_id'].unique()
        week_repeated_users=np.intersect1d(week_users,month_repeated_users)
        repeated_user_per_week.append(week_repeated_users)

    return week_keys, repeated_user_per_week

def CustomerLifetime(month,sorted_completed_months_keys,completed_per_month):

    current_month_index = sorted_completed_months_keys.index(month)
    current_month_users = MonthlyTotalUsers(sorted_completed_months_keys[current_month_index],completed_per_month)[1]


    user_lifetime=0
    for user in current_month_users:
        user_lifetime+=1
        for month_index in range(0,current_month_index):
            month_users = MonthlyTotalUsers(sorted_completed_months_keys[month_index],completed_per_month)[1]
            if user in month_users:
                user_lifetime+=1

    return user_lifetime / current_month_users.shape[0]


def CustomerLifetimeValue(month,sorted_completed_months_keys,completed_per_month):

    cl=CustomerLifetime(month,sorted_completed_months_keys,completed_per_month)

    current_month_index = sorted_completed_months_keys.index(month)

    total_num_orders=0
    total_order_value=0.0

    for month_index in range(0,current_month_index+1):
        month_group = completed_per_month.get_group(sorted_completed_months_keys[month_index])
        total_num_orders+=month_group.shape[0]
        total_order_value+=month_group.total.sum()

    avg_order_value = total_order_value / total_num_orders

    return cl * avg_order_value

def BasketValue(month,sorted_completed_months_keys,completed_per_month):
    current_month_index = sorted_completed_months_keys.index(month)

    total_num_orders=0
    total_order_value=0.0

    for month_index in range(0,current_month_index+1):
        month_group = completed_per_month.get_group(sorted_completed_months_keys[month_index])
        total_num_orders+=month_group.shape[0]
        total_order_value+=month_group.item_total.sum()

    avg_order_value = total_order_value / total_num_orders

    return avg_order_value

##############################
##############################
# Conditional Tables are under development in Dash.
# Here is an handmade version.
##############################
##############################

COLORS = [
    {
        'background': '#ffffff',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#e6faff',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#ccf5ff',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#b3f0ff',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#99ebff',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#80e5ff',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#66e0ff',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#4ddbff',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#33d6ff',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#1ad1ff',
        'text': 'rgb(30, 30, 30)'
    },
]

def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def cell_style(value, min_value, max_value):
    style = {}
    #print('')
    #print('value = ',value)
    if is_numeric(value) and ~np.isnan(value):
        if ~isinstance(value, float):
            if max_value > min_value:
                relative_value = (value - min_value) / (max_value - min_value)
                if value != 0.0 and value == min_value:
                    relative_value=0.1
            elif max_value == 0.0  and min_value==0.0:
                relative_value =0.0
            else:
                relative_value=1.0
        else:
            relative_value=value

        #print('relative_value = ',relative_value)
        #print('value = {}'.format(value))
        #print('relative_value = {}'.format(relative_value))
        color_index = int(round(relative_value * 10))
        #print('color_index = ',color_index)

        if color_index == len(COLORS):
            color_index -=1
        #print('color_index = {}'.format(color_index))
        style = {
            'backgroundColor': COLORS[color_index]['background'],
            'color': COLORS[color_index]['text'],
        }
    else:
        style = {
            'backgroundColor': COLORS[0]['background'],
            'color': COLORS[0]['text'],
        }
    return style


def ConditionalTable(dataframe):

    rows = []
    for i in range(0,len(dataframe)):
        if i != (len(dataframe)-1):
            max_value = np.nanmax(dataframe.iloc[i][2:].values)
            min_value = np.nanmin(dataframe.iloc[i][2:].values)
            #print('min value ',min_value)
            #print('max value ',max_value)
            row = {}
            for col_index,col in enumerate(dataframe.columns):
                value = dataframe.iloc[i][col]
                if col_index > 1:
                    style = cell_style(value, min_value, max_value)
                else:
                    style = cell_style(value, 0.0, 0.0)

                if isinstance(value,float) and ~np.isnan(value):
                    value='{:.3f}'.format(value)

                row[col] = html.Div(
                    value,
                    style=dict({
                        'height': '100%',
                        'border-style': 'solid hidden solid hidden',
                        'border-width': '0.4px',
                        'text-align': 'center',
                        'vertical-align': 'middle',
                    }, **style)
                )
            rows.append(row)
        else:
            row = {}
            for col_index,col in enumerate(dataframe.columns):
                value = dataframe.iloc[i][col]
                style = cell_style(value, 0.0, 0.0)
                row[col] = html.Div(
                        value,
                        style=dict({
                            'height': '100%',
                            'border-style': 'solid hidden solid hidden',
                            'border-width': '0.4px',
                            'text-align': 'center',
                            'vertical-align': 'middle',
                        }, **style)
                    )
            rows.append(row)

        #print('')
    return rows