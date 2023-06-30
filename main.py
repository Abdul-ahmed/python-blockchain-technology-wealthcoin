# Module 1 - Part 1 - Create a Blockchain
# Building a blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }

        self.transactions = []
        self.chain.append(block)
        return block

    def previous_block(self):
        return self.chain[-1]

    @staticmethod
    def proof_of_work(previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    @staticmethod
    def hash(block):
        encode_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encode_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })

        previous_block = self.previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/blockchain-blocks')
            if response.status_code == 200:
                length = response.json()['data']['length']
                chain = response.json()['data']['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# Module 1 - Part 2 - Mining our Blockchain
# Creating web service api
app = Flask(__name__)
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an address for node in port 500
node_address = str(uuid4()).replace('-', '')

# Our blockchain instantiation
blockchain = Blockchain()


# Home
@app.route("/", methods=['GET'])
def home():
    return jsonify({
        "status": True,
        "code": 200,
        "message": "Welcome to my blockchain"
    }), 200


# Mining block
@app.route("/mine-block", methods=['GET'])
def mine_block():
    previous_block = blockchain.previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver='Ahmed', amount=1)
    block = blockchain.create_block(proof, previous_hash)
    response = {
        "status": True,
        "code": 200,
        "message": "Block mined successfully",
        "data": {
            "index": block["index"],
            "timestamp": block["timestamp"],
            "proof": block["proof"],
            "previous_hash": block["previous_hash"],
            "transactions": block["transactions"]
        }
    }
    return jsonify(response), 200


# Get blockchain
@app.route("/blockchain-blocks", methods=['GET'])
def blockchain_blocks():
    response = {
        "status": True,
        "code": 200,
        "message": "Block mined successfully",
        "data": {
            "chain": blockchain.chain,
            "length": len(blockchain.chain)
        }
    }

    return jsonify(response), 200


# Check Blockchain
@app.route("/validate-blockchain", methods=['GET'])
def validate_blockchain():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {
            "status": True,
            "code": 200,
            "message": "Blockchain is valid",
        }
    else:
        response = {
            "status": False,
            "code": 400,
            "message": "Blockchain is invalid",
        }
    return jsonify(response), response["code"]


# Module 2 - Part 1 - Decentralizing our blockchain
# Add new transaction to Blockchain
@app.route("/add-transaction", methods=['POST'])
def add_transaction():
    json_request = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json_request for key in transaction_keys):
        return "Some keys are missing", 400

    index = blockchain.add_transaction(json_request['sender'], json_request['receiver'], json_request['amount'])
    response = {
        "status": True,
        "code": 201,
        "message": f"Transaction will be added to the Block {index}"
    }
    return jsonify(response), response["code"]


# Connecting nodes
@app.route("/connect-nodes", methods=['POST'])
def connect_nodes():
    json_request = request.get_json()
    nodes = json_request.get("nodes")
    if nodes is None:
        return "Empty node", 400

    for node in nodes:
        blockchain.add_node(node)

    response = {
        "status": True,
        "code": 201,
        "message": f"All nodes connected and and WealthCoin contains the following nodes",
        "data": {
            "total_nodes": list(blockchain.nodes)
        }
    }

    return jsonify(response), response["code"]


# Replacing the chain with the longest chain
@app.route("/replace-chain", methods=['GET'])
def replace_chain():
    chain_replaced = blockchain.replace_chain()
    if chain_replaced:
        response = {
            "status": True,
            "code": 200,
            "message": "Chain replaced",
            "data": {
                "new_chain": blockchain.chain
            }
        }
    else:
        response = {
            "status": False,
            "code": 400,
            "message": "Currently the longest, all good",
            "data": {
                "actual_chain": blockchain.chain
            }
        }
    return jsonify(response), response["code"]

# Creating a cryptocurrency (WealthCoin)


# app.run(host = '127.0.0.1', port = 5000)
app.run(host='0.0.0.0', port=5000)
