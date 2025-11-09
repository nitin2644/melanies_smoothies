# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title("Customize Your Smoothie 🥤")
st.write("""Choose the fruits you want in your custom smoothie.""")

name_on_order = st.text_input('Name on Smoothie:')
if name_on_order:
    st.write('The name on your smoothie will be:', name_on_order)

# Get Snowflake session
session = st.connection("snowflake").session()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Extract clean list of display names
ingredient_options = pd_df['FRUIT_NAME'].tolist()

# SINGLE multiselect (fixed duplicate error)
ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=ingredient_options,
    max_selections=5
)

if ingredient_list:
    ingredients_string = ', '.join(ingredient_list)

    for fruit_chosen in ingredient_list:
        # Get correct search term (e.g., "Apples" → "Apple")
        search_on_value = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.write(f"**{fruit_chosen}** → searching as: **{search_on_value}**")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fixed API URL (use fruityvice.com, not your domain)
        response = requests.get(f"https://fruityvice.com/api/fruit/{search_on_value}")
        
        if response.status_code == 200:
            fv_data = response.json()
            fv_df = pd.json_normalize(fv_data)
            st.dataframe(fv_data, use_container_width=True)
        else:
            st.error(f"Could not fetch data for {search_on_value}")

    # Build safe insert statement
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
        VALUES (%s, %s, FALSE)
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if name_on_order.strip() == "":
            st.warning("Please enter your name!")
        elif not ingredient_list:
            st.warning("Please select at least one fruit!")
        else:
            try:
                session.sql(my_insert_stmt, params=[ingredients_string, name_on_order]).collect()
                st.success(f"Your Smoothie is ordered, {name_on_order}! ✅", icon="🥤")
            except Exception as e:
                st.error(f"Order failed: {e}")
