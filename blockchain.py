import hashlib
import json
import logging
import random
from time import time

from models import Transaction

logger = logging.getLogger(__name__)

RECIPIENT = 'recipient'


class Blockchain:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Blockchain, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        self.nodes = set()
        self.chain = []
        self.next_block_id = 0
        self.pooled_transactions = []

        # Create the genesis block
        self._add_block(proof=0, previous_hash=0, comment="Genesis Block")

    @property
    def last_block(self):
        return self.chain[-1]

    def _mine(self):
        """Dummy mining function that is always success"""
        last_proof = self.last_block['proof']
        new_pow = self.proof_of_work(last_proof)

        previous_hash = self.hash(self.last_block)
        self._add_block(new_pow, previous_hash)

        # Reward for mining
        # sender = 0 mean this is system generated
        self.new_transaction(
            Transaction(
                sender="0",
                recipient=RECIPIENT,
                amount=1,
                comment="Mining Reward"
            )
        )

    def _add_block(self, proof, previous_hash=None, comment=None):
        """
        Create a new Block in the Blockchain

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        if previous_hash is None:
            previous_hash = self.hash(self.chain[-1])

        block = {
            'id': self.next_block_id,
            'timestamp': time(),
            'transactions': self.pooled_transactions,
            'proof': proof,
            'previous_hash': previous_hash,
            'comment': comment
        }

        self.chain.append(block)
        self.next_block_id += 1
        self.pooled_transactions = []

        return block

    def random_test_for_new_block(self):
        if len(self.pooled_transactions) < 3:
            return False

        return random.choice([True, False])

    def new_transaction(self, transaction: Transaction):
        self.pooled_transactions.append({
            'sender': transaction.sender,
            'recipient': transaction.recipient,
            'amount': transaction.amount,
            'comment': transaction.comment,
            'timestamp': time(),
        })

        if not self.random_test_for_new_block():
            return

        logger.debug("Creating new block")
        self._mine()

    @staticmethod
    def hash(block):
        """
        Creates SHA-256 hash of a Block

        :param block: <dict> Block
        :return: <str>
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.validate_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def validate_proof(last_proof, new_proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param new_proof: <int> New Proof
        :return: <bool> True if correct, False if not.
        """
        guess = f'{last_proof}{new_proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def validate_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        if len(chain) <= 1:
            return True

        curr_block = chain[-1]
        pointer = curr_block['id'] - 1  # 2nd last block of the chain
        while pointer >= 0:
            prev_block = chain[pointer]
            if self.hash(prev_block) != curr_block['previous_hash']:
                return False

            if not self.validate_proof(prev_block['proof'], curr_block['proof']):
                return False

            curr_block = prev_block
            pointer -= 1

        return True
