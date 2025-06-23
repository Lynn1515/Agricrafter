for file in assets/demo_video/*.mp4; do
  ffmpeg -i "$file" -vf "fps=8,scale=320:-1:flags=lanczos" -loop 0 "${file%.mp4}.gif"
done