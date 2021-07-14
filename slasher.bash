#!/usr/bin/env bash

# Recreate temporary filter complex
rm -f /tmp/filter_complex.ff
touch /tmp/filter_complex.ff

# Argument parsing
IN=$1
INTERVALS=$2
OUT=$3

# Create FFmpeg filter complex through looping through timestamps
# Thanks shawnblais and Hashim Aziz!
# https://superuser.com/questions/681885/how-can-i-remove-multiple-segments-from-a-video-using-ffmpeg/1498811#1498811
i=0
pairs=()
while read -r line; do
	let i+=1
	
	# Separate silence end and silence length
	array=($line)
	start=${array[0]}
	length=${array[1]}

    # Get start of silence
	end=$(($start + $length))

	# Append filter context with new trim filters
	echo "[0:v]trim=start=$start:end=$end,setpts=PTS-STARTPTS,format=yuv420p[${i}v];[0:a]atrim=start=$start:end=$end,asetpts=PTS-STARTPTS[${i}a];" >> /tmp/filter_complex.ff
	pairs+=("[${i}v]" "[${i}a]")
done < $INTERVALS

# Combine all of our generated A/V pairs
pairs_str=$(printf '%s' "${pairs[@]}")

# Append concatenation line
echo "${pairs_str}concat=n=$i:v=1:a=1[outv][outa]" >> /tmp/filter_complex.ff

# Apply filter complex to input
ffmpeg -hide_banner -i "$IN" -filter_complex_script /tmp/filter_complex.ff -map [outv] -map [outa] $OUT
