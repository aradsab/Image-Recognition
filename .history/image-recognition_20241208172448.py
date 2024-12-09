import argparse
import os
import numpy as np
import pickle
import subprocess
subprocess.run(["pip", "install", "Werkzeug==2.0.3"])
subprocess.run(["pip", "install", "tensorflow==2.4"])
import tensorflow as tf
from tensorflow import keras

def parse_args():
#     Adapted from the example code in A6 file
    """
    Parse arguments.
    """
    parser = argparse.ArgumentParser()

    # hyperparameters sent by the client are passed as command-line arguments to the script
    # We don't use these but I left them in as a useful template for future development
    parser.add_argument("--copy_X",        type=bool, default=True)
    parser.add_argument("--fit_intercept", type=bool, default=True)
    parser.add_argument("--normalize",     type=bool, default=False)
    
    # data directories
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--test", type=str, default=os.environ.get("SM_CHANNEL_TEST"))

    # model directory: we will use the default set by SageMaker, /opt/ml/model
    parser.add_argument("--model_dir", type=str, default=os.environ.get("SM_MODEL_DIR"))

    return parser.parse_known_args()


def load_dataset(path):
    """
    Load dataset from pickle file.
    """
    files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith(".cnn")]
    
    if len(files) == 0:
        raise ValueError("No data files found in directory: {}".format(path))

    with open(files[0], 'rb') as f:
        train_labels, train_data = pickle.load(f)
    
    return train_data, train_labels


def model_fn(model_dir):
    """
    Load the model for inference
    """
    loaded_model = tf.keras.models.load_model(os.path.join(model_dir, "modelCNN"))
    return loaded_model

def predict_fn(input_data, model):
    """
    Apply model to the incoming request.
    """
    return model.predict(input_data)


def create_model():
    model = keras.Sequential([
        keras.layers.Conv2D(filters=32, kernel_size=3, activation='relu', input_shape=(32, 32, 3)),
        keras.layers.MaxPooling2D(pool_size=2),
        keras.layers.Conv2D(filters=64, kernel_size=3, activation='relu'),
        keras.layers.MaxPooling2D(pool_size=2),
        keras.layers.Flatten(),
        keras.layers.Dense(units=128, activation='relu'),
        keras.layers.Dense(units=10, activation='softmax')
    ])
    return model


if __name__ == "__main__":
    args, _ = parse_args()

    print("Training mode")
    try:
        # Load data
        X_train, y_train = load_dataset(args.train)
        X_train = X_train.reshape((-1, 32, 32, 3))

        print("Training...")
        model = create_model()
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        
        # Train the model
        model.fit(X_train, y_train, epochs=3, batch_size=32, validation_split=0.1)

        # Save the model to the specified directory
        model.save(os.path.join(args.model_dir, 'modelCNN'))

    except Exception as e:
        import traceback
        import sys

        trc = traceback.format_exc()
        with open(os.path.join(args.model_dir, "failure"), "w") as s:
            s.write("Exception during training: " + str(e) + "\n" + trc)

        print("Exception during training: " + str(e) + "\n" + trc, file=sys.stderr)
        sys.exit(255)