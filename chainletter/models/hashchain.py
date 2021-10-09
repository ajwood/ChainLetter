import hashlib
import random
import re

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import validates, relationship

from . import db

class HashChain(db.Model):
    __tablename__ = "hashchain"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("hashchain.id"))
    sha256 = Column(String(64), unique=True)

    # Adapted from https://stackoverflow.com/a/20834316/512652
    parent = relationship(lambda: HashChain, remote_side=id, backref="children")

    def __init__(self, parent_id, sha256, is_root=False):
        """
        An entry in the hash chain.

        I'm paranoid about accidentally having a NULL parent_id (see
        https://stackoverflow.com/q/69420311/512652), so we have to set is_root
        to allow NULL.
        """
        if parent_id is None and not is_root:
            raise ValueError("attempting parent_id=None, but is_root is False")
        self.parent_id = parent_id
        self.sha256 = sha256

    def __repr__(self):
        return f"HashChain({self.id}, {self.parent_id}, '{self.sha256[:6]}...')"

    @property
    def nchildren(self):
        """Number of children nodes"""
        return len(self.children)

    @staticmethod
    def make_root():
        """
        Make a chain root node (i.e. parent_id=NULL and a random sha256)
        """
        rand_hash = "{:064x}".format(random.getrandbits(256))
        return HashChain(parent_id=None, sha256=rand_hash, is_root=True)

    def make_child(self):
        """Make a new child instance"""
        if self.id is None:
            raise RuntimeError(
                "Attempting to make child from a new instance that hasn't yet been assigned an id"
            )
        val = f"{self.sha256}{self.nchildren}"
        sha256 = hashlib.sha256(val.encode()).hexdigest()

        # Add the new child to our list. I'm not totally sure whether it should
        # be our responsibility to do this, or leave it up to the caller to
        # add it to their session.
        child = HashChain(parent_id=self.id, sha256=sha256)
        self.children.append(child)
        return child

    @validates("sha256")
    def validate_sha256(self, key, sha256):
        """Should be 64 hex characters"""
        if not re.match(r"^[0-9a-f]{64}$", sha256):
            raise ValueError(f"Illegal sha256 value '{sha256}' (len {len(sha256)})")
        return sha256
