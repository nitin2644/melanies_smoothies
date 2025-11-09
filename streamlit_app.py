# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title("Customize Your Smoothie")
st.write("""Choose the fruits you want in your custom smoothie.""")

# Clean name input
name_on_order = st.text_input('Name on Smoothie:').strip()
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
ingredients_string = ''
for a in ingredient_list:
    # Clean each fruit name + join with single space and comma
    #clean_ingredients = [fruit.strip() for fruit in ingredient_list]
    ingredients_string += a + ' '
    for fruit_chosen in clean_ingredients:
        search_on_value = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0].strip()
        
        st.subheader(f"{fruit_chosen} Nutrition Information")
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on_value}")
        
        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.warning(f"No nutrition info for {fruit_chosen} (using: {search_on_value})")

    # SUPER CLEAN INSERT: No leading/trailing/double spaces
    clean_name = name_on_order.strip()

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
        VALUES ('{clean_ingredients}', '{clean_name}', FALSE)
    """

    submit = st.button('Submit Order')

    if submit:
        if not clean_name:
            st.warning("Please enter your name!")
        elif not clean_ingredients_final:
            st.warning("Please select at least one fruit!")
        else:
            try:
                session.sql(my_insert_stmt).collect()
                st.success(f"Your Smoothie is ordered, {clean_name}!")
            except Exception as e:
                st.error(f"Order failed: {str(e)}")
