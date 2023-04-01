#!/bin/bash

# Set Internal Field Seperator to Comma to maintain sanity for this...
OLDIFS=$IFS; IFS=',';

# Set the input file and the points at which to split the audio
input_file="input.mp3"
output_prefix="Album Name"

declare -a split_points=(
  "00:00:00,Track 1"
  "00:13:22,Track 2"
  "00:25:34,Track 3"
)

# Loop through the split points and create a new output file for each segment
i=1
for track in "${split_points[@]}"
do
    #echo $track
    set -- $track
    echo $1 $2
    start_time=$1
    track_name=$2
    # Set the end time of the segment
    # If the loop counter = the array length then it pulls the end of the file
    # Otherwise the loop counter is referenced to get the next element in the array and then pull that for the end time
    if [[ $i -eq ${#split_points[@]} ]]; then
        # If this is the last split point, set the end time to the end of the file
        end_time=$(ffprobe -i "$input_file" -show_format -v quiet | sed -n 's/duration=//p')
        echo "$end_time"
    else
        next_elem=${split_points[$((i))]}
        set -- $next_elem
        echo $1
        end_time=$1
    fi

    # Create the output file name based on the name and the part number
     output_file="${output_prefix}_${track_name}.mp3"

    # Extract the segment of audio from the input file and save it to the output file
     ffmpeg -i "$input_file" -ss "$start_time" -to "$end_time" -c copy "$output_file"

    # Increment the part number
    ((i++))
done

IFS=$OLDIFS

