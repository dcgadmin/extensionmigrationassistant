
# Introduction
The AWS SCT Extension is primarily introduced as part of the conversion process from a commercial engine to an open-source compatible option like PostgreSQL when using the AWS Schema Conversion Tool. It serves to conceal the procedural complexity by utilizing wrapper code defined within extensions stored as schemas, such as aws_oracle_ext, aws_sqlserver_ext, and others.

For customers migrating from a commercial engine like Oracle to SQL Server, the Extension Pack acts as a proprietary toolset. AWS SCT introduces it as wrapper code that mimics the functionality of commercial engine features or functions. This wrapper code is encapsulated within schemas and is extensively leveraged in the converted code.

<img width="454" alt="image" src="https://github.com/dcgadmin/sctextensionmigrator/assets/137620464/e6797f5f-3917-4d8b-8b31-e6e57ddc1732">


Below are some of the pros and cons of using AWS SCT Extension Pack on migrated databases primary on RDS or Amazon Aurora

## Value to Customer

- Build-In Migration pattern to mitigate complex Oracle functions or DBMS_* packages.
- Reduction in Code conversion efforts for enterprise scale migrations.

## Cons 

- Known Performance issues with Extension pack.
- Reduce Code readability.
- No Documentation and version support.
- Efforts to undo SCT Changes and rewrite if Customer asked for Native Support(PostgreSQL/orafce) as no flag to disable it.

# How AWS Extension Pack is Introduce

The AWS SCT Extension Pack is highly beneficial for migrating workloads from commercial engines to AWS Database targets like RDS or Amazon Aurora PostgreSQL. It significantly accelerates the conversion process and simplifies the migration to managed instances.

To illustrate its functionality, let's consider a sample function, INSTR, commonly used in the Oracle world for text or string processing. During the conversion phase, the AWS SCT tool utilizes the Extension Pack to transform each occurrence of INSTR within procedural code into AWS_ORACLE_EXT.INSTR. Internally, AWS_ORACLE_EXT.INSTR provides the wrapped implementation for INSTR functionality, similar to how it operates in Oracle.

However, it's important to note that, over time, customers who have migrated their databases to AWS PostgreSQL-compatible instances may encounter challenges if they decide to migrate to Google Cloud's PostgreSQL-compatible options. This challenge arises due to the dependencies and inherent stickiness of the Extension Pack.

<img width="1113" alt="image" src="https://github.com/dcgadmin/sctextensionmigrator/assets/137620464/bb79ce83-e010-48ec-92b7-5283ff7ff5cc">


# SCT Extension Assessment

Customer awareness of extension dependencies and their usage within the overall database schema or code is crucial for those migrated to AWS databases like RDS or Amazon Aurora and using extension code beneath procedural functionalty.

Through the assessment process, we can scan the migrated code in PostgreSQL or MySQL and capture usage patterns and dependencies on various extension pack functions. The extent to which extension pack features are leveraged during migrations from commercial engines to AWS databases varies depending on the complexity of the database.

By analyzing the usage patterns, we can categorize the dependency on the extension pack as Simple, Medium, or Complex. This categorization helps to highlight the efforts required to address extension dependencies and resolve them using native PostgreSQL solutions.


## Installation

SCT assessment requires [Python](https://www.python.org/ftp/python/3.11.4/python-3.11.4-embed-amd64.zip) version 3.11.4 or above to run.
Post cloning the assessment tool, we will need to install the dependencies.


###  Assesment Tool Dependency

SCT Migrator assessment tool use below libraries that need to be installed as part of running.

- pandas  - used for data manipulation
- SQL alchemy - Adapter used for the database connection
- psycopg2 - For interaction with PostgreSQL.
- matplotlib - For visualization and plot graph
- numpy - Used for chart data computing
- jinja2 - required for html template rendering


```sh
cd sct_assessment
pip3 install psycopg2-binary
pip3 install matplotlib==3.5.3
pip3 install SQLAlchemy==2.0.22
pip3 install pandas==1.3.5
pip3 install numpy==1.21.6
pip3 instal Jinja2==3.1.2
```

Or

```sh
cd sct_assessment
pip install -r requirements.txt (For windows 64-bit)
pip3 install -r requirements.txt (For macOS)
```



## Running Assessment tool

SCT assessment tool will need access to PostgreSQL databases, primarily on RDS or Amazon Aurora.

```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD [--pg-schema PG_SCHEMA]
```
You can see the details of every argument required by using following steps

```sh
cd sct_assessment
python assessment.py --help

  --host HOST           RDS/Amazon Aurora POstgreSQL Compatible Database DNS/IP address
  --port PORT           Database port number (Default - 5432)
  --database DATABASE   Database name (Default - postgres)
  --user USER           Database user
  --password PASSWORD   Database password
  --pg-schema PG_SCHEMA List of Comma separated list of schema name
```

pg-schema is optional. To see the result according to schema provide single or comma separated list.If pg-schema is not provided it will assume to run for all schema within specified database.

#### Sample 1 - running SCT assessment with specific shcema.
```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD --pg-schema PG_SCHEMA1
```

#### Sample 2 - running SCT assessment for multiple list os schema's.
```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD --pg-schema PG_SCHEMA1,PG_SCHEMA2
```

#### Sample 3 - running SCT assessment for all schema just skip pg-schema argument.
```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD
```

## Assessment Output

Once SCT Assessment is completed, you will find newly created reports within a directory (SCTAssessment) as below
```sh
AWS SCT Extension Assessment Report created successfully
Report Generated :  SCTAssessment\sct_assessment_report.html
```
You will also get a zip file which contains the html report, charts (.png) and csv file as per input csv(csv_export) flag
```sh
SCTAssessment.zip
```


Check out [sample report](https://drive.google.com/file/d/1xnmCv7-FyDz6SkgHdYidCDBeGTObofON/view?usp=sharing) generated on sample schema migrated using AWS SCT and using AWS_ORACLE_EXT.
