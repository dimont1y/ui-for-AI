import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
COINMARKETCAP_API_KEY = os.environ.get("COINMARKETCAP_API_KEY")
ETHERSCAN_API_KEY=os.environ.get("ETHERSCAN_API_KEY")
BSCSCAN_API_KEY=os.environ.get("BSCSCAN_API_KEY")
SOLSCAN_API_KEY=os.environ.get("SOLSCAN_API_KEY")