from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from datetime import datetime

# Initialize SparkContext and StreamingContext
sc = SparkContext("local[2]", "LineWiseWordCount")
ssc = StreamingContext(sc, 1)  # 1 second batch interval
ssc.checkpoint("./checkpoint_directory")  # Specify the checkpoint directory

# Directory where new data files will be placed (for streaming)
directory = "./text_file_directory"

# Function to split lines into words and lowercase them
def count_words(line):
    words = line.split()
    return [(word.lower(), 1) for word in words]

# Function to update the running counts of words
def update_function(new_values, running_count):
    return sum(new_values) + (running_count or 0)

# Create a DStream that reads new text files added to `directory`
lines = ssc.textFileStream(directory)

# Count each word in each batch and update their counts
word_counts = lines.flatMap(count_words).reduceByKey(lambda x, y: x + y)
word_totals = word_counts.updateStateByKey(update_function)

# Placeholder for the last seen word counts
last_seen_counts = []

# Function to print word counts; prints all words appeared in file
def print_word_counts(rdd):
    global last_seen_counts
    current_counts = rdd.collect()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not current_counts:  # If the RDD is empty
        if last_seen_counts == []:
            print(f"[{current_time} - No data in this interval.]")
        else:
            print(f"[{current_time} - The data hasn't changed in this interval.]")
    else:
        print(f"\n[{current_time} - Word counts:]")
        count_list = [{word: count} for word, count in current_counts]
        print(count_list)
        last_seen_counts = current_counts  # Update the last seen counts

# Apply the function to print word counts for each RDD in the stream
word_totals.foreachRDD(print_word_counts)

# Start the computation
ssc.start()

# Wait for the computation to terminate
ssc.awaitTermination()
