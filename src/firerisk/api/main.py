from unittest.mock import Base
from fastapi import FastAPI

from src.firerisk.api.databases.postgres.models import POSTGRES_Base
from src.firerisk.api.databases.postgres.database import POSTGRES_engine

from src.firerisk.api.databases.timescale.models import TIMESCALE_Base
from src.firerisk.api.databases.timescale.database import TIMESCALE_engine

from src.firerisk.api.routers import auth, frcm, admin, users

# POSTGRES_Base.metadata.create_all(bind=POSTGRES_engine)
# TIMESCALE_Base.metadata.create_all(bind=TIMESCALE_engine)

app = FastAPI()


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}

app.include_router(auth.router)
app.include_router(frcm.router)
app.include_router(admin.router)
app.include_router(users.router)