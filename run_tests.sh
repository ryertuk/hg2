#!/bin/bash
pytest --cov=app --cov-report=html
echo "Tests passed. Coverage report in htmlcov/"
echo "Press any key to continue..."
read -n 1 -s