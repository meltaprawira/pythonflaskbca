import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, Date, Float, ForeignKey

DATABASE_PATH_SCHOOL = 'C:/Users/u063476/Documents/training python/latihan1/mypy/bcaschool/school.db'

DATABASE_URI = 'sqlite:///' + DATABASE_PATH_SCHOOL
engine = create_engine(DATABASE_URI, echo=True)
metadata = MetaData()

#Mendefinisikan table 'student'
students = Table('students', metadata, 
                 Column('student_id', Integer, primary_key=True),
                 Column('name', String),
                 Column('student_class', String), 
                 Column('grade', String) 
                )

#Mendefinisikan table 'grade'
grades = Table('grades', metadata, 
                 Column('grade_id', Integer, primary_key=True),
                 Column('student_id', Integer, ForeignKey('students.student_id')),
                 Column('subject_name', String),
                 Column('score', Float),
                 Column('date', Date)
                )

#Membuat tabel
metadata.create_all(engine)

print("Database student.db dan table karyawan telah berhasil dibuat!")