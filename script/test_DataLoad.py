from DataLoad import DataLoad




## 

md=DataLoad('/data/your_loc/CSV/','test.csv')


md.create_table_ddl()
md.parse_data()
md.create_rejected_ddl()

cnt_data=md.postgres_data_load(md.table_name, md.output_file, md.db, '|', '~')

assert cnt_data==10,'Data Load failed for good records'

assert md.max_columns==15 ,' Schema validation failed'
# checking for the rejected data

cnt_data_rejected=md.postgres_data_load(md.table_name_rejected, md.output_file_rejected, md.db, '|', '~')

assert cnt_data_rejected==3,'Data Load failed for bad records'

print ('Dataload testing success')