import uvicorn
import os

def main() -> None:
    uvicorn.run(
        "firerisk.api_keycloak.main:app",
        host=os.getenv("APP_HOST", "localhost"),
        port=int(os.getenv("APP_PORT", 6767)),
        reload=True,
    )


if __name__ == "__main__":
    main()
        