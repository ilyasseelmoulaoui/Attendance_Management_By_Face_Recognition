import mysql.connector
from datetime import datetime
import cv2

class connect_DB:
    def __init__(self):
        self.connection = None
        self.jours = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.cursor = None
        # self.cursor = self.connection.cursor()

    def get_salle_of_camera(self, ip_camera):

        id_salle = ""
        try:
            #
            # cursor = self.connection.cursor()
            self.connection = mysql.connector.connect(host='localhost', database='absence', user='root', password='')
            self.cursor = self.connection.cursor()
            sql_select_Query = "select id_salle from salle s where s.ip_camera=%s"
            tuple = (ip_camera,)
            # cursor = connection.cursor()
            self.cursor.execute(sql_select_Query, tuple)
            records = self.cursor.fetchall()
            # print(f'records_time = {records[0]}')
            for row in records:
                id_salle = row[0]
            return id_salle

        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)

    def get_date(self):
        # get current datetime (GMT)
        dt = datetime.now()

        # get day of week as an integer (monday is 0)
        jour = dt.weekday()
        # get day of week
        x = self.jours[jour]

        # get (GMT) time of day hh:mm:ss
        heure = dt.time()

        dt = str(dt)[:10]

        return jour, heure, dt

    def get_course_of_day(self,today, id_salle):

        list_debut_seance=[]
        try:
            #
            # cursor = self.connection.cursor()
            self.connection = mysql.connector.connect(host='localhost', database='absence', user='root', password='')
            self.cursor = self.connection.cursor()
            sql_select_Query = "select debut from creneau c where c.jour=%s and c.id_salle=%s"
            tuple = (today, id_salle)
            # cursor = connection.cursor()
            self.cursor.execute(sql_select_Query, tuple)
            records = self.cursor.fetchall()
            # print(f'records_time = {records[0]}')
            for row in records:
                list_debut_seance.append(row[0])
            return today, list_debut_seance

        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)


    def get_students(self, jour, heure):
        list_etd = []
        grp = ''
        cren = ''
        matiere = ''
        j, h, dt = self.get_date()

        #### TEST
        # jour = "jeudi"
        # heure = "10:10:00"
        #####
        try:
            #
            # cursor = self.connection.cursor()
            self.connection = mysql.connector.connect(host='localhost', database='absence', user='root', password='')
            self.cursor = self.connection.cursor()
            sql_select_Query = "select id_creneau, id_groupe, matiere from creneau c where c.jour=%s and c.debut<=%s and c.fin>=%s"
            tuple = (jour, heure, heure)
            # cursor = connection.cursor()
            self.cursor.execute(sql_select_Query, tuple)
            records = self.cursor.fetchall()

            for row in records:
                cren = row[0]
                grp = row[1]
                matiere = row[2]

            sql_select_Query = "select nom_complet from etudiant e where e.id_groupe=%s"

            tuple1 = (grp,)
            # cursor = connection.cursor()
            self.cursor.execute(sql_select_Query, tuple1)
            records = self.cursor.fetchall()

            for row in records:
                list_etd.append(row[0])

        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)
        # finally:
        #     if self.connection.is_connected():
        #         self.connection.close()
        #         cursor.close()
        #         print("\nMySQL connection is closed")

        return list_etd, grp, cren, matiere, dt

    def noter_absence(self, list_pres, grp, cren, dt, id_seance):
        id_etds = []
        id_pres = []
        id_abs = []
        try:
            self.connection = mysql.connector.connect(host='localhost', database='absence', user='root', password='')
            self.cursor = self.connection.cursor()
            # cursor = self.connection.cursor()
            # id tous les etudiants du groupe
            sql_select_Query = "select id_etudiant from etudiant e where e.id_groupe=%s"
            tuple = (grp,)
            # cursor = connection.cursor()
            self.cursor.execute(sql_select_Query, tuple)
            records = self.cursor.fetchall()

            for row in records:
                id_etds.append(row[0])

            # id etudiants presents
            for etd in list_pres:
                sql_select_Query = "select id_etudiant from etudiant e where e.nom_complet=%s and e.id_groupe=%s"
                tuple = (etd, grp)
                # cursor = connection.cursor()
                self.cursor.execute(sql_select_Query, tuple)
                records = self.cursor.fetchall()
                for row in records:
                    #id_pres.append(row[0])
                    list_pres[etd].append(row[0])

            pres_id = []

            for name in list_pres.keys():
                pres_id.append(list_pres[name][2])

            # id etudiants absents
            id_abs = self.trouverAbsents(id_etds, pres_id)

            # noter la presence
            sql_select_Query = "insert into attendance (present,id_creneau, id_etudiant, date_seance, taux_validation, image, id_seance) values (1, %s, %s, %s, %s, %s, %s)"
            for name in list_pres.keys():
                tuple = (cren, list_pres[name][2], dt, list_pres[name][1], list_pres[name][0], id_seance)
                # cursor = connection.cursor()
                self.cursor.execute(sql_select_Query, tuple)

            # noter l'absence
            sql_select_Query = "insert into attendance (present, id_creneau, id_etudiant, date_seance, id_seance) values (0, %s, %s, %s, %s)"
            for id_etd in id_abs:
                tuple = (cren, id_etd, dt, id_seance)
                # cursor = connection.cursor()
                self.cursor.execute(sql_select_Query, tuple)

            # maybe after each insertion
            self.connection.commit()

            print(self.cursor.rowcount, "record inserted.")

        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)
        # finally:
        #     if self.connection.is_connected():
        #         self.connection.close()
        #         self.cursor.close()
        #         print("\nMySQL connection is closed")

    def trouverAbsents(self, list_etd, list_pres):
        n = len(list_etd)
        m = len(list_pres)
        abs = []
        for i in range(n):
            for j in range(m):
                if list_etd[i] == list_pres[j]:
                    break
                if j == m - 1:
                    abs.append(list_etd[i])
        return abs

    def get_attendance_of_session_by_date_and_cours(self, date, cours, id_groupe):

        # id_groupe = 0
        id_creneau = 0
        dic_etds = {}
        groupe_name = ''
        images_seance = []
        # get course id

        try:
            self.connection = mysql.connector.connect(host='localhost', database='absence', user='root', password='')
            self.cursor = self.connection.cursor()
            # cursor = self.connection.cursor()
            # id tous les etudiants du groupe
            sql_select_Query = "select id_creneau from creneau c where c.matiere=%s"
            tuple = (cours,)

            # cursor = connection.cursor()
            self.cursor.execute(sql_select_Query, tuple)
            records = self.cursor.fetchall()

            for row in records:
                id_creneau = row[0]

            # get student infos of session
            sql_select_Query = "select id_etudiant, present, taux_validation, image, id_attendance, id_seance from attendance a where a.id_creneau=%s and date_seance=%s"
            tuple = (id_creneau, date)
            self.cursor.execute(sql_select_Query, tuple)
            records = self.cursor.fetchall()

            if records == []:
                return '',{},[]
            for row in records:
                v = [row[1], row[2], row[3], row[4]]
                dic_etds[row[0]] = v
                id_seance = row[5]

            # get student infos of session
            for etudiant in dic_etds.keys():
                sql_select_Query = "select matricule, nom_complet, id_groupe from etudiant e where e.id_etudiant=%s"
                tuple = (etudiant,)
                self.cursor.execute(sql_select_Query, tuple)
                records = self.cursor.fetchall()
                for row in records:
                    id_groupe = row[2]
                    v = [row[0], row[1]]
                    dic_etds[etudiant].append(v)

            # get groupe name by groupeId
            sql_select_Query = "select nom_groupe from groupe g where g.id_groupe=%s"
            tuple = (id_groupe,)
            self.cursor.execute(sql_select_Query, tuple)
            records = self.cursor.fetchall()
            for row in records:
                groupe_name = row[0]

            sql_select_Query = "select image1, image2, image3 from seance c where c.id_seance=%s"
            tuple = (id_seance,)
            self.cursor.execute(sql_select_Query, tuple)
            records = self.cursor.fetchall()
            for row in records:
                images_seance = [row[0], row[1], row[2]]


        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)
        # finally:
        #     if self.connection.is_connected():
        #         self.connection.close()
        #         self.cursor.close()
        #         print("\nMySQL connection is closed")

        return groupe_name, dic_etds, images_seance

    def get_group(self):

        dic_grp = {}
        gr = []
        try:
            self.connection = mysql.connector.connect(host='localhost', database='absence', user='root', password='')
            self.cursor = self.connection.cursor()
            sql_select_Query = "select id_groupe, nom_groupe from groupe g where g.id_groupe>%s"
            # cursor = connection.cursor()
            tuple = (0,)
            self.cursor.execute(sql_select_Query, tuple)
            records = self.cursor.fetchall()
            for row in records:
                dic_grp[row[0]] = row[1]
                gr.append(row[1])

        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)
        # finally:
        #     if self.connection.is_connected():
        #         self.connection.close()
        #         cursor.close()
        #         print("\nMySQL connection is closed")

        return dic_grp, gr

    def get_cours(self):
        cours = []
        try:
            self.connection = mysql.connector.connect(host='localhost', database='absence', user='root', password='')
            self.cursor = self.connection.cursor()
            sql_select_Query = "select distinct matiere from creneau c"
            # cursor = connection.cursor()
            self.cursor.execute(sql_select_Query)
            records = self.cursor.fetchall()
            for row in records:
                cours.append(row[0])

        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)
        # finally:
        #     if self.connection.is_connected():
        #         self.connection.close()
        #         cursor.close()
        #         print("\nMySQL connection is closed")

        return cours

    def valide_presence(self, id):
        try:
            self.connection = mysql.connector.connect(host='localhost', database='absence', user='root', password='')
            self.cursor = self.connection.cursor()
            # noter la presence
            sql_select_Query = "update attendance set present=1 where id_attendance=%s"
            tuple = (id,)
            self.cursor.execute(sql_select_Query, tuple)
            self.connection.commit()
        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)

    def valide_absence(self, id):
        try:
            self.connection = mysql.connector.connect(host='localhost', database='absence', user='root', password='')
            self.cursor = self.connection.cursor()
            # noter la presence
            sql_select_Query = "update attendance set present=0, taux_validation=null, image=null where id_attendance=%s"
            tuple = (id,)
            self.cursor.execute(sql_select_Query, tuple)
            self.connection.commit()
        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)


    def create_seance(self,images):
        try:
            self.connection = mysql.connector.connect(host='localhost', database='absence', user='root', password='')
            self.cursor = self.connection.cursor()
            # noter la presence
            sql_select_Query = "insert into seance (image1,image2,image3) values (%s,%s,%s)"
            tuple = (images[0], images[1], images[2],)
            self.cursor.execute(sql_select_Query, tuple)
            self.connection.commit()
            record_id = self.cursor.lastrowid
            return record_id
        except mysql.connector.Error as e:
            print("Error reading data from MySQL table", e)


    def timedelta_to_normal_format(self,list_time):
        list = []
        for td in list_time:
            total_seconds = td.total_seconds()

            # Calculate the number of hours, minutes, and seconds from the total number of seconds
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Format the timedelta object as a string in the HH:MM:SS format
            td_str = '{:02d}:{:02d}:{:02d}'.format(int(hours), int(minutes), int(seconds))

            list.append(td_str)
        return list
