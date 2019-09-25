import os
import csv
import psycopg2
import argparse



"""
This is a basic postgres connection method.By default this will connect to the postgres instance
set in environment variable.For this assignment only ODS connection is defined
"""




def get_postgres_con(v_con_name='ODS'):
    if v_con_name=='ODS':
        conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'],
                                port=os.environ['POSTGRES_PORT'],
                                user=os.environ['POSTGRES_USER'],
                                password=os.environ['POSTGRES_PASSWORD'],
                                dbname=os.environ['POSTGRES_DB'])
        print (" Connected to  " + str(os.environ['POSTGRES_HOST']))
        return conn
    else:
        print('Connection Not Defined')
        return None

"""
This is a the base class for complete ETL from defining meta to Loading the data
"""

class DataLoad:

    """ Intialization expecting input file path and filename ,all other variables are 
        optional.If nothing is provided by default file delim will be ',' and db will be ODS
        and schema will be public
    """

    def __init__(self,input_path,filename,delim=',',db='ODS',schema='public'):

        self.input_path=input_path
        self.filename=filename
        self.ddl = {}

        if not delim:
            self.delim=','
        else:
            self.delim = delim

        if not schema:
            self.schema='public'
        else:
            self.schema = schema

        if not db:
            self.db='ODS'
        else:
            self.db=db


    """
    This method will infer the schema and will create ddl for the table.Table name will be name 
    of the input file .The table will be always drop create by default.Columns datatype will be
    text so that dataload will never fail due to datatype issues
    """

    def create_table_ddl(self):
        input_file = os.path.join(self.input_path, self.filename)
        f = open(input_file, 'r')
        reader = csv.reader(f, delimiter=self.delim)
        col_lst=next(reader)
        self.col_lst=col_lst
        print(self.col_lst)
        self.ncol = len(col_lst)  # Read first line and count columns
        f.close()
        my_func= lambda x:x+' text ' if len(x)>0 else ''

        col_ddl =list(map(my_func ,col_lst))
        col_ddl= 'idxid bigint ,'+','.join(col_ddl).strip(',')

        self.table_name=self.filename.split('.')[0]

        crt_ddl=" create table {schema}.{tab_name} ({col_ddl})".\
            format(tab_name=self.table_name,col_ddl=col_ddl,schema=self.schema)

        self.ddl[self.table_name]=crt_ddl

        print (self.ddl)

    """
    This method will infer  create ddl for the rejected record table.Table name will be name 
    of the input file_rejected .The table will be always drop create by default.Columns datatype will be
    text.Each rejected row will be assigned with an index for better representation
    """

    def create_rejected_ddl(self):
        if self.max_columns==0:
            print('No rejected records')
        else:
            self.table_name_rejected = self.table_name+'_rejected'


            crt_ddl_rejected = " create table {schema}.{tab_name} (idxid bigint,text_data text)". \
                format(tab_name=self.table_name_rejected,schema=self.schema)
            self.ddl[self.table_name_rejected]=crt_ddl_rejected

    """
    This method will parse the input file and split that into clean data and rejected data.
    File delimeter will be replaced by '|' and quotes will be replaced by '~' for robustness
    """

    def parse_data(self):

        input_file = os.path.join(self.input_path, self.filename)
        f = open(input_file, 'r')
        reader = csv.reader(f, delimiter=self.delim)
        col_lst=next(reader)
        col_ddl = 'idxid,'+','.join(col_lst).strip(',')
        print(col_ddl)


        output_file = os.path.join(self.input_path, 'formatted_' + self.filename)
        output_format= open(output_file, 'w')
        output_format.write(str(col_ddl)+'\n')


        output_file_rejected = os.path.join(self.input_path, 'rejected_' + self.filename)
        output_reject = open(output_file_rejected, 'w')
        output_reject.write('idxid|text_data'+'\n')

        reader = csv.reader(f, delimiter=self.delim)
        lst=[0]
        for i,row in enumerate(reader):

            """splitting data into 2 parts one with proper schema formatted_file
            ,one rejected data rejected file.Removing single quotes and double quotes from the data
            converting delimter to '|' which is more robust since ',' could be present in data
            """

            if self.ncol == len(row):
                table_txt =  '~'+str(i)+'~|~'+'~|~'.join(row)+'~'
                output_format.write(str(table_txt) + '\n')

            if self.ncol != len(row) and len(row)>0:
                lst.append(len(row))
                table_txt = '~'+str(i)+'~|~'+self.delim.join(row)+'~'
                output_reject.write(str(table_txt) + '\n')

        f.close()
        output_reject.close()
        output_format.close()

        """Setting file name So that other methods can access the same"""
        self.output_file_rejected=output_file_rejected
        self.output_file = output_file
        self.max_columns=max(lst)

    """
    This is a simple method which is loading flat file to Postgres Table.File location can
    be any location in client machine.Delimeter is a parameter.Table name and file name are
    mandatory parameters for this method
    """



    def postgres_data_load(self,table_name, file_name,con_name='ODS', delim=',',quotes='"'):



        self.src_table_name=table_name

        conn=get_postgres_con(con_name)

        SQL_STATEMENT = """ COPY {schema}.{tab_name} FROM STDIN WITH CSV HEADER NULL AS '' QUOTE '{qt}' DELIMITER AS '{delim}'  """.format(
            tab_name=table_name,schema=self.schema, delim=delim,qt=quotes)
        my_file = open(file_name)

        drop_ddl = "drop table IF EXISTS {schema}.{tab_name}".format(tab_name=table_name,schema=self.schema)
        cursor = conn.cursor()
        cursor.execute(drop_ddl)
        print(self.ddl[table_name])
        cursor.execute(self.ddl[table_name])
        print("COPY Command -", SQL_STATEMENT)
        cursor.copy_expert(sql=SQL_STATEMENT, file=my_file)

        if file_name==self.output_file:

            grp_by_col=','.join(self.col_lst)

            drop_ddl = "drop table IF EXISTS {schema}.fact_{tab_name}".format(tab_name=table_name,schema=self.schema)
            
            cursor.execute(drop_ddl)

            ##for fact creation we can add any of the filtering condition

            crt_qry="""create table {schema}.fact_{tab_name} as 
                    select distinct {col} from {schema}.{tab_name}""".format(tab_name=table_name,schema=self.schema,col=grp_by_col)

            cursor.execute(crt_qry)

            dist_cnt='select count(*)  from {schema}.fact_{tab_name}'.format(tab_name=table_name,schema=self.schema)






        elif file_name==self.output_file_rejected:


            drop_ddl = "drop table IF EXISTS {schema}.fact_{tab_name}".format(tab_name=table_name,schema=self.schema)
            
            cursor.execute(drop_ddl)

            ##for fact creation we can add any of the filtering condition

            crt_qry="""create table {schema}.fact_{tab_name} as 
                    select distinct text_data from {schema}.{tab_name}""".format(tab_name=table_name,schema=self.schema)

            cursor.execute(crt_qry)

            dist_cnt='select count(*)  from {schema}.fact_{tab_name}'.format(tab_name=table_name,schema=self.schema)


        else:
            ## for any other use case we can extend this .For simplicity defined main 2 scenarios
            dist_cnt = "select 'NA'"


        print(dist_cnt)
        cursor.execute(dist_cnt)
        cnt=cursor.fetchone()[0]
        print('No of rows loaded: '+str(cnt))

        conn.commit()
        cursor.close()

        return cnt


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='You can add a description here')

    parser.add_argument('-l','--fileloc', help='Input filename location',required=True)
    parser.add_argument('-f','--filename', help='File name to load ',required=True)
    parser.add_argument('-d', '--delim', help='File delimeter ', required=False)
    parser.add_argument('-db','--database', help='Database for the table ',required=False)
    parser.add_argument('-s', '--schema', help='Target Schema for the table ', required=False)

    args = parser.parse_args()

    print(args)


    dataload = DataLoad(args.fileloc, args.filename,args.delim,args.database,args.schema)

    dataload.create_table_ddl()
    dataload.parse_data()
    dataload.create_rejected_ddl()

    dataload.postgres_data_load(dataload.table_name, dataload.output_file,dataload.db, '|','~')

    #checking for the rejected data
    if dataload.max_columns > 0:
        dataload.postgres_data_load(dataload.table_name_rejected, dataload.output_file_rejected, dataload.db, '|','~')



