from flask import Flask, jsonify, request, render_template, Response, json
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from
from datetime import datetime

import os

#Mendifiniskan app
app = Flask(__name__)

#Lokasi database
DATABASE_PATH_SCHOOL = 'C:/Users/u063476/Documents/training python/latihan1/mypy/bcaschool/school.db'


#Konfigurasi database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH_SCHOOL
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False


#Konfigurasi Swagger
app.config['SWAGGER']={
    'title':'Data School BCA API',
    'uiversion':3,
    'headers':[],
    'specs':[
        {
            'endpoint':'apispec_1',
            'route':'/apispec_1.json',
            'rule_filter':lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/apidocs/'
}

swagger = Swagger(app)

db = SQLAlchemy(app)

# create table
@app.before_request
def create_tables():
    db.create_all()

    
#Model Data Karyawan
class Students(db.Model):
    student_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    student_class = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(100))

class Grades(db.Model):
    grade_id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    subject_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False )
    # students = db.relationship("Students", backref=backref("students", uselist=False))

@app.route('/')
def index():
    return render_template('index.html')

#Koneksi API Create Student
@app.route('/school/student', methods=['POST'])
@swag_from('swagger_docs/create_data_student.yaml')
def create_student():
    #mendapatkan data dari permintaan POST
    data = request.json

    #Membuat objek karyawan
    new_student = Students(
        name=data['name'],
        student_class=data['student_class']
        # grade=data['grade']
    )
    #Menyimpan objek ke database
    db.session.add(new_student)
    db.session.commit()

    #Mengembalikan respons HTTP201 Created
    return jsonify({'message':'Data Siswa berhasil ditambahakan'}),201

#Koneksi create student from ui
@app.route('/input_student', methods=['GET', 'POST'])
def input_student():
    if request.method == 'POST':
        name = request.form.get('name')
        student_class = request.form.get('student_class')

        if not name or not student_class:
            return render_template('createdata-student.html', error="Semua field wajib diisii")

        new_student = Students(
            name = name, 
            student_class = student_class
        )

        db.session.add(new_student)
        db.session.commit()

        #Mengarahkan ke halaman konfirmasi
        return render_template('confirmation.html')
    else:
        return render_template('createdata-student.html')

#Koneksi API Create Grade
@app.route('/school/grade', methods=['POST'])
@swag_from('swagger_docs/create_data_grade.yaml')
def create_grade():
    #mendapatkan data dari permintaan POST
    data = request.json

    #Membuat objek karyawan
    new_grade = Grades(
        subject_name=data['subject_name'],
        score=data['score'],
        date=data['date']
    )

    #Menyimpan objek ke database
    db.session.add(new_grade)
    db.session.commit()

    #Mengembalikan respons HTTP201 Created
    return jsonify({'message':'Data Nilai berhasil ditambahakan'}),201

#Koneksi create grade from ui
@app.route('/input_grade', methods=['GET', 'POST'])
def input_grade():
    print("masuk input post", request.method)

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject_name = request.form.get('subject_name')
        score=request.form.get('score')
        date=datetime.strptime(request.form.get('date'),'%Y-%m-%d')

        if not student_id or not subject_name or not score :
            return render_template('createdata-grade.html', error="Semua field wajib diisii")
        print("masuk input post")
        new_grade = Grades(
            student_id = student_id, 
            subject_name = subject_name,
            score = score,
            date=date
        )

        db.session.add(new_grade)
        db.session.commit()

        update_grade_student(student_id)

        #Mengarahkan ke halaman konfirmasi
        return render_template('confirmation-grade.html')
    else:
        student_list = []
        try: 
            #mengambil semua data karyawan dari db
            all_student = Students.query.all()

            #membuat daftar dari data karyawan 
            for student in all_student:
                student_data = {
                    'student_id': student.student_id,
                    'name': student.name,
                    'student_class': student.student_class,
                    'grade': student.grade,
                }
                print('masuk', student.name)
                student_list.append(student_data)
        except Exception as e:
            #mengembalikan pesan kesalahan 
            return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data siswa: {}".format(str(e))),500
        finally:
            if student_list:
                return render_template('createdata-grade.html', student_list=student_list)
            else:
                return render_template('error.html', pesan="Tidak ada data siswa yang dapat ditampilkan"),404 

#Koneksi API show all data
@app.route('/school/display_all_student', methods=['GET'])
@swag_from('swagger_docs/get_all_student.yaml')
def get_all_student():
    student_list = []
    try: 
        #mengambil semua data karyawan dari db
        all_student = Students.query.all()

        #membuat daftar dari data karyawan 
        for student in all_student:
            student_data = {
                'student_id': student.student_id,
                'name': student.name,
                'student_class': student.student_class,
                'grade': student.grade
            }
            student_list.append(student_data)

        if student_list.count==0:
            return render_template('error.html', pesan="Tidak ada data siswa yang dapat ditampilkan"),404 
        else:
            return Response(json.dumps(student_list),  mimetype='application/json')
    except Exception as e:
        #mengembalikan pesan kesalahan 
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data siswa: {}".format(str(e))),500

@app.route('/display_all_student', methods=['GET'])
def get_all_student_ui():
    student_list = []
    try: 
        #mengambil semua data karyawan dari db
        all_student = Students.query.all()

        #membuat daftar dari data karyawan 
        for student in all_student:
            student_data = {
                'student_id': student.student_id,
                'name': student.name,
                'student_class': student.student_class,
                'grade': student.grade
            }
            student_list.append(student_data)
    except Exception as e:
        #mengembalikan pesan kesalahan 
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data siswa: {}".format(str(e))),500
    finally:
        if student_list:
            return render_template('displayall.html', student_list=student_list)
        else:
            return render_template('error.html', pesan="Tidak ada data siswa yang dapat ditampilkan"),404 


#Koneksi API show all data
@app.route('/school/display_all_grade', methods=['GET'])
@swag_from('swagger_docs/get_all_grade.yaml')
def get_all_grade():
    grade_list = []
    try: 
        #mengambil semua data karyawan dari db
        all_grade = Grades.query.join(Students, Students.student_id==Grades.student_id).add_columns(Grades.grade_id,Grades.subject_name,Grades.score,Grades.date, Grades.student_id, Students.name ).all()

        #membuat daftar dari data karyawan 
        for grade in all_grade:
            grade_data = {
                'grade_id': grade.grade_id,
                'name': grade.name,
                'subject_name': grade.subject_name,
                'score': grade.score,
                'date': grade.date
            }
            grade_list.append(grade_data)

        if grade_list.count==0:
            return render_template('error.html', pesan="Tidak ada data siswa yang dapat ditampilkan"),404 
        else:
            return Response(json.dumps(grade_list),  mimetype='application/json')
    except Exception as e:
        #mengembalikan pesan kesalahan 
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data grade: {}".format(str(e))),500

#Koneksi API show all data
@app.route('/display_all_grade', methods=['GET'])
def get_all_grade_ui():
    grade_list = []
    try: 
        #mengambil semua data karyawan dari db
        all_grade = Grades.query.join(Students, Students.student_id==Grades.student_id).add_columns(Grades.grade_id,Grades.subject_name,Grades.score,Grades.date, Grades.student_id, Students.name ).all()

        #membuat daftar dari data karyawan 
        for grade in all_grade:
            grade_data = {
                'grade_id': grade.grade_id,
                'name': grade.name,
                'subject_name': grade.subject_name,
                'score': grade.score,
                'date': grade.date
            }
            grade_list.append(grade_data)

        if grade_list.count==0:
            return render_template('error.html', pesan="Tidak ada data siswa yang dapat ditampilkan"),404 
        else:
            return Response(json.dumps(grade_list),  mimetype='application/json')
    except Exception as e:
        #mengembalikan pesan kesalahan 
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data grade: {}".format(str(e))),500
    finally:
        if grade_list:
            return render_template('display-grade.html', grade_list=grade_list)
        else:
            return render_template('error.html', pesan="Tidak ada data siswa yang dapat ditampilkan"),404 


@app.route('/school/display_student/<int:student_id>', methods=['GET'])
@swag_from('swagger_docs/get_one_student.yaml')
def get_one_student(student_id):
    try: 
        student = Students.query.get(student_id)
        if not student:
            return jsonify({'message': 'Siswa tidak ditemukan'}),404

        return jsonify({'message': f'student_id: {student.student_id}, name: {student.name}, class: {student.student_class}, grade: {student.grade}'}),200
    except Exception as e:
        #mengembalikan pesan kesalahan 
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data siswa: {}".format(str(e))),500


#Koneksi API show all data
@app.route('/school/display_grade/<int:grade_id>', methods=['GET'])
@swag_from('swagger_docs/get_one_grade.yaml')
def get_one_grade(grade_id):
    try: 
        grades = Grades.query.get(grade_id)
        if not grades:
            return jsonify({'message': 'Grade tidak ditemukan'}),404
        
        return jsonify({'message': f'grade_id: {grades.grade_id}, student_id: {grades.student_id}, subject_name: {grades.subject_name}, score: {grades.score}, date: {grades.date}'}),200
    except Exception as e:
        #mengembalikan pesan kesalahan 
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data siswa: {}".format(str(e))),500


def get_one_grade_by_student_id(student_id):
    grade_list = []
    try: 
        #mengambil semua data karyawan dari db
        grade_list = Grades.query.join(Students, Students.student_id==Grades.student_id).add_columns(Grades.grade_id,Grades.subject_name,Grades.score,Grades.date, Grades.student_id, Students.name ).filter_by(student_id=student_id).all()
        return render_template('displayall.html',grade_list= grade_list)
    except Exception as e:
        #mengembalikan pesan kesalahan 
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data siswa: {}".format(str(e))),500
    finally:
        if grade_list:
            return render_template('displayall.html', grade_list=grade_list)
        else:
            return render_template('error.html', pesan="Tidak ada data siswa yang dapat ditampilkan"),404 


@app.route('/school/update_student/<int:student_id>', methods=['POST'])
@swag_from('swagger_docs/update_student.yaml')
def update_student(student_id):
    try:
        #mendapatkan data dari permintaan POST
        data = request.json

        student = Students.query.get(student_id)
        if not student:
            return jsonify({'message': 'Siswa tidak ditemukan'}),404
        
        #Membuat objek karyawan
        update = Students(
            name=data['name'],
            student_class=data['student_class'],
            grade=data['grade']
        )

        student.name = update.name
        student.student_class = update.student_class
        student.grade = update.grade

        db.session.commit()

        return jsonify({'message': f'student_id: {student.student_id}, name: {student.name}, class: {student.student_class}, grade: {student.grade}'}),200
    except Exception  as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}),500

@app.route('/update_student', methods=['POST'])
def update_student_ui():
    try:
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        student_class = request.form.get('student_class')
        grade = request.form.get('grade')

        student = Students.query.get(student_id)
        if not student:
            return jsonify({'message': 'Siswa tidak ditemukan'}),404
        
        student.name = name
        student.student_class = student_class
        student.grade = grade

        db.session.commit()

        return redirect(url_for('get_all_student'))
    except Exception  as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}),500


@app.route('/school/update_grade/<int:grade_id>', methods=['POST'])
@swag_from('swagger_docs/update_grade.yaml')
def update_grade(grade_id):
    try:
        student_id = request.form.get('student_id')
        grade_id = request.form.get('grade_id')
        subject_name = request.form.get('subject_name')
        score = request.form.get('score')
        grade = Grades.query.get(grade_id)
        if not grade:
            return jsonify({'message': 'Siswa tidak ditemukan'}),404
        
        grade.subject_name = subject_name  
        grade.score = score

        db.session.commit()

        update_grade_student(student_id)

        return redirect(url_for('get_one_grade_by_student_id',student_id=student_id))
    except Exception  as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}),500
    

def update_grade_student(student_id):
    grade_list = []
    try: 
        print("student_id ", student_id)

        #mengambil semua data karyawan dari db
        grade_list = Grades.query.join(Students, Students.student_id==Grades.student_id).add_columns(Grades.grade_id,Grades.subject_name,Grades.score,Grades.date, Grades.student_id, Students.name ).filter_by(student_id=student_id).all()
        print("grade_list ", grade_list)
        totalScore = 0
        totalSubject = 0

        for grade in grade_list:
            print("totalScore ", int(grade.score))
            totalScore += int(grade.score)
            totalSubject += 1   

        print("total score", totalScore)
        print("total subjec", totalSubject)
        avgScore = int(totalScore/totalSubject)
    except Exception as e:
        #mengembalikan pesan kesalahan 
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data siswa: {}".format(str(e))),500
    finally:
        if avgScore >= 90:
            grade = 'A'
        elif avgScore >=80 and avgScore < 90:
            grade = 'B'
        elif avgScore >=70 and avgScore < 80:
            grade = 'C'
        elif avgScore < 70:
            grade = 'D'

        student = Students.query.get(student_id)
        if not student:
            return jsonify({'message': 'Siswa tidak ditemukan'}),404

        student.grade = grade
        db.session.commit()

#Koneksi API Delete
@app.route('/school/student/<int:student_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_student.yaml')
def delete_student(student_id):
    try:
        student_to_delete = Students.query.filter_by(student_id=student_id).first()
        if student_to_delete:
            db.session.delete(student_to_delete)
            db.session.commit()

            delete_grade_by_student(student_id)

            return jsonify({'message':f'Data karyawan dengan id {student_id} berhasil dihapus'}),200
        else:
            return jsonify({'message':f'Data karyawan dengan id {student_id} tidak ditemukan'}),404
    except Exception as e:
        return jsonify({'message':f'Terjadi kesalahan: {e}'}),500

#Koneksi API Delete
@app.route('/school/grade/<int:grade_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_grade.yaml')
def delete_grade(grade_id):
    try:
        grade_to_delete = Grades.query.filter_by(grade_id=grade_id).first()
        if grade_to_delete:
            db.session.delete(grade_to_delete)
            db.session.commit()

            update_grade_student(grade_to_delete.student_id)

            return jsonify({'message':f'Data karyawan dengan id {grade_id} berhasil dihapus'}),200
        else:
            return jsonify({'message':f'Data karyawan dengan id {grade_id} tidak ditemukan'}),404
    except Exception as e:
        return jsonify({'message':f'Terjadi kesalahan: {e}'}),500
    
def delete_grade_by_student(student_id):
    try:
        grade_to_delete = Students.query.filter_by(student_id=student_id).first()
        if grade_to_delete:
            db.session.delete(grade_to_delete)
            db.session.commit()
            return jsonify({'message':f'Data karyawan dengan id {student_id} berhasil dihapus'}),200
        else:
            return jsonify({'message':f'Data karyawan dengan id {student_id} tidak ditemukan'}),404
    except Exception as e:
        return jsonify({'message':f'Terjadi kesalahan: {e}'}),500

    

if __name__ == '__main__':
    app.run(debug=True)
    

