import cv2
import face_recognition
import pickle
import os

# Get the account number as input from the user
account_number = input("Enter your account number: ")

# Define the path to the folder containing images for this account number
folderPath = os.path.join('Data', account_number)

# Check if the folder exists
if not os.path.exists(folderPath):
    print(f"No folder found for account number {account_number}")
    exit()

# Get the list of image files from the account-specific folder
pathList = os.listdir(folderPath)

imgList = []
PersonIds = []  # Image names will be stored as person IDs

# Import the person images into a list
for path in pathList:
    img = cv2.imread(os.path.join(folderPath, path))
    if img is not None:
        imgList.append(img)
        PersonIds.append(os.path.splitext(path)[0])
    else:
        print(f"Image not found or failed to load: {path}")

def findEncoding(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        except IndexError:
            print("No face found in one of the images, skipping that image.")
    return encodeList

print("Encoding Started...")
encodeListKnown = findEncoding(imgList)
encode_ListKnown_With_Ids = [encodeListKnown, PersonIds]
print("Encoding Completed")

# Define the path to save the encoded file with the account number as the filename
encodedFilePath = os.path.join('Data', account_number, f'{account_number}.p')

# Save these encodings into a file for future recognition
with open(encodedFilePath, 'wb') as file:
    pickle.dump(encode_ListKnown_With_Ids, file)
print(f"File saved as {encodedFilePath}")
