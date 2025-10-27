import os
from database import Product, Base
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import streamlit as st
import webbrowser


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
        
    # Main content
    session = Session()
    products = session.query(Product).all()
    
    if not products:
        st.info('No products added yet. Use the sidebar to add your first product.')
    else:
        for product in products:
            with st.container():
                display_product_detail(product)
    session.close()
        
        
# Function to add new product
def add_product():
    ''' Form to add a new product '''
    with st.form('add_product'):
        name = st.text_input('Product name')
        price = st.number_input('Your price', min_value=0)
        url = st.text_input('Product URL (optional)')
        
        if st.form_submit_button('Add product'):
            session = Session()
            product = Product(name=name, your_price=price, url=url)
            session.add(product)
            session.commit()
            session.close()
            st.success(f'Added product: {name}')
            return True
    return False


# Function to delete products 
def delete_product(product_id: str):
    ''' Delete a product and all its competitors '''
    session = Session()
    product = session.query(Product).filter_by(id=product_id).first()
    if product:
        session.delete(product)
        session.commit()
    session.close()


# Function to display product
def display_product_detail(product):
    ''' Display details for a single product '''
    st.subheader(product.name)
    cols = st.columns([1, 2])
    with cols[0]:
        st.metric(
            label='Your Price',
            value=f'{product.your_price:.2f}',
        )
        with cols[1]:
            col1, col2 = st.columns(2)
            with col1:
                if product.url:
                    st.button(
                        'Visit product',
                        key=f'visit_btn_{product.id}',
                        use_container_width=True,
                        on_click=lambda: webbrowser.open_new_tab(product.url),
                    )
                else:
                    st.text('No URL provided')
            with col2:
                st.button(
                    '🗑️ Delete',
                    key=f'delete_btn_{product.id}',
                    type='primary',
                    use_container_width=True,
                    on_click=lambda: delete_product(product.id),
                )
    

# Load env variables
load_dotenv()


# Databse setup
engine = create_engine(os.getenv('POSTGRES_URL'))
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# Run the app
if __name__ == '__main__':
    main()