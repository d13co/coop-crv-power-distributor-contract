function bigprint {
  head=$(echo "  $@  " | sed 's/./=/g')
  echo "$head"
  echo "  $@  "
  echo "$head"
}
