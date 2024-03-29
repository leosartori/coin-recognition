#######################################################################

# Coin Detector and Recognizer - Exam of Computer Vision 2018/2019 UNIPD

# @author Leonardo Sartori (leonardo.sartori.1@studenti.unipp.it)
# @version 1.0

#######################################################################

import datetime
import os

from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense, GlobalAveragePooling2D
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from keras.optimizers import SGD, rmsprop

from keras.models import Model

from keras.applications.inception_v3 import InceptionV3
from keras.applications.inception_v3 import preprocess_input

INPUT_SIZE = 224
BATCH_SIZE = 32
USE_VAL = True

TRAIN_PATH = 'images/coins-dataset/classified/train'
VAL_PATH = 'images/coins-dataset/classified/test'

# SMALL DEBUG TRAINSET
# TRAIN_PATH = '/home/leonardo/Documents/computer_vision/project/images/small_train'


# HERE THERE IS A SERIES OF MODEL TESTED, BEST IS cifar (keras.io/examples/cifar10_cnn/)
# BUT ANYWAY FAR FROM TRANSFER LEARNING RESULTS

def create_model(l_num):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), input_shape=(INPUT_SIZE, INPUT_SIZE,3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors
    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(l_num))
    model.add(Activation('softmax'))

    return model

def create_model_doc(l_num):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(3, INPUT_SIZE, INPUT_SIZE)))
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(l_num, activation='softmax'))
    return model

def create_model_cifar(l_num):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding='same', input_shape=(3, INPUT_SIZE, INPUT_SIZE)))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(l_num))
    model.add(Activation('softmax'))
    return model

def create_model_zi(l_num):

    model = Sequential()

    model.add(Conv2D(64, (5, 5), padding='same', input_shape=(3, INPUT_SIZE, INPUT_SIZE)))
    model.add(Activation('relu'))

    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(128, (5, 5), padding='same'))
    model.add(Activation('relu'))

    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(256, (3, 3), padding='same'))
    model.add(Activation('relu'))

    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(512, (3, 3), padding='same'))
    model.add(Activation('relu'))

    model.add(Flatten())
    model.add(Dense(1024))
    model.add(Activation('relu'))

    model.add(Dense(l_num))
    model.add(Activation('softmax'))

    return model

if __name__ == '__main__':

    labels_num = sum(os.path.isdir(os.path.join(TRAIN_PATH,i)) for i in os.listdir(TRAIN_PATH))
    print ("labels_num: " + str(labels_num))

    # alternative to rms
    #sgd = SGD(lr=0.0001, decay=1e-6, momentum=0.9, nesterov=True)
    rms = rmsprop(lr=0.0001, decay=1e-6)

    # ------------------ TRANSFER LEARNING ------------------

    # BEST MODEL TESTED IS InceptionV3, very complex and big but we don't have time constraints so I'll use it
    base_model=InceptionV3(weights='imagenet',include_top=False) #imports the Inception model and discards the last 1000 neuron layer.

    x=base_model.output

    #we add dense layers so that the model can learn more complex functions and classify for better results.
    x=GlobalAveragePooling2D()(x)
    x=Dense(1024,activation='relu')(x)
    # x=Dense(1024,activation='relu')(x) # dense layer 2, removal speeds uo train and does not affect performance significantly
    x=Dense(512,activation='relu')(x) #dense layer 3
    preds=Dense(labels_num,activation='softmax')(x) #final layer with softmax activation

    #specify the inputs
    #specify the outputs
    model=Model(inputs=base_model.input,outputs=preds)
    #now a model has been created based on selected architecture

    # freeze layers already trained
    for layer in model.layers[:20]:
        layer.trainable=False
    for layer in model.layers[20:]:
        layer.trainable=True

    # now use the model as usual

    model.compile(loss='categorical_crossentropy',
                      optimizer=rms,
                      metrics=['accuracy'])

    # alternative and custom preprocessing and data augmentation
    #train_datagen = ImageDataGenerator(
    #    rescale=1./255,
    #    zoom_range=0.2,
    #    rotation_range=20,
    #    horizontal_flip=True,
    #    vertical_flip=True
    #)

    # use pretrained network preprocessing
    train_datagen=ImageDataGenerator(preprocessing_function=preprocess_input) #included in our dependencies

    # this is a generator that will read pictures found in
    # subfolders of path, and indefinitely generate
    # batches of augmented image data
    train_generator = train_datagen.flow_from_directory(
        TRAIN_PATH,  # this is the target directory
        target_size=(INPUT_SIZE, INPUT_SIZE),  # all images will be resized to 150x150
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    # train_generator is DirectoryIterator yielding tuples of (x, y) where x is a
    # numpy array containing a batch of images with shape
    # (batch_size, *target_size, channels) and y is a numpy array of corresponding labels

    # Check on loaded files
    # sample_batch = next(train_generator)
    # print('Train img shape: ' + str(sample_batch[0].shape))

    # Setup the rest of parameters for training
    if USE_VAL:
        # for test, only rescaling
        test_datagen = ImageDataGenerator(rescale=1./255)

        # similar generator, for validation data
        validation_generator = test_datagen.flow_from_directory(
                VAL_PATH,
                target_size=(INPUT_SIZE, INPUT_SIZE),
                batch_size=BATCH_SIZE,
                class_mode='categorical')

        # TRAIN
        step_size_train=train_generator.n//train_generator.batch_size

        model.fit_generator(
                train_generator,
                steps_per_epoch=step_size_train,
                epochs=30,
                validation_data=validation_generator,
                validation_steps=50 // BATCH_SIZE)
    else:
        # TRAIN WITHOUT VALIDATION (ONLY FOR DEBUG)
        model.fit_generator(
            train_generator,
            steps_per_epoch=1000 // BATCH_SIZE,
            epochs=30,
            validation_data=None,
            validation_steps=50 // BATCH_SIZE)

    # creation of unique model name
    model_filename = 'model' + str(datetime.datetime.now().isoformat())

    # serialize model to JSON
    model_json = model.to_json()
    with open(model_filename + '.json', "w") as json_file:
        json_file.write(model_json)

    # serialize weights to HDF5
    model.save_weights(model_filename + '.h5')

    print("Saved model to disk as " + model_filename)
