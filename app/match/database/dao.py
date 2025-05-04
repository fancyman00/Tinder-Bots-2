from match.database.models.match import Match
from base.database.dao.base import BaseDAO

class MatchDAO(BaseDAO):
    model = Match