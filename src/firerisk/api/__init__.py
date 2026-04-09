import uvicorn
import os

def main() -> None:
    uvicorn.run(
        "firerisk.api.main:app",
        host=os.getenv("APP_HOST", "localhost"),
        port=int(os.getenv("APP_PORT", 6767)),
        reload=True,
        reload_dirs=["/app/src"],
    )


if __name__ == "__main__":
    main()
        