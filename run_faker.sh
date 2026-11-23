#!/bin/bash

cd C:/Users/HP/Desktop/sales-inventory || exit 1


rm -f  uploaded_files/.test_database.db
python db_faker.py

echo "Database updated on $(date)" >> faker_update.log

