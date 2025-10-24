import streamlit as st


# Init function for app layout
def main():
    st.title('Price Monitor')
    st.markdown(
        '##### Compare product prices to competitors\' prices. \
         Input your product details and competitors\' URLs to get started'
    )
    st.markdown('### Tracked Products')
    st.markdown('---')
    
    # Sidebar for adding new products
    with st.sidebar:
        st.header('Add New Product')
        add_product()
        
        
# Function to add new product
def add_product():
    ''' Form to add a new product '''
    with st.form('add_product'):
        name = st.text_input('Product name')
        price = st.number_input('Your price', min_value=0)
        url = st.text_input('Product URL (optional)')
        
        if st.form_submit_button('Add product'):
            st.success(f'Added product: {name}')
            return True
    return False



# Run the app
if __name__ == '__main__':
    main()