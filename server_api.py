from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import uvicorn
from uuid import uuid4



app = FastAPI()

# Modelo de datos para las cadenas de texto
class TextItem(BaseModel):
    text: str

# Almacenamiento en memoria de los datos
storage: Dict[int, str] = {}
current_id = 0

@app.post("/add/")
async def add_text(item: TextItem):
    global current_id
    current_id += 1
    storage[current_id] = item.text
    return current_id

@app.get("/get/{item_id}")
async def get_text(item_id: int):
    if item_id not in storage:
        raise HTTPException(status_code=404, detail="Item not found")
    return storage[item_id]

@app.delete("/delete/{item_id}")
async def delete_text(item_id: int):
    if item_id not in storage:
        raise HTTPException(status_code=404, detail="Item not found")
    del storage[item_id]
    return {"message": "Item deleted successfully"}

import psutil

def close_port(port):
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port:
            print(f"Closing port {port} by terminating PID {conn.pid}")
            process = psutil.Process(conn.pid)
            process.terminate()



if __name__ == "__main__":
    puerto = 8000
    close_port(puerto)
    #ip = "170.210.32.67"
    ip = "0.0.0.0"
    uvicorn.run(app)
    # ngrok http http://localhost:8000 

