from flask import Flask, render_template, request

import cv2
from database import connect_DB

app = Flask(__name__)
camera = cv2.VideoCapture(1)
db = connect_DB()


def generate_frames():
    while True:
        ## read the camera frame
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    cours = db.get_cours()
    dic_grps, gr = db.get_group()
    return render_template('index.html', value=[dic_grps, cours])


@app.route('/result', methods=['GET', 'POST'])
def liste_presence():
    if request.method == 'POST':
        date = request.form.get('date')
        cours = request.form.get('cours')
        grp = request.form.get('grp')
    grp, dic_pres, images_seance = db.get_attendance_of_session_by_date_and_cours(date, cours, grp)

    if dic_pres != {}:
        return render_template('list.html', value=[grp, dic_pres, date, cours, images_seance])
    else:
        cours = db.get_cours()
        dic_grps, gr = db.get_group()
        no_cours = "Aucune séance n'est disponible pour les informations selectionnées"
        return render_template('index.html', value=[dic_grps, cours, no_cours])


# @app.route('/valider_presence/<int:id>', methods=['GET', 'POST'])
@app.route('/valider_presence/<int:id>/<string:grp>/<string:cours>/<string:date>')
def valider_presence(id, grp, cours, date):
    print("test1")
    db.valide_presence(id)
    grp, dic_pres, images_seance = db.get_attendance_of_session_by_date_and_cours(date, cours, grp)
    return render_template('list.html', value=[grp, dic_pres, date, cours, images_seance])


@app.route('/valider_absence/<int:id>/<string:grp>/<string:cours>/<string:date>')
def valider_absence(id, grp, cours, date):
    print("test2")
    db.valide_absence(id)
    grp, dic_pres, images_seance = db.get_attendance_of_session_by_date_and_cours(date, cours, grp)
    return render_template('list.html', value=[grp, dic_pres, date, cours, images_seance])


def accueil():
    cours = db.get_cours()
    dic_grps, gr = db.get_group()
    return render_template('index.html', value=[dic_grps, cours])


if __name__ == "__main__":
    app.run(debug=True)
