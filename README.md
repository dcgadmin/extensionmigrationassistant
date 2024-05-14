# Extension Migration Assistance.

Our Goal is to transform any migration to PostgreSQL or PostgreSQL Compatible on AWS as Open, Agile and Free from any kind of lockin. The aim is to provide customers moved away from commercial database engines like Oracle or MSSQL in past or planning to move with the freedom to choose any platform without hidden restrictions or stickiness or proprietary extensions.


### Introduction
An Extension is primarily introduced as part of the conversion process from a commercial engine like Oracle or SQL Server to an open-source compatible option like PostgreSQL when using the AWS Schema Conversion Tool. It serves to conceal the procedural complexity by utilizing wrapper code defined within extensions stored as schemas, such as aws_oracle_ext, aws_sqlserver_ext, and others.

For customers migrating from a commercial engine like Oracle to SQL Server, the Extension Pack acts as a proprietary toolset. Conversion Tool introduces it as wrapper code that mimics the functionality of commercial engine features or functions. This wrapper code is encapsulated within schemas and is extensively leveraged in the converted PL\pgsql code. In future it will act as invisible lock-in to move out of AWS.

<img width="700" alt="image" src="https://github.com/dcgadmin/extensionmigrationassistant/assets/52906469/927b315b-90fa-4726-9f4b-430826586e76">


Below are some of the pros and cons of using Conversion Extension Pack on migrated databases primary on RDS or Amazon Aurora PostgreSQL Compatible.

### Initial Value to Customer

- Build-In Migration pattern to mitigate complex Proprietary functions or DBMS_* packages.
- Reduction in Code conversion person efforts for enterprise scale migrations.

### Cons 

- Tightly coupled with a Specific Cloud Vendor and not open to move freely.
- Reduce Code readability and future development or refactor.
- No Documentation, Maintainence for future postresql releases or enhancement.
- Known Performance issues with Extension pack.

### How Conversion Extension Pack is Introduce

The Extension Pack is beneficial for accelerating and migrating workloads from commercial engines to AWS Database targets like RDS or Amazon Aurora PostgreSQL. It significantly accelerates the conversion process and simplifies the migration to managed instances.

To illustrate its functionality, let's consider a sample function, INSTR, commonly used in the Oracle world for text or string processing. During the conversion phase, the Conversion tool utilizes the Extension Pack to transform each occurrence of INSTR within procedural code into AWS_ORACLE_EXT.INSTR. Internally, AWS_ORACLE_EXT.INSTR provides the wrapped implementation for INSTR functionality, similar to how it operates in Oracle.

However, it's important to note that, over time, customers who have migrated their databases to  PostgreSQL-compatible instances may encounter challenges if they decide to migrate to any another cloud vendor or self host instance on another platform. This challenge arises due to the dependencies and inherent stickiness of the Extension Pack and its usage applicable only when you are within that specific cloud vendor.

<img width="1113" alt="image" src="https://github.com/dcgadmin/sctextensionmigrator/assets/137620464/bb79ce83-e010-48ec-92b7-5283ff7ff5cc">

<br />

AWS Schema Conversion Tool - Default Conversion.
<br />

<img width="1113" alt="image" src="https://github.com/dcgadmin/extensionmigrationassistant/assets/52906469/2c0bf5f6-a94b-4843-9249-0eee38c5f849">

### Extension Pack Dependency Assessment

Customer awareness of extension dependencies and their usage within the overall database schema or code is crucial for those migrated to  databases like RDS or Amazon Aurora and using extension code beneath procedural functionalty.

Through our assessment process, we can scan the migrated code in PostgreSQL or MySQL and capture usage patterns and dependencies on various extension pack functions. The extent to which extension pack features are leveraged during migrations from commercial engines to RDS\Amazon Aurora databases varies depending on the complexity of the database.

By analyzing the usage patterns, we can categorize the dependency on the extension pack as Simple, Medium, or Complex. This categorization helps to highlight the efforts required to address extension dependencies and resolve them using native PostgreSQL solutions like Orafce or native functionality.

### Extension Pack Dependency Assessment - Sample Report
Check out Extension assessment sample report run on RDS PostgreSQL for sample Oracle schema migrated using AWS Schema Conversion Tool.

[sample report](https://drive.google.com/file/d/1b3kvWF0jE6zo3S0WAfZ7_MxdUVghNjCr/view?usp=sharing) 

### Extension Dependency Assessment - Installation
For further read on installtion and generating extension dependency report, please check out.
https://github.com/dcgadmin/extensionmigrationassistant/blob/main/assessment/readme.md

### Contact Details for further details

If you are looking for automated solution to transform embedded extensions packs within procedural or schema, let us know we an assist and provide guidance.
Our motto is to make yours database codebases as native and open for all platform.

contact@datacloudgaze.com
