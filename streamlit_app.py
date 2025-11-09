# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f"Customize Your Smoothie")
st.write(
  """Choose the Fruits you want in your custom smoothie).
  """
)

name_on_order = st.text_input('Name on Smoothie: ')
st.write('The name on the smoothie will be: ', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options")
#st.dataframe(data=my_dataframe, use_container_width=True)

fruit_names = my_dataframe.select(col("FRUIT_NAME")).collect()  # Replace "FRUIT_NAME" with your actual column name
ingredient_options = [row["FRUIT_NAME"] for row in fruit_names]

# Display in multiselect
ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=ingredient_options,
    max_selections=5
)
if ingredient_list:
    ingredients_string = ''
    for a in ingredient_list:
        ingredients_string+=a+ ' '

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width = True)
