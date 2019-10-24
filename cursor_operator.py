import pyautogui
import cv2
import numpy as np
import face_processing as fp
from tensorflow import keras, device


#pyautogui.moveTo(100,150)
x,y = pyautogui.position()

print("pos: ", x, ' ', y)


####################


raw_data = np.load("capresults.npy", allow_pickle=True)

# del datapoints with empty vectors
mask = np.ones(len(raw_data), dtype=bool)
data = np.zeros((len(raw_data), 13), dtype='O')

for i, dp in enumerate(raw_data):
    if (dp[3].size is 0 or dp[5].size is 0):
        mask[i] = False
    
    #flattened = np.concatenate([[*dp[0], dp[1][0] / 1920, dp[1][1] / 1080, dp[2][0] / 1920, dp[2][1] / 1080,], dp[3], [dp[4] / 2073600], dp[5]], axis=0).astype('float32')
    flattened = np.concatenate([[*dp[0], *dp[1], *dp[2]], dp[3], [dp[4]], dp[5]], axis=0).astype('float32')
    if flattened.shape[0] is data.shape[1]:
        data[i] = flattened
del raw_data

data = data[mask, ...]

# split into training and testing sets
mask = np.random.choice([True, False], len(data), p=[0.75, 0.25])

training_data = data[mask, ...][:, 2:]
training_labels = data[mask, ...][:, :2]

mask = ~mask

testing_data = data[mask, ...][:, 2:]
testing_labels = data[mask, ...][:, :2]

del data

model = keras.Sequential()
model.add(keras.Input(shape=(11,), name='data'))
model.add(keras.layers.Dense(128, activation='relu'))
model.add(keras.layers.Dense(16, activation='relu'))
model.add(keras.layers.Dense(64, activation='relu'))
model.add(keras.layers.Dense(16, activation='relu'))
model.add(keras.layers.Dense(64, activation='relu'))
model.add(keras.layers.Dense(16, activation='relu'))
model.add(keras.layers.Dense(64, activation='relu'))


model.add(keras.layers.Dense(2, activation='linear', name='output'))

model.compile(optimizer='adam', loss='mean_squared_error', 
            metrics=['mean_squared_error'])

model.fit(training_data, training_labels, epochs=40)

test_loss, test_mse = model.evaluate(testing_data, testing_labels, verbose=0)
print("\nTest MSE:", test_mse)

##############################################################################################



video = cv2.VideoCapture(0)

#cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

face_avg = fp.PropertyAverager(10)



while video.isOpened():
    ret, frame = video.read()
    if not ret:
        break

    faces = fp.process(frame)

    if len(faces) is 1:
        face_avg.add(faces[0].gaze)
        face_avg.draw(frame, faces[0])
    else:
        face_avg.invalidate()

    for face in faces:
        face.draw_bbox(frame)
        face.draw_pts(frame)

    cv2.imshow('frame', frame)

    lmid_x, lmid_y = face.l_mid
    rmid_x, rmid_y = face.r_mid
    gaz_x, gaz_y, gaz_z = face.gaze
    pos_x, pos_y, pos_z = face.h_pose
    fac_siz = float(face.size)

   


    data = np.array([[float(lmid_x), float(lmid_y), float(rmid_x), float(rmid_y), float(gaz_x), float(gaz_y), float(gaz_z), fac_siz, float(pos_x), float(pos_y), float(pos_z)]])

    #print(type(data), data.shape, data)
    #mask = np.ones(1, dtype = bool)
    #print(type(td), td.shape, td)
    tab = model.predict(data)
    #print(type(tab), tab.shape, tab)

    gx = tab[0,0]
    gy = tab[0,1]

   # if gx > 1:
   #     gx = 1
   # elif gx < 0:
   #     gx = 0
   # elif gy > 1:
   #     gy = 1
   # elif gy < 0:
   #     gy = 0
    print('x = ', gx, '| y = ', gy)
    
    if(gx < 1 and gx > 0 and gy < 1 and gy > 0):
        pyautogui.moveTo(1920*gx,1080*gy)
    
        
    

    
    

    




    key = cv2.waitKey(1)
    if key == ord(' '):
        video.release()
        break
   

video.release()
cv2.waitKey(0)