# Project Summaries

## 1. Spark Streaming Application Architecture
**Description**:  
This project involves building a Spark Streaming application designed for real-time processing of text data. The application computes word frequencies from text files placed in a specified directory. It demonstrates a typical stream processing architecture using Apache Spark.

**Highlights**:  
- **FileWiseTop10WordCount**: Identifies and prints the top 10 words by frequency after stateful processing, including timestamps for real-time status updates.
- **LineWiseWordCount**: Provides a comprehensive count of all words in each batch, incorporating a mechanism to detect and notify when no new data changes occur.
- **Key Features**:
  - DStream transformations: Splitting, mapping, reducing.
  - Stateful word count tracking with `updateStateByKey`.
  - Real-time output and fault tolerance with checkpointing.
- **Performance Considerations**: Processes data in near real-time with a 1-second batch interval and includes scalability suggestions for handling high data injection rates.

---

## 2. CIFAR-10 CNN Training and Deployment on AWS SageMaker
**Description**:  
This project demonstrates the end-to-end workflow of training, saving, loading, deploying, and running a Convolutional Neural Network (CNN) model using the CIFAR-10 dataset. The deployment utilizes AWS SageMaker for distributed training and inference, with a comparison to local machine execution.

**Highlights**:  
- **CNN Training on CIFAR-10**:  
  - Preprocessing includes image normalization and augmentation.  
  - The CNN model is trained iteratively on five data batches and validated on a separate test set.
- **AWS SageMaker**:  
  - Fully managed service for building, training, and deploying ML models.
  - Utilizes SageMaker's distributed training features and scalable endpoints for real-time predictions.
- **Key Features**:
  - Data preparation using Amazon S3.
  - Deployment with SageMaker endpoints.
  - Monitoring training progress with built-in tools.
- **Performance Comparison**: Evaluates SageMaker's distributed capabilities against a local machine to highlight scalability and efficiency.

---

These two projects illustrate the effective use of modern tools and frameworks for scalable data processing and machine learning workflows, providing insights into real-time analytics and cloud-based deployment strategies.
