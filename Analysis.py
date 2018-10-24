import pandas as pd
import numpy as np
import operator
from functools import reduce
import collections
import sys
import math

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import methods

order = pd.read_csv('query_result_2018-05-28T11_01_55.232Z.csv')

order = order[order.state=='complete']

all_users = order.user_id.unique()

# sort df by customer creation time
date_columns=[ value for value in order.columns.values if '_at' in value]
for column in date_columns:
    order[column] = pd.to_datetime(order[column])

# group data by month-year
completed_per_month=order.groupby([order.completed_at.dt.month,order.completed_at.dt.year])

sorted_completed_months_keys = list(completed_per_month.groups.keys())
sorted_completed_months_keys.sort(key=operator.itemgetter(1,0))

# delete anything before 2018, if any
sorted_completed_months_keys = [month_tuple for month_tuple in sorted_completed_months_keys if month_tuple[1]>=2018]


###############################
################################
x_values_months=[month_indx for month_indx,_ in enumerate(sorted_completed_months_keys)]

total_users=[]
for month in sorted_completed_months_keys:
    total_users.append(methods.MonthlyTotalUsers(month,completed_per_month)[0])

##################################
##################################
new_users=[]
for month in sorted_completed_months_keys:
    new_users.append(methods.MonthlyNewUsers(month,sorted_completed_months_keys,completed_per_month)[0])

##################################
##################################
repeating_users=[]
for month in sorted_completed_months_keys:
    repeating_users.append(methods.MonthlyRepeatingUsers(month,sorted_completed_months_keys,completed_per_month)[0])
##################################
##################################
customers_lifetime=[]
for month in sorted_completed_months_keys:
    customers_lifetime.append(methods.CustomerLifetime(month,sorted_completed_months_keys,completed_per_month))

##################################
##################################
customers_lifetime_value=[]
for month in sorted_completed_months_keys:
    customers_lifetime_value.append(methods.CustomerLifetimeValue(month,sorted_completed_months_keys,completed_per_month))

##################################
##################################

basket_value=[]
for month in sorted_completed_months_keys:
    basket_value.append(methods.BasketValue(month,sorted_completed_months_keys,completed_per_month))

##################################
##################################

# tables definition in the following
# each table is defined by a dataframe

column_list = ['Month','NC']
for index,_ in enumerate(sorted_completed_months_keys[1:]):
    column_list.append('Month {}'.format(index+1))

# cohort with absolute values
abs_cohort_df = pd.DataFrame(columns=column_list)

for index,start_month in enumerate(sorted_completed_months_keys):

    month_cohort=['{}-{}'.format(start_month[0],start_month[1])]

    total_nc=methods.MonthlyNewUsers(start_month,sorted_completed_months_keys,completed_per_month)[0]
    month_cohort.append(total_nc)

    for end_month in sorted_completed_months_keys[index+1:]:
        repeat=methods.MonthlyRepeatingUsersStartEnd(start_month,end_month,sorted_completed_months_keys,completed_per_month)
        month_cohort.append(repeat[0])

    for _ in range(len(column_list)-len(month_cohort)):
        month_cohort.append(math.nan)
    
    month_df = pd.DataFrame([month_cohort],columns=column_list)
    abs_cohort_df = abs_cohort_df.append(month_df,ignore_index=True)

# cohort with percentage values
per_cohort_df = pd.DataFrame(columns=column_list)

for index,start_month in enumerate(sorted_completed_months_keys):
    month_cohort=['{}-{}'.format(start_month[0],start_month[1])]

    total_nc=methods.MonthlyNewUsers(start_month,sorted_completed_months_keys,completed_per_month)[0]
    month_cohort.append(total_nc)

    for end_month in sorted_completed_months_keys[index+1:]:
        repeat=methods.MonthlyRepeatingUsersStartEnd(start_month,end_month,sorted_completed_months_keys,completed_per_month)[0]
        month_cohort.append(repeat/total_nc)

    for _ in range(len(column_list)-len(month_cohort)):
        month_cohort.append(math.nan)
    
    month_df = pd.DataFrame([month_cohort],columns=column_list)
    per_cohort_df = per_cohort_df.append(month_df,ignore_index=True)


# dashboard definition
app = dash.Dash()

app.layout = html.Div([

    html.H1(children='Month-Based Analysis',style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            dcc.Graph(
                    id='total-users-per-month',
                    figure={
                        'data': [go.Scatter(
                                    x=x_values_months,
                                    y=total_users,
                                    #text=None,
                                    mode='lines+markers',
                                    opacity=0.7,
                                    marker={
                                        'size': 15,
                                        'line': {'width': 0.5, 'color': 'white'}
                                    },
                                    name='plot'
                                    )],
                        'layout': go.Layout(
                            title='Total customers (TC)',
                            xaxis={'title': 'Time (mm/yyyy)',
                                    'ticktext':['{:02d}/{}'.format(month[0],month[1]) for month in sorted_completed_months_keys],
                                    'tickvals':x_values_months,
                                    },
                            yaxis={'title': 'TC'},
                            margin=go.Margin(
                                    l=50,
                                    r=10,
                                    b=100,
                                    t=100,
                                    pad=4
                                )
                            #legend={'x': 0, 'y': 1},
                            #hovermode='closest'
                        )}
            )
        ],className='four columns'),
        html.Div([
            dcc.Graph(
                    id='new-users-per-month',
                    figure={
                        'data': [go.Scatter(
                                    x=x_values_months,
                                    y=new_users,
                                    #text=None,
                                    mode='lines+markers',
                                    opacity=0.7,
                                    marker={
                                        'size': 15,
                                        'line': {'width': 0.5, 'color': 'white'}
                                    },
                                    name='plot'
                                    )],
                        'layout': go.Layout(
                            title='New customers (NC)',
                            xaxis={'title': 'Time (mm/yyyy)',
                                    'ticktext':['{:02d}/{}'.format(month[0],month[1]) for month in sorted_completed_months_keys],
                                    'tickvals':x_values_months,
                                    },
                            yaxis={'title': 'NC'},
                            margin=go.Margin(
                                    l=50,
                                    r=10,
                                    b=100,
                                    t=100,
                                    pad=4
                                )
                            #legend={'x': 0, 'y': 1},
                            #hovermode='closest'
                        )
                    })
        ],className='four columns'),
        html.Div([
            dcc.Graph(
                id='repeating-users-per-month',
                figure={
                    'data': [go.Scatter(
                                x=x_values_months,
                                y=repeating_users,
                                #text=None,
                                mode='lines+markers',
                                opacity=0.7,
                                marker={
                                    'size': 15,
                                    'line': {'width': 0.5, 'color': 'white'}
                                },
                                name='plot'
                                )],
                    'layout': go.Layout(
                        title='Repeating customers (RC)',
                        xaxis={'title': 'Time (mm/yyyy)',
                                'ticktext':['{:02d}/{}'.format(month[0],month[1]) for month in sorted_completed_months_keys],
                                'tickvals':x_values_months,
                                },
                        yaxis={'title': 'RC'},
                        margin=go.Margin(
                                    l=50,
                                    r=10,
                                    b=100,
                                    t=100,
                                    pad=4
                                )
                        #margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        #legend={'x': 0, 'y': 1},
                        #hovermode='closest'
                    )
            })
        ],className='four columns')
    ],className="row"),

    html.Div([
        html.Div([
            html.H6(children='Repeating Custumers Month by Month (absolute)',style={'textAlign': 'center'}),
            dt.DataTable(
                rows=methods.ConditionalTable(abs_cohort_df),
                columns=abs_cohort_df.columns,
                row_height=40.0,
                column_width=120.0,
                header_row_height=40.0,
                min_height=245,
                id='table'
            )
        ],className='six columns'),
        html.Div([
            html.H6(children='Repeating Custumers Month by Month (percentage)',style={'textAlign': 'center'}),
            dt.DataTable(
                rows=methods.ConditionalTable(per_cohort_df),
                columns=per_cohort_df.columns,
                row_height=40.0,
                column_width=120.0,
                header_row_height=40.0,
                min_height=245.0,
                id='table'
            )
        ],className='six columns')
    ],className="row"),

    html.Div([
        html.Div([
            dcc.Graph(
                id='customer-lifetime-per-month',
                figure={
                    'data': [go.Scatter(
                                x=x_values_months,
                                y=customers_lifetime,
                                #text=None,
                                mode='lines+markers',
                                opacity=0.7,
                                marker={
                                    'size': 15,
                                    'line': {'width': 0.5, 'color': 'white'}
                                },
                                name='plot'
                                )],
                    'layout': go.Layout(
                        title='Customers Lifetime (CL)',
                        xaxis={'title': 'Time (mm/yyyy)',
                                'ticktext':['{:02d}/{}'.format(month[0],month[1]) for month in sorted_completed_months_keys],
                                'tickvals':x_values_months,
                                },
                        yaxis={'title': 'CL'},
                        margin=go.Margin(
                                    l=50,
                                    r=10,
                                    b=100,
                                    t=100,
                                    pad=4
                                )
                        #margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        #legend={'x': 0, 'y': 1},
                        #hovermode='closest'
                    )
            })
        ],className='four columns'),
        html.Div([
            dcc.Graph(
                id='basket-value',
                figure={
                    'data': [go.Scatter(
                                x=x_values_months,
                                y=basket_value,
                                #text=None,
                                mode='lines+markers',
                                opacity=0.7,
                                marker={
                                    'size': 15,
                                    'line': {'width': 0.5, 'color': 'white'}
                                },
                                name='plot'
                                )],
                    'layout': go.Layout(
                        title='Avg Basket Value (BV)',
                        xaxis={'title': 'Time (mm/yyyy)',
                                'ticktext':['{:02d}/{}'.format(month[0],month[1]) for month in sorted_completed_months_keys],
                                'tickvals':x_values_months,
                                },
                        yaxis={'title': 'BV','range':[0.0,50.0]},
                        margin=go.Margin(
                                    l=50,
                                    r=10,
                                    b=100,
                                    t=100,
                                    pad=4
                                )
                        #margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        #legend={'x': 0, 'y': 1},
                        #hovermode='closest'
                    )
            })
        ],className='four columns'),


        html.Div([
            dcc.Graph(
                id='customer-lifetime-value-per-month',
                figure={
                    'data': [go.Scatter(
                                x=x_values_months,
                                y=customers_lifetime_value,
                                #text=None,
                                mode='lines+markers',
                                opacity=0.7,
                                marker={
                                    'size': 15,
                                    'line': {'width': 0.5, 'color': 'white'}
                                },
                                name='plot'
                                )],
                    'layout': go.Layout(
                        title='Customers Lifetime Value (CLV)',
                        xaxis={'title': 'Time (mm/yyyy)',
                                'ticktext':['{:02d}/{}'.format(month[0],month[1]) for month in sorted_completed_months_keys],
                                'tickvals':x_values_months,
                                },
                        yaxis={'title': 'CLV'},
                        margin=go.Margin(
                                    l=50,
                                    r=10,
                                    b=100,
                                    t=100,
                                    pad=4
                                )
                        #margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        #legend={'x': 0, 'y': 1},
                        #hovermode='closest'
                    )
            })
        ],className='four columns')
    ],className="row")
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server()



