import sqlite3

conn = sqlite3.connect('telegram_mini_app.db')
cursor = conn.cursor()

# Исправляем формулы водорода и хлора (латиница)
cursor.execute("UPDATE gas_molecules SET formula = 'H2' WHERE id = 1")
cursor.execute("UPDATE gas_molecules SET formula = 'Cl2' WHERE id = 4")

# На всякий случай убедимся, что ключ в реакциях тоже латиница
cursor.execute("UPDATE predefined_reactions SET reaction_key = 'Cl2+H2' WHERE id = 1")

conn.commit()
print("Формулы и ключ исправлены.")
conn.close()