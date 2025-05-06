import cv2
import os
import pickle
import face_recognition
import numpy as np

def check_face(frame):


    account_number = input("Enter your account number: ")

    # Construct the path to the specific encoder file
    encoderFilePath = os.path.join('Data', account_number, f'{account_number}.p')

    # Check if the encoder file exists
    if not os.path.exists(encoderFilePath):
        print(f"No encoder file found for account number {account_number}")
        exit()

    # Load the image from the provided path
    img = frame
    if img is None:
        print(f"Image not found.")
        exit()

    # Resize and convert the image for processing
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Load the specific Encoding File for the account number
    print("Loading Encode File")
    with open(encoderFilePath, 'rb') as file:
        encode_ListKnown_With_Ids = pickle.load(file)

    encodeListKnown, PersonIds = encode_ListKnown_With_Ids
    print('Encodings Loaded')

    # Locate the face and find its encodings
    faceCurFrame = face_recognition.face_locations(imgS)
    if len(faceCurFrame) == 0:
        print("Face not visible")
    else:
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print("matches", matches)
            print("faceDis", faceDis)
            matchIndex = np.argmin(faceDis)

            # Check if the closest match is within an acceptable range
            if matches[matchIndex]:
                print("Known")
            else:
                print("Unknown")
