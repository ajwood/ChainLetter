from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    Boolean,
    CheckConstraint,
    DateTime,
    func,
)
from sqlalchemy.orm import validates, relationship, backref

from . import db


class Letter(db.Model):
    __tablename__ = "letters"
    __table_args__ = (CheckConstraint("hashchain_id > veteran_id"),)

    id = Column(Integer, primary_key=True)
    hashchain_id = Column(
        Integer, ForeignKey("hashchain.id"), nullable=True, unique=True
    )
    ipaddress = Column(Text, nullable=False)
    username = Column(Text, nullable=False)
    home_address = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    veteran_id = Column(Integer, ForeignKey("hashchain.id"), nullable=True)
    flagged = Column(Boolean)
    reviewed = Column(Boolean)
    created_on = Column(DateTime(timezone=True), server_default=func.now())

    hc = relationship(
        "HashChain", backref=backref("letter", uselist=False), foreign_keys=hashchain_id
    )
    veteran = relationship("HashChain", foreign_keys=veteran_id)

    def __init__(
        self, /, hashchain_id, ipaddress, username, home_address, message, veteran_id
    ):
        """
        A letter contributed by a user in the chain. Should map 1:1 with the
        hashchain table, with the exception that there may be "unused" hashchain
        entries, for invitations that haven't been acted on.

        Paramters
        ---------
        hashchain_id
            The hashchain link with which this letter is associated
        ipaddress
            The ip address from which this letter was submitted
        username
            The name of the person who signs the letter (e.g., "andrew",
            "Andrew", "Andrew Wood")
        home_address
            The home location, identified by the submitter (e.g., "Canada",
            "Montreal", "Montreal, QC")
        message
            The main body content of the letter
        veteran_id
            If a user participates multiple times, they can note a hash they
            used for a previous submission, which can be used to collect their
            full set of letters, or identify loops in the hashchain.
        """
        self.hashchain_id = hashchain_id
        self.ipaddress = ipaddress
        self.username = username
        self.home_address = home_address
        self.message = message
        self.veteran_id = veteran_id

        # People are terrible, and there will surely be some ugly content show.
        # We provide a mechanism for users to anonymously flag offensive
        # content. Flagged content will be hidden from the front-end, and must
        # be reviewed by an admin, leading to one of the following resolutions:
        # a) content is fine, you wimps (someone may have misclicked): unflag
        #    and carry on
        # b) content is mostly fine, but parts need to be modified; pull out the
        #    bad bits, unflag and carry on
        # c) content is heinous: keep flagged
        #
        # Once reviewed, presumably the admin showed good judgement, so the
        # flagging mechanism is disabled from the front-end.
        self.flagged = False
        self.reviewed = False

    def get_veteran_letters(self):
        """
        Get all the letters associated with this veteran user, by following a
        chain or veteran relationships (if exists).
        """
        # Can probably use an itertools.from_chain for this
        cluster = set()
        raise Exception("TODO IMPLEMENT ME!")
