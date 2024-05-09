

### Installation

Extension Migration Assistant  requires [Python](https://www.python.org/ftp/python/3.11.4/python-3.11.4-embed-amd64.zip) version 3.11.4 or above to run.
Post cloning the assessment tool, we will need to install the dependencies.

#### Minimal Database Privileges on RDS or Amazon Aurora PostgreSQL Compatible

Minimal required privileges to run on PostgreSQL Databases.
```sql
CREATE USER sctanalyzer WITH LOGIN PASSWORD 'YourPassword';
GRANT CONNECT ON DATABASE <<YourDatabase>> TO sctanalyzer;
REVOKE CREATE ON SCHEMA public FROM sctanalyzer;

--Provide Grants to Extensions related tables, if it failes it implies no dependency with AWS SCT Extensions
grant usage on schema aws_oracle_ext to sctanalyzer;
GRANT SELECT ON table aws_oracle_ext.versions  TO sctanalyzer;
```

####  Assesment Tool Installation Dependency

Steps to clone and run extensionmigrationassistance on RDS or Amazon Aurora PostgreSQL Databases.

-step 1 : clone sctextensionassessment repo 
```sh
git clone https://github.com/dcgadmin/extensionmigrationassistant.git
```
-step 2 : Create virtual environment using python(Optional, we can follow Step 4 onwards as well)
```sh
python -m venv <<environment_name>>
```
-step 3 : Activate virtual environment
```sh
<<environment_name>>\Scripts\activate
```
-step 4 : switch to project directory
```sh
cd extensionmigrationassistant\assessment
```
-step 5 : install dependencies using pip3/pip and requirement.txt

```sh
pip install -r requirements.txt (For Ubuntu / windows 64-bit)
pip3 install -r requirements.txt (For macOS)
```

### Running Assessment tool

Extension Migration Assistant tool will need access to PostgreSQL databases, primarily on RDS or Amazon Aurora.

```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD [--pg-schema PG_SCHEMA] [--outputpath OUTPUTPATH]
```
You can see the details of every argument required by using following steps

```sh
cd assessment
python assessment.py --help

  --host HOST               RDS/Amazon Aurora PostgreSQL Compatible Database endpoint
  --port PORT               Database port number (Default - 5432)
  --database DATABASE       Database name (Default - postgres)
  --user USER               Database user
  --password PASSWORD       Database password
  --pg-schema PG_SCHEMA     List of Comma separated list of schema name(Optional)
  --outputpath OUTPUTPATH   Provide output path of report (Optional)
```

pg-schema is optional. To see the result according to schema provide single or comma separated list.If pg-schema is not provided it will assume to run for all schema within specified database.

##### Sample 1 - running Extension Migration Assistant on specific shcema.
```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD --pg-schema PG_SCHEMA1
```

##### Sample 2 - running Extension Migration Assistant on multiple list of schema's.
```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD --pg-schema PG_SCHEMA1,PG_SCHEMA2
```

##### Sample 3 - running Extension Migration Assistant for all schema.
```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD
```

##### Sample 4 - running Extension Migration Assistant for all schema with output to specific path
```sh
python assessment.py --host HOST [--port PORT] [--database DATABASE] --user USER --password PASSWORD --outputpath <<OUTPUT_PATH>>
```

### Assessment Output

Once Extension Migration Assistant Assessment is completed, you will find newly created reports within a directory (SCTExtensionAssessment) as below
```sh
AWS SCT Extension Assessment Report created successfully
Report : ....\extensionassessmentreport.html
Report zip file is created successfully
```
You will also get a zip file which contains the html report, charts (.png) and csv file with additional dependencies details.
```sh
SCTExtensionAssessment.zip
```


Check out [sample report](https://drive.google.com/file/d/1b3kvWF0jE6zo3S0WAfZ7_MxdUVghNjCr/view?usp=sharing) generated on sample schema migrated using AWS Schema Conversion Tool to RDS PostgreSQL with its underlying Extension packs(AWS_ORACLE_EXT).
