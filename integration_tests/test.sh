jupyter $1 --no-browser&> output.log &
APP_PID=$!
sleep 10
kill $APP_PID
cat output.log
if grep -q "nbautoexport | Successfully registered post-save hook." output.log; then
  echo "nbautoexport post-save hook successfully registered"
else
  echo "nbautoexport post-save hook failed to register"
  exit 1
fi
