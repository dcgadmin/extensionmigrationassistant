import pandas as pd
from sqlalchemy import create_engine, text
from jinja2 import Environment, FileSystemLoader
from matplotlib import pyplot as plt
import os
import csv
import shutil
import argparse
import numpy as np

from argparse import RawTextHelpFormatter

env = Environment(loader=FileSystemLoader(''))
template = env.get_template('SCTAssessmentReportTemplate.html')


def create_connection(host, port, database, user, password):
    alchemy_connection = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return alchemy_connection

def connection_arguments():
    parser = argparse.ArgumentParser(description='Capture AWS SCT Extension usage complexity metrics for Proprietary database \n migrated to RDS\Amazon Aurora PostgreSQL Compataible' , formatter_class=RawTextHelpFormatter)
    parser.add_argument('--host', required=True,help='RDS/Amazon Aurora POstgreSQL Compatible Database DNS/IP address')
    parser.add_argument('--port', required=False, type=int,  help='Database port number (Default - 5432)' , default=5432)
    parser.add_argument('--database', required=False, help='Database name (Default - postgres)' , default='postgres' )
    parser.add_argument('--user', required=True, help='Database user')
    parser.add_argument('--password', required=True ,help='Database password')
    parser.add_argument('--pg-schema', required=False ,help = "List of Comma separated list of schema name")

    args = parser.parse_args()

    alchemy_connection = create_connection(args.host, args.port, args.database, args.user, args.password)
    
    engine = create_engine(alchemy_connection)
    conn = engine.connect()

    return conn,args,parser

def read_data_from_csv(csv_filepath):
    data = []
    with open(csv_filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def execute_replaced_value(replaced_value,conn):
    result = conn.execute(text(replaced_value))
    return result

def donut_chart(merged_df, output_image_directory, args):
    merged_df = merged_df.sort_values(by=["Category"])
    if args.pg_schema and len(args.pg_schema.split(',')) == 1:
        
        efforts = merged_df.groupby("Category")["Efforts(Hours)"].sum()
        schema = merged_df["Category"].unique()
    else:
        efforts = merged_df.groupby("DBSchema")["Efforts(Hours)"].sum()
        schema = merged_df["DBSchema"].unique()

    total_efforts = sum(efforts)

    fig, ax = plt.subplots(figsize=(12, 6), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(efforts, wedgeprops=dict(width=0.5), startangle=-40)

    bbox_props = dict(boxstyle="square,pad=0.6", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kw["arrowprops"].update({"connectionstyle": connectionstyle})

        percentage = efforts.iloc[i] / total_efforts * 100
        count = efforts.iloc[i]
        label = f"{schema[i]}, {percentage:.1f}%, Efforts(Hours): {count}"

        ax.annotate(label, xy=(x, y), xytext=(1.25 * np.sign(x), 1.2 * y),
                    horizontalalignment=horizontalalignment, **kw)

    ax.set_title("Efforts requirement")
    plt.tight_layout()
    output_filename = os.path.join(output_image_directory, 'schema_efforts.png')
    plt.savefig(output_filename)
    plt.close()

def stacked_bar_chart_1(merged_df, output_image_directory): 
    complexity = merged_df["complexity"].unique()
    efforts = merged_df.groupby("Function category")["Efforts(Hours)"].sum()
    
    custom_color_map = {
                        'SIMPLE': 'lightgrey',
                        'MEDIUM': 'skyblue',
                        'COMPLEX': 'deepskyblue',
                        }
    category_colors = [custom_color_map.get(colour, 'gray') for colour in complexity]

    bar_width = 0.8
    ax = efforts.plot(kind ="barh", stacked=True, width=bar_width,  figsize=(10,6), color=category_colors)
    for p in ax.containers:
        ax.bar_label(p, label_type="edge", fontsize=8)
    plt.xlabel('Efforts(Hours)')
    plt.ylabel('Function category')
    plt.title('Efforts by Function category and Complexity')
    handles = [plt.Rectangle((0,0),1,1, color=custom_color_map[level]) for level in complexity]
    plt.legend(handles, complexity, title="Complexity")
    plt.tight_layout()
    output_filename = os.path.join(output_image_directory, 'functionalwiseefforts.png')
    plt.savefig(output_filename)

def stacked_bar_chart_2(merged_df, output_image_directory):
    grouped_data = merged_df.groupby(['DBSchema', 'complexity'])['Efforts(Hours)'].sum().unstack()

    x_labels = grouped_data.index
    complexity_colors = {
    'SIMPLE': 'lightgrey',
    'MEDIUM': 'skyblue',
    'COMPLEX': 'deepskyblue',
        }

    complexities = merged_df['complexity'].unique()
    bar_width = 0.2 
    index = np.arange(len(x_labels))  

    fig, ax = plt.subplots(figsize=(10, 6))

    count_labels = []
    for i, complexity in enumerate(complexities):
        bar_data = grouped_data[complexity]
        bars = plt.bar(index + i * bar_width, bar_data, bar_width, label=complexity, color=complexity_colors[complexity])

        for bar in bars:
            height = bar.get_height()
            count_labels.append(height)
            ax.annotate('{:.1f}'.format(height), 
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom')

    plt.xlabel('DBSchema')
    plt.ylabel('Efforts(Hours)')
    plt.title('Grouped Bar Chart of Efforts by DBSchema and Complexity')
    plt.xticks(index + bar_width, x_labels, rotation=90)
    plt.legend(title='Complexity',loc='upper left', ncol = 3)
    plt.tight_layout()

    output_filename = os.path.join(output_image_directory, 'schemawiseefforts.png')
    plt.savefig(output_filename)
    plt.close()   

def generate_html_report(data, df2, conn, args,parser ):
    query_subheader_content = ""
    grouped_queries = {}
    query_subheader_anchor_map = {}
    
    for item in data:
        sql_query = item['query']
        merge_df = item['merge_df']
        html_result = item['html_result']
        csv_export = item["csv_export"]
        query_name = item["query_name"]

        if not args.pg_schema:
            replaced_value = sql_query.replace("<<POSTGRES_SCHEMA>>", f'("DBSchema")')

        else:
            schemaList = (', '.join("'" + item + "'" for item in args.pg_schema.split(',')))
            replaced_value = sql_query.replace("<<POSTGRES_SCHEMA>>", f"({schemaList})")

        if csv_export == "Y" or html_result == "Y" or merge_df == "Y":
            result_df = pd.DataFrame() 
            if replaced_value:
                result = execute_replaced_value(replaced_value, conn)

                result_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                if  csv_export == "Y":
                    result_df.to_csv(os.path.join(output_directory, f"{query_name}.csv"), index=False)    
            
            if query_name == 'sctextensions' and not result_df["SCT Oracle Extension Exists"].item():
                item['query_result'] = result_df
                merged_df = pd.DataFrame()
                query_subheader = item.get('query_subheader', '')

                if (html_result == "Y" or merge_df == "Y") and query_subheader:
                    if query_subheader not in grouped_queries:
                        grouped_queries[query_subheader] = []
                        anchor_name = f"anchor_{len(grouped_queries)}"
                        query_subheader_anchor_map[query_subheader] = anchor_name

                    grouped_queries[query_subheader].append(item)
                break;

            if merge_df == "Y":
                merged_df = result_df.merge(df2, on="AWS Extension Dependency", how = "left") 
                merged_df['Efforts(Hours)'] = pd.to_numeric(merged_df['Efforts(Hours)'], errors='coerce').fillna("4")
                merged_df['SCT Function Reference Count'] = merged_df['SCT Function Reference Count'].apply(int)
                merged_df["Efforts(Hours)"] = merged_df["Efforts(Hours)"].apply(int)
                merged_df['Function category'].fillna('INTERNAL_NOTFOUND', inplace=True)
                merged_df['complexity'].fillna('COMPLEX', inplace=True)
                merged_df = merged_df.sort_values(by=["DBSchema", "Category"])
                efforts_hr = 0
                for ind in merged_df.index:
                    if  merged_df['SCT Function Reference Count'][ind] > 1:
                        efforts_hr = int(merged_df['SCT Function Reference Count'][ind] * merged_df['Efforts(Hours)'][ind] * 0.3 + merged_df['SCT Function Reference Count'][ind] * merged_df['Efforts(Hours)'][ind] * 0.7 * 0.5)
                    else:
                        efforts_hr = int(merged_df['SCT Function Reference Count'][ind] * merged_df['Efforts(Hours)'][ind])
                    merged_df.at[ind, 'Efforts(Hours)'] = efforts_hr
                merged_df["Efforts(Hours)"] = round(merged_df["Efforts(Hours)"],0).apply(int)
                item['query_result'] = merged_df

                total_efforts_sum = merged_df['Efforts(Hours)'].sum()
                query_description = item.get('query_description', '')
                query_description += f" (Total Efforts Sum: {total_efforts_sum})"
                item['query_description'] = query_description
            else:
                item['query_result'] = result_df

            query_subheader = item.get('query_subheader', '')

            if (html_result == "Y" or merge_df == "Y") and query_subheader:
                if query_subheader not in grouped_queries:
                    grouped_queries[query_subheader] = []
                    anchor_name = f"anchor_{len(grouped_queries)}"
                    query_subheader_anchor_map[query_subheader] = anchor_name

                grouped_queries[query_subheader].append(item)
        
    for query_subheader, anchor_name in query_subheader_anchor_map.items():
        query_subheader_content += f'<li><a class="content-link" href="#{anchor_name}">{query_subheader}</a></li>'

    rendered_html = template.render(query_subheader_content=query_subheader_content, grouped_queries=grouped_queries, query_subheader_anchor_map=query_subheader_anchor_map)
    return rendered_html, merged_df,rendered_html

def save_html_report(html_content, output_filename,output_image_directory):
    with open(output_filename, 'w') as f:
        f.write(html_content)
    return html_content

if __name__== "__main__":

    csv_filepath = r"sct_input.csv" 
    csv_aws = r"awssctcomplexitymatrix.csv"
    working_directory = r""
    output_directory = r"SCTAssessment"
    csv_directory = r"SCTAssessment\csv" 
    conn,args,parser = connection_arguments()

    path = os.path.join(working_directory, output_directory)
    os.makedirs(path, exist_ok=True)
    output_file = os.path.join(path,"sct_assessment_report.html")
    output_image_directory = os.path.join(output_directory, 'charts')
    os.makedirs(output_image_directory, exist_ok=True)
    df2 = pd.read_csv(csv_aws)
    data = read_data_from_csv(csv_filepath)
    html_content, merged_df, rendered_html = generate_html_report(data, df2, conn, args, parser)

    if not merged_df.empty:
        donut_chart(merged_df, output_image_directory, args)
        stacked_bar_chart_1(merged_df, output_image_directory)
        stacked_bar_chart_2(merged_df, output_image_directory)
    save_html_report(html_content, output_file, output_image_directory)
    output_archive_path = 'SCTAssessment/sct_assessment_report'
    shutil.make_archive(output_archive_path, 'zip', output_directory)
    print("AWS SCT Extension Assessment Report created successfully")
    output = r"SCTAssessment\sct_assessment_report.html"
    print("Report Generated :  "+  output)
    pdf_output_filename = os.path.join(output_directory, "sct_assessment_report.pdf")



    
    
            
    


