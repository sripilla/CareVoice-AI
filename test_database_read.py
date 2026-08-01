from database.database import DatabaseManager

db = DatabaseManager()

reports = db.get_all_reports()

print("\n========== STORED REPORTS ==========\n")

for report in reports:
    print(report)

db.close()