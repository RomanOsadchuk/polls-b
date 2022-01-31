# dependencies
# from .mongodb import QuestionsCollection as QuestionsStorage
# from .mongodb import ChoicesCollection as ChoicesStorage

from .postgres import QuestionsTable as QuestionsStorage
from .postgres import ChoicesTable as ChoicesStorage
