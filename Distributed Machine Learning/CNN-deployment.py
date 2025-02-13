# Create Sagemaker execution role
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
import boto3
import os


role = sagemaker.get_execution_role()
sess = sagemaker.Session()
bucket = sess.default_bucket()


s3_prefix = "script-mode-workflow"
pickle_s3_prefix = f"{s3_prefix}/pickle"
pickle_s3_uri = f"s3://{bucket}/{s3_prefix}/pickle"
pickle_train_s3_uri = f"{pickle_s3_uri}/train"


train_dir = os.path.join(os.getcwd(), "")

# Obtaining training data and data preprocessing


import numpy as np
import pickle


def pickleTrainingData():
    def unpickle(file):
        with open(file, 'rb') as fo:
            dict = pickle.load(fo, encoding='bytes')
        return dict


    train_data = np.empty((0, 32*32*3))
    train_labels = []


    for i in range(1, 2):
        fileNameDataBatch = './cifar-10-batches-py/data_batch_' + str(i)
        batch = unpickle(fileNameDataBatch)
        train_data = np.vstack((train_data, batch[b'data']))
        train_labels += batch[b'labels']


    train_labels = np.array(train_labels)
    train_data = train_data.reshape(-1, 32, 32, 3) / 255.0
    
    pickle.dump([train_labels,train_data], open('./train.cnn', 'wb'))


pickleTrainingData()



# Uploading training data to s3 bucket
s3_resource_bucket = boto3.Session().resource("s3").Bucket(bucket)
s3_resource_bucket.Object(os.path.join(pickle_s3_prefix, "train.cnn")).upload_file(
    train_dir + "/train.cnn"
)

# Setting up estimator and invoking cnnScript


entry_point = "cnnScript.py"


train_instance_type = "ml.m5.large"


estimator_parameters = {
    "entry_point": entry_point,
    "source_dir": "script",
    "framework_version": "0.23-1",
    "py_version": "py3",
    "instance_type": train_instance_type,
    "instance_count": 1,
    "role": role,
    "base_job_name": "cnn-model",
}


estimator = SKLearn(**estimator_parameters)


inputs = {
    "train": pickle_train_s3_uri
}


# starting the training job
estimator.fit(inputs)


# Creating the endpoint to interact with our model


predictor = estimator.deploy(initial_instance_count=1,
                                     instance_type='ml.m5.large',
                                     endpoint_name='cnn-endpoint')



# Obtaining test data and storing the data and its corresponding labels


def getTestData():
    def unpickle(file):
        with open(file, 'rb') as fo:
            dict = pickle.load(fo, encoding='bytes')
        return dict
    fileNameTestBatch = './cifar-10-batches-py/test_batch'
    test_data = unpickle(fileNameTestBatch)[b'data']
    test_data = test_data.reshape(-1, 32, 32, 3) / 255.0
    test_labels = np.array(unpickle(fileNameTestBatch)[b'labels'])
    
    num_samples_to_select = 600
    random_indices = np.random.choice(test_data.shape[0], num_samples_to_select, replace=False)
    selected_test_data = test_data[random_indices]
    selected_test_labels = test_labels[random_indices]
    
    return selected_test_data, selected_test_labels


test_data, test_labels = getTestData()


# Predicting on test data and calculating accuracy of predictions


from sklearn.metrics import accuracy_score


def getAccuracyOfPrediction(cnn_predictions, test_labels):
    cnn_predicted_labels = np.argmax(cnn_predictions, axis=1)
    accuracy = accuracy_score(test_labels, cnn_predicted_labels)
    print("Accuracy:", accuracy)
    
    
predictions = predictor.predict(test_data)


getAccuracyOfPrediction(predictions, test_labels)


# Cleanup of endpoint

predictor.delete_endpoint(True)
