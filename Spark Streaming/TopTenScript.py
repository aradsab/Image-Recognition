from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from datetime import datetime

# Create a local StreamingContext with two working threads and batch interval of 1 second
sc = SparkContext("local[2]", "FileWiseTop10WordCount")
ssc = StreamingContext(sc, 1)  # Batch interval of 1 second
ssc.checkpoint("checkpoint_directory")  # Provide a directory for checkpointing

# Directory where new data files will be placed (for streaming)
directory = "./text_file_directory"

# Create a DStream that reads new text files added to `directory`
lines = ssc.textFileStream(directory)

# This function splits lines into words
def split_into_words(line):
    return line.split()

# Count each word in each batch
words = lines.flatMap(split_into_words)
pair_words = words.map(lambda word: (word, 1))
word_counts = pair_words.reduceByKey(lambda x, y: x + y)

# Update the counts using updateStateByKey
updated_counts = word_counts.updateStateByKey(
    lambda new_values, running_count: sum(new_values) + (running_count or 0)
)

# Function to sort and print the top 10 words across all batches in the desired format
def print_top10_word_counts(rdd):
    if rdd.isEmpty():
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No data in this interval.")
    else:
        top10 = rdd.takeOrdered(10, key=lambda x: -x[1])
        top10_formatted = [{word: count} for word, count in top10]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} - Top 10 words: {top10_formatted}")

# Apply the function to each RDD in the stream
updated_counts.foreachRDD(print_top10_word_counts)

# Start the computation
ssc.start()

# Wait for the computation to terminate
ssc.awaitTermination()
