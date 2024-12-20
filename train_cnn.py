import pandas as pd
import numpy as np
import os
import tensorflow as tf
import cv2
from tensorflow import keras
from tensorflow.keras.layers import Conv3D, MaxPooling3D, Flatten, Dense, Dropout, BatchNormalization, Input, GlobalMaxPooling3D, GlobalAveragePooling3D
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.utils import Sequence
from sklearn.model_selection import KFold, train_test_split
from tensorflow.keras import mixed_precision
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping, LearningRateScheduler
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt


policy = mixed_precision.Policy('mixed_float16')
mixed_precision.set_global_policy(policy)


gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    for gpu in gpus:
      tf.config.experimental.set_memory_growth(gpu, True)
  except RuntimeError as e:
    print(e)

IMG_WIDTH, IMG_HEIGHT, IMG_DEPTH = 200, 200, 200
defined_value=[
    0.000573,
    0.000562,
    0.0005795,
    0.0005276,
    0.000579,
    0.0006115,
    0.0005767,
    0.00056,
    0.000568,
    0.0005505,
    0.0005628,
    0.0005241,
    0.0005894,
    0.0005738,
    0.0005892,
    0.0005439,
    0.0005489,
    0.0005692,
    0.0005353,
    0.00054,
    0.0005572,
    0.0005592,
    0.0005725,
    0.0005376,
    0.0005438,
    0.0005517,
    0.00052,
    0.0005575,
    0.0005544,
    0.000546,
    0.0006317,
    0.0006108,
    0.000555,
    0.000603,
    0.0006311,
    0.0006313,
    0.0006106,
    0.0006388,
    0.000643,
    0.000652,
]

class DataGenerator(Sequence):
    def __init__(self, dir_list, defined_values, img_folder='Negated_Images_Amplified', batch_size=16, shuffle=True):
        self.img_folder = img_folder
        self.defined_values = defined_values
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.dir_list = dir_list
        self.indexes = np.arange(len(self.dir_list))

    def __len__(self):
        return len(self.dir_list) // self.batch_size

    def __getitem__(self, index):
        print('Length of dir_list:', len(self.dir_list))
        print('Batch size:', self.batch_size)
        indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]
        batch_dirs = [self.dir_list[k] for k in indexes]
        X, y = self.__data_generation(batch_dirs)
        return X, y

    def on_epoch_end(self):
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, batch_dirs):
        X = np.empty((self.batch_size, 200, 200, 200, 1))
        y = np.empty((self.batch_size, 1))
        for i, dir_name in enumerate(batch_dirs):
            dir_path = os.path.join(self.img_folder, dir_name)
            file_list = sorted([f for f in os.listdir(dir_path) if f.endswith('.png')])
            image_array = np.empty((200, 200, 200))
            for j, file_name in enumerate(file_list):
                image = cv2.imread(os.path.join(dir_path, file_name))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                image = cv2.resize(image, (200, 200), interpolation = cv2.INTER_AREA)
                image = np.array(image)
                image = image.astype('float32')
                image /= 255
                image_array[:, :, j] = image
            X[i,] = np.expand_dims(image_array, axis=3)
            y[i] = self.defined_values[int(dir_name[2:]) % 40]
        return X, y


    
def create_model():
    model = Sequential([
        # Input layer
        Conv3D(filters=8, kernel_size=(3, 3, 3), activation='relu', input_shape=(200, 200, 200, 1), kernel_regularizer=l2(0.01)),
        # Output: 200 * 200 * 200 * 8

        # Pooling
        MaxPooling3D(pool_size=(2, 2, 2)),
        # Output: 100 * 100 * 100 * 8

        # Convolution layer
        Conv3D(filters=16, kernel_size=(3, 3, 3), activation='relu', kernel_regularizer=l2(0.01)),
        # Output: 100 * 100 * 100 * 16

        # Pooling
        MaxPooling3D(pool_size=(4, 4, 4)),
        # Output: 25 * 25 * 25 * 16

        # Convolution layer
        Conv3D(filters=32, kernel_size=(3, 3, 3), activation='relu', kernel_regularizer=l2(0.01)),
        # Output: 25 * 25 * 25 * 32

        # Pooling
        MaxPooling3D(pool_size=(2, 2, 2)),
        # Output: 12 * 12 * 12 * 32

        # Convolution layer
        Conv3D(filters=64, kernel_size=(3, 3, 3), activation='relu', kernel_regularizer=l2(0.01)),
        # Output: 12 * 12 * 12 * 64

        # Convolution layer
        Conv3D(filters=128, kernel_size=(3, 3, 3), activation='relu', kernel_regularizer=l2(0.01)),
        # Output: 12 * 12 * 12 * 128

        # Global Max Pooling
        GlobalMaxPooling3D(),
        # Output: 128

        # Flatten
        Flatten(),
        # Output: 128

        # Dense layers
        Dense(units=128, activation='relu', kernel_regularizer=l2(0.01)),
        Dense(units=32, activation='relu', kernel_regularizer=l2(0.01)),
        Dense(units=1, activation='sigmoid', kernel_regularizer=l2(0.01))
    ])
    
    # Compile
    model.compile(optimizer=Adam(learning_rate=0.0001), loss='mean_squared_error')
    
    return model
# Learning rate scheduler
def scheduler(epoch, lr):
    if epoch < 10:
        return lr
    else:
        return lr * tf.math.exp(-0.1)

# Metrics Calculation
def calculate_metrics(y_true, y_pred):
    mse = np.mean((y_true - y_pred)**2)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return mse, mape

# 5-Fold Cross Validation
kf = KFold(n_splits=5, shuffle=True)

# Initialize the data generator
data_gen = DataGenerator(dir_list=[f for f in os.listdir('Negated_Images_Amplified') if os.path.isdir(os.path.join('Negated_Images_Amplified', f))], defined_values=defined_value, batch_size=16)

# Split the directories into training, validation, and test sets
train_val_dirs, test_dirs = train_test_split(data_gen.dir_list, test_size=0.2, random_state=42)


# Split the data into training and testing sets for the current fold
test_gen = DataGenerator(dir_list=test_dirs, defined_values=defined_value, batch_size=16)

    
# Create and compile the model
model = create_model()
model.summary()

#define callbacks
callbacks = [
    EarlyStopping(monitor='loss', patience=6),
    LearningRateScheduler(scheduler)
]


# Initialize lists to store metrics and predictions
mse_scores = []
mape_scores = []
accuracy_scores = []
predicted_values = []

# Iterate over the folds
for train_index, val_index in kf.split(train_val_dirs):
    # Split the data into training and validation sets for the current fold
    train_dirs = [train_val_dirs[i] for i in train_index]
    val_dirs = [train_val_dirs[i] for i in val_index]

    train_gen = DataGenerator(dir_list=train_dirs, defined_values=defined_value, batch_size=16)
    val_gen = DataGenerator(dir_list=val_dirs, defined_values=defined_value, batch_size=16)
    
    # Create and compile the model
    model = create_model()
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(train_gen, validation_data=val_gen, epochs=10, callbacks = callbacks)
    
    # Evaluate the model on the test set
    y_test = [defined_value[int(dir_name[2:]) % 40] for dir_name in test_gen.dir_list]
    y_pred = model.predict(test_gen)

    # Calculate metrics
    mse, mape = calculate_metrics(y_test, y_pred)
    mse_scores.append(mse)
    mape_scores.append(mape)

    # Calculate accuracy and store the scores
    accuracy = 100 - mape
    accuracy_scores.append(accuracy)

    predicted_values.extend(y_pred)

# Plotting the accuracy scores
plt.plot(accuracy_scores)
plt.xlabel('Fold')
plt.ylabel('Accuracy')
plt.title('Accuracy Scores per Fold')
plt.show()

# Save the weights of the model
model.save_weights('model_weights.h5')

# Print the average, minimum, maximum, and standard deviation of the predicted values
print("Average Predicted Value:", np.mean(predicted_values))
print("Minimum Predicted Value:", np.min(predicted_values))
print("Maximum Predicted Value:", np.max(predicted_values))
print("Standard Deviation of Predicted Values:", np.std(predicted_values))


# Write the results to a text file
with open('results.txt', 'w') as f:
    f.write("Average Predicted Value: " + str(np.mean(predicted_values)) + "\n")
    f.write("Minimum Predicted Value: " + str(np.min(predicted_values)) + "\n")
    f.write("Maximum Predicted Value: " + str(np.max(predicted_values)) + "\n")
    f.write("Standard Deviation of Predicted Values: " + str(np.std(predicted_values)) + "\n")

    f.write("\nMSE scores:\n")
    for score in mse_scores:
        f.write(str(score) + "\n")

    f.write("\nMAPE scores:\n")
    for score in mape_scores:
        f.write(str(score) + "\n")

    f.write("\nAccuracy scores:\n")
    for score in accuracy_scores:
        f.write(str(score) + "\n")
