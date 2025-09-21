set -e
set -x


TEST_DB=1 poetry run pytest -x --cov=./ --no-cov-on-fail --cov-report term-missing ./"$1" 2>&1
set +x
last_line=$(poetry run coverage report | grep "TOTAL")

# Extract the coverage percentage from the last line
coverage=$(echo "$last_line" | awk '{print $NF}')

# Extract the numeric value from the coverage percentage
numeric_coverage=$(echo "$coverage" | tr -d '%')

required_coverage=75

# Compare the numeric coverage value to $required_coverage
if [ "$numeric_coverage" -gt $required_coverage ]; then
  echo "Passed: Coverage is $numeric_coverage, required; $required_coverage"
  exit 0
else
  echo "Failed: Coverage is not greater than $required_coverage%"
  echo "Coverage is $numeric_coverage"
  exit 1
fi

