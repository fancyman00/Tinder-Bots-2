from match.database.crud import MatchCRUD


match_crud = MatchCRUD()

async def get_match_crud():
    return match_crud