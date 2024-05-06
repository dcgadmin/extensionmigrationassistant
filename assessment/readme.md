

### Installation

Extension Migration Assistant  requires [Python](https://www.python.org/ftp/python/3.11.4/python-3.11.4-embed-amd64.zip) version 3.11.4 or above to run.
Post cloning the assessment tool, we will need to install the dependencies.

#### Minimal Database Privileges on RDS or Amazon Aurora PostgreSQL Compatible

Minimal privileges needed to run on Databases.
```sql
CREATE USER sctanalyzer WITH LOGIN PASSWORD 'YourPassword';
GRANT CONNECT ON DATABASE <<YourDatabase>> TO sctanalyzer;
REVOKE CREATE ON SCHEMA public FROM sctanalyzer;

--Provide Grants to Extensions related tables, if it failes it implies no dependency with AWS SCT Extensions
grant usage on schema aws_oracle_ext to sctanalyzer;
GRANT SELECT ON table aws_oracle_ext.versions  TO sctanalyzer;
```

####  Assesment Tool Dependency

Extension Migration Assistant tool use below libraries that need to be installed as part of running.

- pandas  - used for data manipulation
- SQL alchemy - Adapter used for the database connection
- psycopg2 - For interaction with PostgreSQL.
- matplotlib - For visualization and plot graph
- numpy - Used for chart data computing
- jinja2 - required for html template rendering


```sh
cd assessment
pip3 install psycopg2-binary
pip3 install matplotlib==3.5.3
pip3 install SQLAlchemy==2.0.22
pip3 install pandas==1.3.5
pip3 install numpy==1.21.6
pip3 install Jinja2==3.1.2
```

Or

```sh
cd assessment
pip install -r requirements.txt (For Ubuntu / windows 64-bit)
pip3 install -r requirements.txt (For macOS)
```



### Running Assessment tool

Extension Migration Assistant tool will need access to PostgreSQL databases, primarily on RDS or Amazon Aurora.

```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD [--pg-schema PG_SCHEMA]
```
You can see the details of every argument required by using following steps

```sh
cd assessment
python assessment.py --help

  --host HOST           RDS/Amazon Aurora POstgreSQL Compatible Database DNS/IP address
  --port PORT           Database port number (Default - 5432)
  --database DATABASE   Database name (Default - postgres)
  --user USER           Database user
  --password PASSWORD   Database password
  --pg-schema PG_SCHEMA List of Comma separated list of schema name
```

pg-schema is optional. To see the result according to schema provide single or comma separated list.If pg-schema is not provided it will assume to run for all schema within specified database.

##### Sample 1 - running Extension Migration Assistant  with specific shcema.
```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD --pg-schema PG_SCHEMA1
```

##### Sample 2 - running Extension Migration Assistant  for multiple list of schema's.
```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD --pg-schema PG_SCHEMA1,PG_SCHEMA2
```

##### Sample 3 - running Extension Migration Assistant for all schema just skip pg-schema argument.
```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD
```

### Assessment Output

Once Extension Migration Assistant Assessment is completed, you will find newly created reports within a directory (SCTAssessment) as below
```sh
AWS SCT Extension Assessment Report created successfully
Report Generated :  SCTAssessment\sct_assessment_report.html
```
You will also get a zip file which contains the html report, charts (.png) and csv file as per input csv(csv_export) flag
```sh
SCTAssessment.zip
```


Check out [sample report](https://drive.google.com/file/d/1wvciyyuvc7ZeWTHUw1EJ2xd48WKjKCyP/view?usp=sharing) generated on sample schema migrated using AWS Schema Conversion Tool and using Extension packs(AWS_ORACLE_EXT).
