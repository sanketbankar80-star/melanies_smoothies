import snowflake.connector
import streamlit as st

st.title(":cup_with_straw: Customise Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!"""
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

snowflake_secrets = st.secrets.get("connections", {}).get("snowflake") or st.secrets.get("snowflake")
if not snowflake_secrets:
    st.error(
        "Snowflake credentials were not found in Streamlit secrets. "
        "Add them under [connections.snowflake] or [snowflake] in secrets.toml."
    )
    st.stop()

@st.cache_resource
def init_snowflake_connection(credentials):
    return snowflake.connector.connect(
        account=credentials.get("account"),
        user=credentials.get("user"),
        password=credentials.get("password"),
        role=credentials.get("role"),
        warehouse=credentials.get("warehouse"),
        database=credentials.get("database"),
        schema=credentials.get("schema"),
        client_session_keep_alive=credentials.get("client_session_keep_alive", False),
    )

cnx = init_snowflake_connection(snowflake_secrets)

with cnx.cursor() as cursor:
    cursor.execute("SELECT fruit_name FROM smoothies.public.fruit_options")
    fruit_options = [row[0] for row in cursor.fetchall()]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5,
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    submit_order = st.button("Submit Order")
    if submit_order:
        insert_query = "INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES (%s, %s)"
        with cnx.cursor() as cursor:
            cursor.execute(insert_query, (ingredients_string, name_on_order))
        cnx.commit()
        st.success("Your Smoothie is ordered!", icon="✅")
        

