import unittest
from flask_testing import TestCase
from flask import url_for
from dataschool import app, db, Students, Grades  # Import modul-modul yang diperlukan
from datetime import datetime

# Kelas MyTest untuk melakukan testing pada aplikasi
class MyTest(TestCase):

    # Metode untuk membuat aplikasi dalam mode testing
    def create_app(self):
        app.config['TESTING'] = True  # Mengaktifkan mode testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'  # Menggunakan database in-memory untuk testing
        return app

    # Metode yang dijalankan sebelum setiap test
    def setUp(self):
        db.create_all()  # Membuat semua tabel dalam database

    # Metode yang dijalankan setelah setiap test
    def tearDown(self):
        db.session.remove()  # Menghapus sesi database
        db.drop_all()  # Menghapus semua tabel dalam database

    # Test untuk endpoint index '/'
    def test_index(self):
        response = self.client.get('/')  # Melakukan request GET ke '/'
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('index.html')  # Memastikan template yang digunakan adalah 'index.html'

    # Test untuk membuat grade baru
    def test_creates_student(self):
        # Melakukan request POST ke '/karyawan' dengan data karyawan baru
        response = self.client.post('/school/student', json={
            'name': 'Sem',
            'student_class': '8',
            'grade': 'A'
        })
        self.assertStatus(response, 201)  # Memastikan response adalah 201 Created
        student = Students.query.first()  # Mengambil karyawan pertama dari database
        self.assertEqual(student.name, 'Sem')  # Memastikan nama karyawan adalah 'John Doe'

    # Test untuk membuat grade baru
    def test_creates_grades(self):
        # Melakukan request POST ke '/grade' 
        responseStudent = self.client.post('/school/student', json={
            'name': 'Sem',
            'student_class': '8',
            'grade': 'A'
        })
        self.assertStatus(responseStudent, 201)  # Memastikan response adalah 201 Created

        response = self.client.post('/school/grade', json={
            'student_id': '1',
            'subject_name': 'pkn',
            'score': '100',
            'date': '2023-09-29'
        })
        self.assertStatus(response, 201)  # Memastikan response adalah 201 Created
        # grade = Grades.query.first()  # Mengambil karyawan pertama dari database
        # self.assertEqual(grade.sudent_id, '1')  # Memastikan nama karyawan adalah 'John Doe'

    # Test untuk menghapus karyawan
    def test_delete_student(self):
        # Membuat objek karyawan baru dan menyimpannya ke database
        student = Students(name='Talia', student_class='8', grade='A')
        db.session.add(student)
        db.session.commit()

        # Melakukan request DELETE ke '/karyawan/{id_karyawan}'
        response = self.client.delete(f'/school/student/{student.student_id}')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assertIsNone(Students.query.get(student.student_id))  # Memastikan karyawan dengan id tersebut sudah dihapus

    # Test untuk mendapatkan semua karyawan
    def test_get_all_student(self):
        # Membuat dua objek karyawan baru dan menyimpannya ke database
        student1 = Students(name='Filbert', student_class='9', grade='A')
        student2 = Students(name='Jane', student_class='9', grade='A')
        db.session.add(student1)
        db.session.add(student2)
        db.session.commit()

        # Melakukan request GET ke '/display_all'
        response = self.client.get('/display_all_student')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('displayall.html')  # Memastikan template yang digunakan adalah 'displayall.html'
        self.assertIn(b'Filbert', response.data)  # Memastikan 'Filbert' ada dalam response data
        self.assertIn(b'Jane', response.data)  # Memastikan 'Jane' ada dalam response data

    # Test untuk mendapatkan satu karyawan berdasarkan id
    def test_get_one_student(self):
        # Membuat objek karyawan baru dan menyimpannya ke database
        student = Students(name='Doe', student_class='9', grade='A')
        db.session.add(student)
        db.session.commit()

        # Melakukan request GET ke 'school/display_student/{student.student_id}'
        response = self.client.get(f'/school/display_student/{student.student_id}')
        self.assert200(response)  # Memastikan response adalah 200 OK


    # Test untuk mendapatkan semua grade
    def test_get_all_grade(self):
        # Membuat dua objek karyawan baru dan menyimpannya ke database
        grade1 = Grades(student_id='1', subject_name='BI', score=90, date=datetime.strptime('2023-09-29','%Y-%m-%d'))
        grade2 = Grades(student_id='1', subject_name='Matematika', score=93, date=datetime.strptime('2023-09-29','%Y-%m-%d'))
        db.session.add(grade1)
        db.session.add(grade2)
        db.session.commit()

        # Melakukan request GET ke '/display_all'
        response = self.client.get('/school/display_all_grade')
        self.assert200(response)  # Memastikan response adalah 200 OK


    # Test untuk menghapus karyawan melalui UI
    def test_delete_grade(self):
        # Membuat objek karyawan baru dan menyimpannya ke database
        grade = Grades(student_id='1', subject_name='Biologi', score=90, date=datetime.strptime('2023-09-29','%Y-%m-%d'))
        db.session.add(grade)
        db.session.commit()

        response = self.client.delete(f'/school/grade/{grade.grade_id}')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assertIsNone(Students.query.get(grade.grade_id))  # Memastikan karyawan dengan id tersebut sudah dihapus

if __name__ == '__main__':
    unittest.main()  # Menjalankan semua test