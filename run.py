import uvicorn
from fastapi import FastAPI

from blockchain import Blockchain
from models import Transaction

app = FastAPI()
blockchain = Blockchain()


@app.get("/transactions")
async def pool_transactions():
    return blockchain.pooled_transactions


@app.post("/transactions")
async def new_transaction(transaction: Transaction):
    blockchain.new_transaction(transaction)

    response = {
        'success': True
    }
    return response


@app.get("/chain")
async def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return response


@app.get("/verify")
async def full_chain():
    return {
        "success": blockchain.validate_chain(blockchain.chain)
    }


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
