import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from jinja2 import Environment, FileSystemLoader
from matplotlib import pyplot as plt
import os
import shutil
import argparse
import numpy as np
from argparse import RawTextHelpFormatter

def load_template():
    try:
        env = Environment(loader=FileSystemLoader(''))
        template = env.get_template('SCTAssessmentReportTemplate.html')
        return template
    except Exception as e:
        print(f"{e}\nUnable to load SCTAssessmentReportTemplate.html")

def connection_arguments():
    parser = argparse.ArgumentParser(description=r'Capture AWS SCT Extension usage complexity metrics for Proprietary database migrated to RDS\Amazon Aurora PostgreSQL Compataible' , formatter_class=RawTextHelpFormatter)
    parser.add_argument('--host', required=True,help=r'RDS/Amazon Aurora PostgreSQL Compatible Database DNS/IP address')
    parser.add_argument('--port', required=False, type=int,  help=r'Database port number (Default - 5432)' , default=5432)
    parser.add_argument('--database', required=False, help=r'Database name (Default - postgres)' , default='postgres' )
    parser.add_argument('--user', required=True, help='Database user')
    parser.add_argument('--password', required=True ,help='Database password')
    parser.add_argument('--pg-schema', required=False ,help = "List of Comma separated list of schema name")
    args = parser.parse_args()
    
    try:
        alchemy_connection = f"postgresql://{args.user}:{args.password}@{args.host}:{args.port}/{args.database}"
        engine = create_engine(alchemy_connection)
        conn = engine.connect()
        return conn,args,parser
    except Exception as e:
        print(e)

def read_data_from_csv():
    try:
        data = pd.read_csv("sct_input.csv")
        aws_df = pd.read_csv("awssctcomplexitymatrix.csv")
        return data,aws_df
    except Exception as e:
        print(e)
    
def output_dir(file_name):
    parent_directory = os.getcwd()
    output_directory = r"SCTAssessment"
    path = os.path.join(parent_directory,output_directory)
    try:
        os.makedirs(output_directory, exist_ok = True)
        file_path = os.path.join(path,file_name)
        return file_path
    except OSError as e:
        print(f"Error :{e} \n Invalid directory{path}")

def chart_dir(file_name):
    parent_directory = r"SCTAssessment"
    output_directory = r"charts"
    try:
        path = os.path.join(parent_directory,output_directory)
        os.makedirs(path, exist_ok = True)
        file_path = os.path.join(path,file_name)
        return file_path
    except OSError as e:
        print(f"Error :{e} \n Invalid directory{path}")

def create_report_zip():
    output_directory = r"SCTAssessment"
    if output_directory and os.path.exists(output_directory):
        shutil.make_archive(output_directory, 'zip', output_directory)
        return True
    else:
        return False
    
def validate_extension(conn):
    try:
        query = """SELECT true as sctextensionexists
                FROM pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace LEFT JOIN pg_catalog.pg_am am ON am.oid = c.relam
                WHERE c.relkind IN ('r') AND c.relname OPERATOR(pg_catalog.~) '^(versions)$' COLLATE pg_catalog.default AND n.nspname OPERATOR(pg_catalog.~) '^(aws_.*_ext)$' COLLATE pg_catalog.default"""
        result = pd.read_sql_query(text(query), conn)
        return result["sctextensionexists"].values
    except Exception as e:
        print(f"Issue occured while validating extension existance\n{e.__cause__}")

def execution(data,aws_df,args,conn):
    results = {}
    titles = {}
    descriptions = {}

    if args.pg_schema != None:
        multiple_schema = (', '.join("'" + item + "'" for item in args.pg_schema.split(",")))
        schema = f"({multiple_schema})"
    else:
        schema = '("DBSchema")'
    try:
        if len(data.index)!=0:
            for index, row in data.iterrows():
                sql_query = row["query"]
                title = row["query_subheader"]
                merge_df = row['merge_df']
                html_result = row['html_result']
                csv_export = row["csv_export"]
                query_name = row["query_name"]
                description = row["query_description"]

                replaced_value = sql_query.replace("<<POSTGRES_SCHEMA>>", schema)
           
                if csv_export == "Y":
                    output = pd.read_sql_query(text(replaced_value),conn)
                    if len(output.index)!=0:
                        csv_file_name = f"{query_name}.csv"
                        output_path = output_dir(csv_file_name)
                        output.to_csv(output_path, index = False)

                elif html_result == "Y":
                    output = pd.read_sql_query(text(replaced_value),conn)
                    if len(output.index)!=0:
                        results[index] = output
                        titles[index] = title
                        descriptions[index] = description

                elif merge_df == "Y":
                    output = pd.read_sql_query(text(replaced_value),conn)
                    if len(output.index)!=0:
                        merged_df = output.merge(aws_df, on="AWS Extension Dependency", how = "left").sort_values(by=["DBSchema"])
                        merged_df = merged_df.astype({"SCT Function Reference Count": int, "Efforts(Hours)": int})
                        merged_df.fillna({'Function category': 'INTERNAL_NOTFOUND', 'complexity': 'COMPLEX'}, inplace=True)
                        efforts_hr = np.where(merged_df['SCT Function Reference Count'] > 1,
                                            merged_df['SCT Function Reference Count'] * merged_df['Efforts(Hours)'] * 0.3 + 
                                            merged_df['SCT Function Reference Count'] * merged_df['Efforts(Hours)'] * 0.7 * 0.5,
                                            merged_df['SCT Function Reference Count'] * merged_df['Efforts(Hours)'])
                        merged_df['Efforts(Hours)'] = efforts_hr.astype(int)
                        results[index] = merged_df
                        titles[index] = title
                        descriptions[index] = description
        
        if len(merged_df.index)!=0:
            donut_chart(merged_df, args)
            stacked_bar_chart_1(merged_df)
            stacked_bar_chart_2(merged_df) 
            return merged_df,results,titles,descriptions
    except Exception as e:
        raise e
        
def executive_summary(merged_df):
    exc_summary = {}
    schema_list = []
    total_days = (merged_df["Efforts(Hours)"].sum() / 8).round()
    schema = merged_df["DBSchema"].unique()
    distinct_function = len(merged_df["AWS Extension Dependency"].unique())

    for schema_name, schema_data in merged_df.groupby('DBSchema'):
        tshirt = schema_data.groupby('complexity')['Efforts(Hours)'].sum().idxmax()
        total_hours = schema_data['Efforts(Hours)'].sum()
        total_schema_days = (total_hours/8).round()
        top2_functions = schema_data.groupby('Function category')['Efforts(Hours)'].sum().nlargest(2).index.tolist()

        schema_list.append({
                            "DBSchema": schema_name,
                            "tshirt": tshirt,
                            "hours": total_hours ,
                            "total_days" : total_schema_days if total_schema_days > 1 else 1,
                            "top2function": top2_functions
                            })

    sorted_schema_list = sorted(schema_list, key=lambda d: d['hours'] , reverse=True)
    exc_summary.update({"totaldays": total_days if total_days > 1 else 1})
    exc_summary.update({"no_of_schema": len(schema)})
    exc_summary.update({"no_of_functions": distinct_function})
    exc_summary.update({"schema_list": sorted_schema_list})
    exc_summary.update({"schema_summary": ', '.join([f"{schema['DBSchema']}: {schema['total_days']} days" for schema in exc_summary['schema_list']])})
    return exc_summary

def render_html(results,titles,descriptions,exc_summary):
    try:
        render = template.render(results=results,titles=titles,descriptions=descriptions,exc_summary=exc_summary)
        html_file_name = "sct_assessment_report.html"
        html_path = output_dir(html_file_name)
        with open(html_path, "w") as file:
            file.write(render)
        print(f"AWS SCT Extension Assessment Report created successfully\nReport : {html_path}")
    except Exception as e:
        print(f"{e}\nUnable to generate SCT assessment report")

def donut_chart(merged_df, args):
    merged_df = merged_df.sort_values(by=["Category"])
    if args.pg_schema and len(args.pg_schema.split(',')) == 1:
        efforts = merged_df.groupby("Category")["Efforts(Hours)"].sum()
        schema = merged_df["Category"].unique()
    else:
        efforts = merged_df.groupby("DBSchema")["Efforts(Hours)"].sum()
        schema = merged_df["DBSchema"].unique()

    total_efforts = sum(efforts)
    colors = ['#05445E','#189AB4','#75E6DA','#D4F1F4']
    explode = [0.05] * len(efforts)

    fig, ax = plt.subplots(figsize=(12, 6), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(efforts, wedgeprops=dict(width=0.5), startangle=-40, explode=explode, colors=colors)

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
        label = f"{efforts.index[i]}, {percentage:.1f}%, Efforts(Hours): {count}"

        ax.annotate(label, xy=(x, y), xytext=(1.25 * np.sign(x), 1.2 * y),
                    horizontalalignment=horizontalalignment, **kw)

    ax.set_title("Efforts requirement")
    plt.tight_layout()
    file_name = 'schema_efforts.png'
    output_image_directory = chart_dir(file_name)
    plt.savefig(output_image_directory)
    plt.close()

def stacked_bar_chart_1(merged_df): 
    complexity = merged_df["complexity"].unique()
    efforts = merged_df.groupby("Function category")["Efforts(Hours)"].sum()
    efforts_sorted = efforts.sort_values(ascending=False)
    
    custom_color_map = {
                        'SIMPLE': 'lightgrey',
                        'MEDIUM': 'skyblue',
                        'COMPLEX': 'deepskyblue',
                        }
    category_colors = [custom_color_map.get(colour, 'gray') for colour in complexity]

    bar_width = 0.8
    ax = efforts_sorted.plot(kind ="barh", stacked=True, width=bar_width,  figsize=(10,6), color=category_colors)
    for p in ax.containers:
        ax.bar_label(p, label_type="edge", fontsize=8)
    plt.xlabel('Efforts(Hours)')
    plt.ylabel('Function category')
    plt.title('Efforts by Function category and Complexity')
    handles = [plt.Rectangle((0,0),1,1, color=custom_color_map[level]) for level in complexity]
    plt.legend(handles, complexity, title="Complexity")
    plt.tight_layout()
    file_name = 'functionalwiseefforts.png'
    output_image_directory = chart_dir(file_name)
    plt.savefig(output_image_directory)

def stacked_bar_chart_2(merged_df):
        grouped_data = merged_df.groupby(['DBSchema', 'complexity'])['Efforts(Hours)'].sum().unstack()
        x_labels = grouped_data.index
        complexity_colors = {
                            'SIMPLE': 'lightgrey',
                            'MEDIUM': 'skyblue',
                            'COMPLEX': 'deepskyblue',
                            }

        complexities = ["SIMPLE","MEDIUM","COMPLEX"]
        bar_width = 0.2 
        index = np.arange(len(x_labels))  
        fig, ax = plt.subplots(figsize=(10, 6))

        count_labels = []
        for i, complexity in enumerate(complexities):
            bar_data = grouped_data[complexity]
            non_zero_bars = bar_data[bar_data != 0]
            non_zero_index = index[:len(non_zero_bars)]

            bars = plt.bar(non_zero_index + i * bar_width, non_zero_bars, bar_width, label=complexity, color=complexity_colors[complexity])
            
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
        plt.title('Cumulative Efforts by DBSchema and Complexity')
        plt.xticks(index + bar_width, x_labels, rotation=90)
        plt.legend(title='Complexity',loc='upper left', ncol = 3)
        plt.tight_layout()
        file_name = 'schemawiseefforts.png'
        output_image_directory = chart_dir(file_name)
        plt.savefig(output_image_directory)
        plt.close()

if __name__== "__main__":
    template = load_template()
    conn,args,parser = connection_arguments()
    data,aws_df = read_data_from_csv()
    if validate_extension(conn):
        merged_df,results,titles,descriptions = execution(data,aws_df,args,conn)
        exc_summary = executive_summary(merged_df)
        render_html(results,titles,descriptions,exc_summary)
        if create_report_zip():
            print(f"Report zip file is created successfully")
        else:
            print("Unable to create report zip")
    else:
        print(f"AWS SCT Extension Schemas does not exists in database - {args.database}")

    
    



  



    
    
            
    


