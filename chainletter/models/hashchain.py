import hashlib
import random
import re
import os

from sqlalchemy import Column, ForeignKey, Integer, String, func, DateTime
from sqlalchemy.orm import validates, relationship

from chainletter.models.letter import Letter

from . import db


class HashChain(db.Model):
    __tablename__ = "hashchain"

    # Max number of allowed children
    MAX_DEGREE = 5

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("hashchain.id"))
    sha256 = Column(String(64), unique=True)
    created_on = Column(DateTime(timezone=True), server_default=func.now())

    # Adapted from https://stackoverflow.com/a/20834316/512652
    _parent = relationship(lambda: HashChain, remote_side=id, backref="children")

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
    def parent(self):
        """
        The parent node. Reason we need this is to work around the root node
        having None parent, this way we can make root parent itself.
        """
        return self._parent or self

    @property
    def shart256(self):
        """
        A short sha256, useful for exposing enough of the hash to access the
        system, but not enough to fill a letter or make baby hashes.
        """
        return self.sha256[:12]

    @property
    def nchildren(self):
        """Number of children nodes"""
        return len(self.children)

    @property
    def depth(self):
        """Number of links between us an our root node"""
        raise Exception("TODO")

    @staticmethod
    def make_root():
        """
        Make a chain root node:
            * parent_id=NULL
            * a random sha256 by default
        """
        rand_hash = "{:064x}".format(random.getrandbits(256))
        return HashChain(parent_id=None, sha256=rand_hash, is_root=True)

    def make_child(self):
        """
        Make a new child instance.

        TODO: finalize the hashing policy and describe here; it needs to include
        a secret to prevent users from being able to predict hashes.
        """
        if self.id is None:
            raise RuntimeError(
                "Attempting to make child from a new instance that hasn't yet been assigned an id"
            )
        elif self.nchildren >= self.MAX_DEGREE:
            raise RuntimeError("Exceeded max number of children at this node")

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
