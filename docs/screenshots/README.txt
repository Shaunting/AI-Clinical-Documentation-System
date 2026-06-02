demo.gif — Project demo (embedded in README and docs/index.html)

To regenerate from a new recording:
  ffmpeg -i "../files/Demo Video.mp4" -vf "fps=8,scale=1200:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse" -loop 0 demo.gif
