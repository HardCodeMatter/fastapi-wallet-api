import uvicorn
from fastapi import FastAPI


app = FastAPI(
    title='WalletAPI',
    version='0.1.0',
)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
