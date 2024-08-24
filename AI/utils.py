from .training import init_vanna

vn = init_vanna()

async def gen_query(human_query: str, model: str = "gpt-3.5-turbo"):
    vn.config['model'] = model
    sql_query = vn.generate_sql(human_query, allow_llm_to_see_data=True)
    return sql_query

async def execute_query(query, model: str = "gpt-3.5-turbo"):
    try:
        vn.config['model'] = model
        df = vn.run_sql(query)
    except Exception as e:
        return query, True
    
    return df, False
