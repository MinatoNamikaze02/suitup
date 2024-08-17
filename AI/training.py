from pathlib import Path
import sys
current_dir = Path(__file__).parent
backend_dir = (current_dir / "..").resolve()
# Add the 'app' directory to sys.path
sys.path.append(str(backend_dir))

from vanna.openai.openai_chat import OpenAI_Chat
from vanna.vannadb.vannadb_vector import VannaDB_VectorStore

from . import documentation
from config import settings

class CMHQVanna(VannaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        model = settings.vanna_model_name
        api_key = settings.vanna_api_key
        VannaDB_VectorStore.__init__(self, vanna_model=model, vanna_api_key=api_key, config=config)
        OpenAI_Chat.__init__(self, config=config)
 
def init_vanna(model="gpt-3.5-turbo"):
    cmhq_analyst = CMHQVanna(config={'api_key': settings.open_ai_api_key, 'model': model})

    cmhq_analyst.connect_to_sqlite('jobs.db')

    return cmhq_analyst

if __name__ == "__main__":
    cmhq_analyst = init_vanna(model="gpt-3.5-turbo")

    command = "SELECT type, sql FROM sqlite_master WHERE sql is not null"

    # ddl training
    print("Training DDL...")
    df_ddl = cmhq_analyst.run_sql(command)

    for ddl in df_ddl['sql']:
        cmhq_analyst.train(ddl=ddl)

    # training documenation
    print("Training Documentation...")
    for doc in documentation.important_documentation:
        cmhq_analyst.train(documentation=doc)
    
