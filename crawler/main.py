import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from card_info import insert_card_info
from card_benefit import insert_benefits_info
from card_events import insert_card_events
from db.connection import connect_db

con = connect_db()
for idx in set(insert_card_info(con)):
    insert_benefits_info(con, idx)
    insert_card_events(con, idx)