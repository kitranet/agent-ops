import sqlite3
import os

def generate_markdown(agent_id):
    os.makedirs("docs", exist_ok=True)
    conn = sqlite3.connect("agentops.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents WHERE agent_id=?", (agent_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        with open(f"docs/{agent_id}.md", "w") as f:
            f.write(f"# Agent Report: {row[0]}\n")
            f.write(f"**Version**: {row[1]}\n")
            f.write(f"**Framework**: {row[2]}\n")
            f.write(f"**Owner**: {row[3]}\n")
            f.write(f"**Status**: {row[4]}\n")
            f.write(f"**Task**: {row[5]}\n")
            f.write(f"**Health Endpoint**: {row[6]}\n")
            f.write(f"**Deployed At**: {row[7]}\n")
