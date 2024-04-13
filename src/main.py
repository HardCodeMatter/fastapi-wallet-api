import uvicorn
from fastapi import FastAPI

from routers import routers


app = FastAPI(
    title='WalletAPI',
    version='0.1.0',
)


for router in routers:
    app.include_router(router=router, prefix='/api/v1')


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
