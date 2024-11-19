# Poluição do Ar - RMSP

# Dependencies
- `Python`
- `MySQL`

# Installation
Install all the required `Python` packages listed in the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

# Database Setup Instructions
Follow these steps to set up and update the database from the **root directory** of the repository. These instructions apply to both `macOS` and `Linux` users.

## 1. Start MySQL Service
### Linux
```bash
sudo systemctl start mysql
```
### macOS
On `macOS`, MySQL typically runs automatically if installed through Homebrew or MySQL installer. If not, run the following:
```bash
brew services start mysql
```

## 2. Create Tables
```bash
python -m backend.src.database.create_tables
```
*This command creates the necessary tables in the database. Make sure you're executing this from the root directory of the repository.*

## 3. Populate Tables
```bash
python -m backend.src.database.populate_tables
```
*Populate the newly created tables with the initial data by running this script.*

## 4. Update Tables
```bash
python3 backend/data/database/update_tables.py
```
*Run this command whenever you want to update the tables with the most recent data.*

