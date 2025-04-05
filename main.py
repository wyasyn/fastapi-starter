import os
from fastapi import FastAPI, Query, Path, HTTPException
from typing import Optional
from datetime import datetime
from fastapi.responses import FileResponse

from data import all_tasks, write_tasks_to_csv, CSV_FILE as CSV_PATH
from schema import TaskCreate, TaskList, TaskUpdate, Task, Priority

app = FastAPI()


@app.get("/", response_model=TaskList, tags=["Tasks"])
def read_tasks(
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    search: Optional[str] = Query(None, description="Search keyword in title or description"),
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|priority)$", description="Sort by 'created_at' or 'priority'"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order 'asc' or 'desc'"),
    page: Optional[int] = Query(1, ge=1, description="Page number"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Items per page")
):
    tasks = all_tasks

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks available.")

    # Filter
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    if completed is not None:
        tasks = [task for task in tasks if task.completed == completed]
    if search:
        search_lower = search.lower()
        tasks = [task for task in tasks if search_lower in (task.title or '').lower() or search_lower in (task.description or '').lower()]

    # Sort
    reverse = sort_order == "desc"
    if sort_by == "priority":
        tasks = sorted(tasks, key=lambda x: x.priority, reverse=reverse)
    elif sort_by == "created_at":
        tasks = sorted(tasks, key=lambda x: x.created_at, reverse=reverse)

    # Pagination metadata
    total_items = len(tasks)
    total_pages = (total_items + page_size - 1) // page_size  # ceiling division
    if page > total_pages and total_pages != 0:
        raise HTTPException(status_code=404, detail="Page number exceeds total pages.")

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated_tasks = tasks[start:end]

    return {
        "tasks": paginated_tasks,
        "total": total_items,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }




@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def read_task(task_id: int = Path(..., ge=1)):
    for task in all_tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks", response_model=Task, status_code=201, tags=["Tasks"])
def create_task(task: TaskCreate):
    task_id = max([t.id for t in all_tasks], default=0) + 1
    now = datetime.utcnow()
    new_task = Task(
        id=task_id,
        created_at=now,
        updated_at=now,
        **task.dict()
    )
    all_tasks.append(new_task)
    write_tasks_to_csv(all_tasks)
    return new_task


@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def update_task(task_id: int, task_update: TaskUpdate):
    for index, task in enumerate(all_tasks):
        if task.id == task_id:
            updated_data = task.dict()
            update_fields = task_update.dict(exclude_unset=True)
            updated_data.update(update_fields)
            updated_data["id"] = task.id
            updated_data["created_at"] = task.created_at
            updated_data["updated_at"] = datetime.utcnow()
            updated_task = Task(**updated_data)
            all_tasks[index] = updated_task
            write_tasks_to_csv(all_tasks)
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def delete_task(task_id: int):
    for index, task in enumerate(all_tasks):
        if task.id == task_id:
            removed_task = all_tasks.pop(index)
            write_tasks_to_csv(all_tasks)
            return removed_task
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/download", response_class=FileResponse, tags=["Tasks"])
def download_tasks_csv():
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="CSV file not found.")
    
    return FileResponse(
        path=CSV_PATH,
        filename="tasks.csv",
        media_type="text/csv"
    )