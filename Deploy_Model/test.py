from Deploy_Model.recognition import face_recognition
import cv2
import numpy as np
import os
from database import connect_DB
import cloudinary.uploader
import time
from datetime import datetime

########### la configuration du service cloud "cloudinary", ici, vous devez ajouter les informations de votre propre compte
cloudinary.config(
    cloud_name="Nom_Cloud",
    api_key="Cle_API",
    api_secret="Secret_Cle",
    secure=True
)
########### End de la configuration du service cloud "cloudinary"

db = connect_DB()
today = datetime.today()
today = today.strftime('%A')

#pour que le code programme, vous devez décommenter la ligne ci-dessous et commenter toutes les sections de lignes "données de test" qui servent uniquement comme un test.
# id_salle = db.get_salle_of_camera(ip_camera)


# ########################  données de test
today = "Monday"
id_salle = 16
########################  fin données de test

today, list_of_course = db.get_course_of_day(today, id_salle)
list_of_course = db.timedelta_to_normal_format(list_of_course)
print(today)
print(list_of_course)

# ########################  données de test
# today = "Monday"
list_of_course = ["16:15:00"]
########################  fin données de test

for heure in list_of_course:
    # while True:

    # pour que le programme fonctionne, vous devez décommenter la ligne ci-dessous et commenter toutes les sections de lignes "données de test" qui servent uniquement comme un test.
    # current_time = time.strftime("%H:%M:%S")


    # ########################  données de test
    current_time = "16:15:00"
    ########################  fin données de test

    if current_time > heure:
        print("pass to the next")
        pass

    if current_time == heure:

        # pour que le programme fonctionne, vous devez décommenter la ligne ci-dessous et commenter toutes les sections de lignes "données de test" qui servent uniquement comme un test.
        # la ligne ci-dessous c'est pour que le programme attend 30min (1800 secondes) après le début de la séance (pour que tous les étudiants soient présents)
        #time.sleep(1800)

        list_etd, grp, cren, matiere, dt = db.get_students(today, heure)

        ###### la ligne ci-dessous c'est pour le test avec une caméra de la machine, pour que le programme fonctionne proprement, vous devez commenter la ligne ci-dessous et décommenter la ligne d'après en mettant l'adresse ip de caméra
        # video_capture = cv2.VideoCapture(0)
        video_capture = cv2.VideoCapture("http://192.168.0.127:8080/video")

        # Check if the webcam is opened correctly
        if not video_capture.isOpened():
            raise IOError("Cannot open the webcam")

        #####
        images = []
        images_seance = []
        encodings = []
        known_face_encodings = []
        known_face_names = []
        dict_name_acc = {}
        # assign directory
        directory = 'faces'

        # iterate over files in
        # that directory
        cpt = 0
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            # checking if it is a file
            if os.path.isfile(f):
                images.append(face_recognition.load_image_file("faces/" + str(filename)))
                encodings.append(face_recognition.face_encodings(images[-1])[0])
                known_face_encodings.append(encodings[-1])
                known_face_names.append(str(filename[:-4]).replace("_", " "))
        #####

        present = []
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        # cette boucle est pour les 3 séquences vidéos qui doivent étre lancées chaque séance
        for i in range(3):
            print(f' séquence n° {i}')
            time_end = time.time() + 5
            time_to_capture = time_end - 1
            while time.time() < time_end:
                # Grab a single frame of video
                ret, frame = video_capture.read()
                temp_frame = frame

                frame_to_save = frame
                # frame = cv2.flip(frame, 1)
                if time_to_capture < time.time() < time_to_capture + 0.5:
                    if len(images_seance) < i + 1:
                        images_seance.append(frame_to_save)
                        # z = z + 1

                # ################## cette partie est pour le test avec la caméra de la machine, pour le bon fonctionnement, vous devez commenter et décommenter la partie qui suit.
                # # Resize frame of video to 1/4 size for faster face recognition processing
                # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                # # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                # rgb_small_frame = small_frame[:, :, ::-1]
                # ################## End caméra machine

                ################## pour le fonctionnement normal, vous devez décommenter cette partie
                ################## Camera serveur
                # frame = cv2.flip(frame, -1)
                # Resize frame of video to 1/4 size for faster face recognition processing
                # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                small_frame = cv2.resize(frame, (0, 0), fx=0.8, fy=0.8)
                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame
                ################## End Camera serveur

                # Only process every other frame of video to save time
                if process_this_frame:
                    # Find all the faces and face encodings in the current frame of video
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    face_names = []
                    for face_encoding in face_encodings:
                        # See if the face is a match for the known face(s)
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"

                        # Use the known face with the smallest distance to the new face
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                        face_names.append(name)

                        ### TEST accuracy
                        # finding the distance level between images
                        distance = round(face_distances[0] * 100)
                        accuracy = round(distance)
                        ###

                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]
                            print(f'name = {name}, acc = {accuracy}%')

                process_this_frame = not process_this_frame

                # Display the results
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size

                    # ################## cette partie est pour le test avec la caméra de la machine, pour le bon fonctionnement, vous devez commenter et décommenter la partie qui suit.
                    # top *= 4
                    # right *= 4
                    # bottom *= 4
                    # left *= 4
                    # ################## End caméra machine

                    ################## pour le fonctionnement normal, vous devez décommenter cette partie
                    ################## Camera serveur
                    top = int(1.25*top)
                    right = int(1.25*right)
                    bottom = int(1.25*bottom)
                    left = int(1.25*left)
                    ################## End Camera serveur

                    # Draw a box around the face
                    if name == "Unknown":
                        cv2.imwrite('./temporary/unknown.jpg', frame[top:bottom, left:right])
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)

                    else:
                        #### test adding every student's image and accuracy
                        if name in dict_name_acc.keys():
                            if accuracy > dict_name_acc[str(name)][1]:
                                cv2.imwrite('./temporary/' + str(name) + '.jpg', frame[top:bottom, left:right])
                                dict_name_acc[str(name)][0] = frame[top:bottom, left:right]
                                dict_name_acc[str(name)][1] = accuracy
                        else:
                            # t = [frame[top:bottom, left:right], accuracy]
                            dict_name_acc[str(name)] = [frame[top:bottom, left:right], accuracy]
                        ##### test end

                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                        if name not in present:
                            present.append(name)

                    # Draw a label with a name below the face
                    font = cv2.FONT_HERSHEY_DUPLEX
                    if name != "Unknown":
                        cv2.putText(frame, f"{name} {accuracy}%", (left + 6, bottom - 6), font, 1.0,
                                    (255, 255, 255), 1)
                    else:
                        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # Display the resulting image
                cv2.imshow('Video', frame)

                # Hit 'q' on the keyboard to quit!
                if cv2.waitKey(1) & 0xFF == ord('q'):

                    break

            time.sleep(3)

        video_capture.release()
        cv2.destroyAllWindows()

        ################ charger les images dans le cloud
        cv2.imwrite('./temporary/general.jpg', temp_frame)
        img_url = cloudinary.uploader.upload("./temporary/general.jpg")['url']
        for name in dict_name_acc.keys():
            t = cloudinary.uploader.upload('./temporary/' + str(name) + '.jpg')['url']
            dict_name_acc[str(name)][0] = t

        i = 0
        for img in images_seance:
            cv2.imwrite('./temporary/images_seance/' + str(i) + '.jpg', img)
            i = i + 1
        t = []
        time.sleep(5)
        directory = "./temporary/images_seance/"
        for img in os.listdir(directory):
            print(f' file = {img}')
            t.append(cloudinary.uploader.upload(directory + img)['url'])

        if len(t) < 3:
            for i in range(3 - len(t)):
                t.append(None)
        id_seance = db.create_seance(t)

        db.noter_absence(dict_name_acc, grp, cren, dt, id_seance)
        print(dict_name_acc)


        ###### supprimer les images enregistrées localement après la fin de la séance
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
