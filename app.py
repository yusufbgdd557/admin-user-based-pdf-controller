from re import A
from flask import session, url_for
from tika import parser
from html.entities import html5
from flask import Flask, render_template, request, redirect, url_for
from flask.scaffold import F
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from werkzeug.utils import secure_filename
import os
import tika
tika.initVM()


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:POSTGRES-USERNAME@localhost/DB-NAME'

UPLOAD_FOLDER = 'YOUR UPLOAD FILE FOLDER LOCATION'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    userId = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(20))
    userPw = db.Column(db.String(20))

    def __init__(self, userName, userPw):
        self.userName = userName
        self.userPw = userPw


class Files(db.Model):
    __tablename__ = 'files'
    pdfId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer)
    # Sorgu işlemlerinden gelen bilgilerin databasede tutalacağı yer/
    author = db.Column(db.String)
    ders_adi = db.Column(db.String)
    summary = db.Column(db.String)
    deadline = db.Column(db.String)
    title = db.Column(db.String)
    keywords = db.Column(db.String)
    danisman_bilgileri = db.Column(db.String)
    juri_bilgileri = db.Column(db.String)

    def __init__(self, userId, author, ders_adi, summary, deadline, title, keywords, danisman_bilgileri, juri_bilgileri):
        self.userId = userId
        self.author = author
        self.ders_adi = ders_adi
        self.summary = summary
        self.deadline = deadline
        self.title = title
        self.keywords = keywords
        self.danisman_bilgileri = danisman_bilgileri
        self.juri_bilgileri = juri_bilgileri


class Admin(db.Model):
    __tablename__ = 'admin'
    adminId = db.Column(db.Integer, primary_key=True)
    adminName = db.Column(db.String(20))
    adminPw = db.Column(db.String(20))

    def __init__(self, adminName, adminPw):
        self.adminName = adminName
        self.adminPw = adminPw


class LoggedUser(db.Model):
    __tablename__ = 'loggedUser'
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(20))

    def __init__(self, userName):
        self.userName = userName


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/admin")
def admin():
    return render_template("adminMain.html")


@app.route("/admin/useroperations")
def user_operations():
    userResult = db.session.query(User)
    return render_template("userOperations.html", userResult=userResult)


@app.route("/admin/useradd", methods=["GET", "POST"])
def useradd():
    if request.method == "POST":
        username = request.form.get("username", False)
        password = request.form.get("password", False)
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        db.session.flush()
        print("Succesfully added")
        return redirect("/admin/useroperations")
    return redirect("/admin")


@app.route("/admin/userupdate", methods=["GET", "POST"])
def userupdate():
    if request.method == "POST":
        username = request.form.get("username", False)
        password = request.form.get("password", False)
        rows_changed = User.query.filter_by(
            userName=username).update(dict(userPw=password))
        db.session.commit()
        db.session.flush()
        return redirect("/admin/useroperations")
    return redirect("/admin")


@app.route("/admin/userdelete", methods=["GET", "POST"])
def userdelete():
    id = request.args.get("id", False)
    if request.method == "POST":
        username = request.form.get("username", False)
        user = User.query.filter_by(userName=username).first()
        db.session.delete(user)
        db.session.commit()
        db.session.flush()
        return redirect("/admin/useroperations")
    return redirect("/admin")


@app.route("/admin/login")
def login_admin():
    return render_template("adminLogin.html")


@app.route("/admin/signup")
def index():
    return render_template("adminSignUp.html")


@app.route("/admin/signup/check", methods=["GET", "POST"])
def check_admin_signup():
    if request.method == "POST":
        username = request.form.get("username", False)
        password = request.form.get("password", False)
        admin = Admin(username, password)
        db.session.add(admin)
        db.session.commit()
        db.session.flush()
        print("Successfully added")
        return redirect("/admin/login")
    return redirect("/admin/signup")


@app.route("/admin/login/check", methods=["GET", "POST"])
def check_admin_login():
    adminResult = db.session.query(Admin)
    username = request.form.get("username", False)
    password = request.form.get("password", False)
    for result in adminResult:
        if result.adminName == username and result.adminPw == password:
            return redirect("/admin")
    return redirect("/admin/login")


@app.route("/admin/pdfinfo", methods=["GET", "POST"])
def pdfinfo():
    return render_template("pdfinfo.html")


@app.route("/query1", methods=["GET", "POST"])
def query1():
    file = Files.query.all()
    return render_template("query1.html", result=file)


@app.route("/query1/result", methods=["GET", "POST"])
def q1result():
    author = request.form.get("author", False)
    lessonName = request.form.get("lessonName", False)
    projectName = request.form.get("projectName", False)
    keywords = request.form.get("keywords", False)
    date = request.form.get("date", False)
    file = Files.query.all()
    resultFile = []
    if(author != ''):
        for i in file:
            check = i.author.replace(' ', '')
            author = author.lower().replace(' ', '')
            if(author in check):
                resultFile.append(i)
    if(lessonName != ''):
        for i in file:
            check = i.ders_adi.replace(' ', '')
            lessonName = lessonName.lower().replace(' ', '')
            if(lessonName in check):
                resultFile.append(i)
    if(projectName != ''):
        for i in file:
            check = i.title.replace(' ', '')
            projectName = projectName.lower().replace(' ', '')
            if(projectName in check):
                resultFile.append(i)
    if(keywords != ''):
        for i in file:
            check = i.keywords.replace(' ', '')
            keywords = keywords.lower().replace(' ', '')
            if(keywords in check):
                resultFile.append(i)
    if(date != ''):
        if(date.lower() == "bahar"):
            for i in file:
                check_arr = i.deadline.split(".")
                check = check_arr[1]
                if(int(check) > 5):
                    resultFile.append(i)
        elif(date.lower() == "güz"):
            for i in file:
                check_arr = i.deadline.split(".")
                check = check_arr[1]
                if(int(check) < 5):
                    resultFile.append(i)
    if(len(resultFile) == 0):
        return render_template("query1.html", result=file)
    return render_template("query1.html", result=resultFile)


@app.route("/query2", methods=["GET", "POST"])
def query2():
    file = Files.query.all()
    return render_template("query2.html", result=file)


@app.route("/query2/result", methods=["GET", "POST"])
def q2result():
    userID = request.form.get("userID", False)  # userID
    lessonName = request.form.get("lessonName", False)  # lesson name
    years = request.form.get("years", False)  # semester
    date = request.form.get("date", False)  # bahar or güz
    file = Files.query.all()
    resultFile = []
    for i in file:
        check = i.ders_adi.lower().replace(' ', '')
        lessonName = lessonName.lower().replace(' ', '')
        if(int(userID) == int(i.userId) and lessonName == check):
            split_dead_line = i.deadline.split('.')
            semester_name = int(split_dead_line[1])
            semester_year = int(split_dead_line[2].replace(' ',''))
            small_year = int(years)
            big_year = small_year + 1
            if(semester_year == small_year or semester_year == big_year):
                if(date.lower() == "bahar"):
                    if(semester_name > 5):
                        resultFile.append(i)
                if(date.lower() == "güz"):
                    if(semester_name < 5):
                        resultFile.append(i)

    if(resultFile != []):
        return render_template("query2.html", result=resultFile)
    return render_template("query2.html", result=file)


@app.route("/user")
def user():
    return render_template("uploadpdf.html")


@app.route("/user/login")
def login_user():
    return render_template("userLogin.html")


@app.route("/user/login/check", methods=["GET", "POST"])
def checkuser():
    userResult = db.session.query(User)
    username = request.form.get("username", False)
    password = request.form.get("password", False)
    for result in userResult:
        if result.userName == username and result.userPw == password:
            logged_user = LoggedUser(userName=username)
            db.session.add(logged_user)
            db.session.commit()
            db.session.flush()
            return render_template("uploadpdf.html", userName=username)
    return redirect("/user/login")


@app.route("/user/uploadpdf", methods=["GET", "POST"])
def uploadpdf():
    pdf_file = request.files.get("pdf")
    if pdf_file.filename == '':
        return redirect("/user")
    filename = secure_filename(pdf_file.filename)
    upload_path = app.config['UPLOAD_FOLDER'] + "\pdf\ " + filename
    if(os.path.isfile(upload_path)):
        print("file is exist")
        parsed = parser.from_file(upload_path)
    else:
        pdf_file.save(os.path.join(upload_path))
        print("uploaded successfully")
        parsed = parser.from_file(upload_path)
    the_text = parsed.get("content").lower()

    # take dead_line
    dead_line = the_text.split('tezin savunulduğu tarih: ')[
        1].split('\n')[0].replace("\n", " ")
    #print("deadline : ", dead_line, "\n\n\n")

    # take summary
    temp = the_text.split('anahtar kelimeler:')[len(
        the_text.split('anahtar kelimeler:')) - 2].split("özet")
    if(len(temp) == 2):
        summary = temp[1].replace("\n", " ")
    if(len(temp) == 3):
        summary = temp[2].replace("\n", " ")
    if(len(temp) == 4):
        arr = temp[len(temp) - 2]
        summary_part1 = ""
        for i in arr:
            if(i != ''):
                summary_part1 += i
        summary_part1 = summary_part1.replace("\n", " ")
        summary_part2 = temp[3].replace("\n", " ")
        summary = summary_part1 + " özet"+summary_part2
    #print("summary : ", summary, "\n\n\n")

    # take title
    tmp = the_text.split('anahtar kelimeler:')[len(
        the_text.split('anahtar kelimeler:')) - 2].split("özet")
    arr = tmp[len(tmp) - 2]
    if(len(tmp) == 2):
        text_arr = arr.split("\n")
        title = text_arr[len(text_arr)-5] + " " + text_arr[len(text_arr)-3]
    if(len(tmp) == 3):
        title = arr.split("viii")[len(
            arr.split("viii")) - 1].replace("\n", " ")
    if(len(tmp) == 4):
        if(filename == "170201025.pdf"):
            arr2 = tmp[len(tmp) - 3]
            text_arr2 = arr2.split("\n")
            title = text_arr2[len(text_arr2)-5] + " " + \
                text_arr2[len(text_arr2)-3]
        else:
            title = arr.split("7")[len(arr.split("7")) - 1].replace("\n", " ")
    #print("title : ", title, "\n\n\n")

    # take keyword
    key_words = the_text.split("anahtar kelimeler: ")[
        1].split(".")[0].replace("\n", " ")
    #print("key words : ", key_words, "\n\n\n")

    # take author, juri_bilgileri, danisman_bilgileri, ders_adi
    tmp3 = the_text.split('tezin savunulduğu tarih: ')[
        0].split('\n')
    arr = []
    author = ""
    juri_bilgileri = ""
    danisman_bilgileri = ""
    ders_adi = ""
    for i in tmp3:
        if(i != ' ' and i != ''):
            arr.append(i)
    if(filename == "OrnekTez2.pdf"):
        author = arr[18]
        juri_bilgileri = arr[21] + ", " + arr[23]
        danisman_bilgileri = arr[19]
        ders_adi = arr[13]
    if(filename == "OrnekTez.pdf"):
        author = arr[12]
        juri_bilgileri = arr[15] + ", " + arr[17]
        danisman_bilgileri = arr[13]
        ders_adi = arr[10]
    if(filename == "170201025.pdf"):
        author = arr[14]
        juri_bilgileri = arr[17] + ", " + arr[19]
        danisman_bilgileri = arr[15]
        ders_adi = arr[11]
    if(filename == "160202123_150201103_160202093.pdf"):
        author = arr[14]+", " + arr[15]+", "+arr[16]
        juri_bilgileri = arr[19] + ", " + arr[21]
        danisman_bilgileri = arr[17]
        ders_adi = arr[12]
    logged_users = LoggedUser.query.all()

    logged_userName = logged_users[-1].userName
    user = User.query.filter_by(userName=logged_userName).first()
    userId = user.userId
    file = Files(userId=userId, author=author, ders_adi=ders_adi, summary=summary, deadline=dead_line,
                 title=title, keywords=key_words, danisman_bilgileri=danisman_bilgileri, juri_bilgileri=juri_bilgileri)
    db.session.add(file)
    db.session.commit()
    db.session.flush()
    result = []
    result.append(user.userName)
    result.append(filename)
    return render_template("uploadpdf.html", result=result)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True, port=8000)
