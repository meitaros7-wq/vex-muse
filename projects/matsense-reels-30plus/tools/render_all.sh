cd /home/user/vex-muse/projects/matsense-reels-30plus/motion
for n in 1 2 3 4 5; do
  (cd ad$n && timeout 2400 npx hyperframes@0.8.145 render -o ../../renders/matsense-reel-$n.mp4 --quality delivery > ../../renders/render-$n.log 2>&1; echo "ad$n exit $?")
done
