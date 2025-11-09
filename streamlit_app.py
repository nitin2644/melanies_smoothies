# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title("Customize Your Smoothie")
st.write("""Choose the fruits you want in your custom smoothie.""")

name_on_order = st.text_input('Name on Smoothie:')
if name_on_order:
    st.write('The name on your smoothie will be:', name_on_order)

# Get session
session = st.connection("snowflake").session()

# Load fruit data
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()
ingredient_options = pd_df['FRUIT_NAME'].tolist()

# Multiselect
ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=ingredient_options,
    max_selections=5
)

if ingredient_list:
    ingredients_string = ','.join(ingredient_list)

    for fruit_chosen in ingredient_list:
        search_on_value = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(f"https://fruityvice.com/api/fruit/{search_on_value}")
        if response.status_code == 200:
            fv_data = response.json()
            st.dataframe(fv_data, use_container_width=True)
        else:
            st.error(f"API error for {search_on_value}: {response.status_code}")

    # CORRECT WAY: Use .format() with literal values (safe in Streamlit-in-Snowflake)
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
        VALUES ('{ingredients_string}', '{name_on_order}', FALSE)
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if not name_on_order.strip():
            st.warning("Please enter your name!")
        elif not ingredient_list:
            st.warning("Please select at least one fruit!")
        else:
            try:
                session.sql(my_insert_stmt).collect()
                st.success(f"Your Smoothie is ordered, {name_on_order}! Well done!")
                st.balloons()
            except Exception as e:
                st.error(f"Order failed: {str(e)}")
