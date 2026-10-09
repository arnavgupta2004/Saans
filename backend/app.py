from fastapi import FastAPI
from mangum import Mangum


app = FastAPI(title="Saans", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, bool | str]:
    return {"ok": True, "version": "0.1.0"}


handler = Mangum(app)
