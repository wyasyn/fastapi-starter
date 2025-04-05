from datetime import datetime
import csv
from typing import List
from schema import Task, Priority
# from pprint import pprint

CSV_FILE = "tasks.csv"

def read_tasks_from_csv() -> List[Task]:
    tasks = []
    try:
        with open(CSV_FILE, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row.get("id"):  # skip empty rows
                    continue
                task = Task(
                    id=int(row["id"]),
                    title=row["title"],
                    description=row["description"] or None,
                    priority=Priority(int(row["priority"])),
                    completed=row["completed"].lower() == "true",
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"])
                )
                tasks.append(task)
    except FileNotFoundError:
        print("CSV file not found. Starting with empty task list.")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return tasks



def write_tasks_to_csv(tasks: List[Task]) -> None:
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "id", "title", "description", "priority", "completed", "created_at", "updated_at"
        ])
        writer.writeheader()
        for task in tasks:
            writer.writerow({
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "priority": task.priority,
                "completed": str(task.completed),
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            })


# In-memory store
all_tasks: List[Task] = read_tasks_from_csv()


# pprint(read_tasks_from_csv())