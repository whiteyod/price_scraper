import os
from database import Product, Base, Competitor
from dotenv import load_dotenv
from scraper import scrape_competitor_product
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse
import time
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
                display_competitors(product)
                add_competitor_form(product, session)
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
    
    
# Function to add product's URL
def add_competitor_form(product, session):
    ''' Form to add a new competitor '''
    with st.expander('Add new competitor', expanded=False):
        with st.form(f'add_competitor_{product.id}'):
            competitor_url = st.text_input('🔗 Competitor product URL')
            col1, col2 = st.columns([3, 1])
            with col2:
                submit = st.form_submit_button(
                    'Add competitor',
                    use_container_width=True
                )
            if submit:
                # Add competitor to the database
                try:
                    with st.spinner('Fetching competitor data...'):
                        data = scrape_competitor_product(competitor_url)
                        competitor = Competitor(
                            product_id=product.id,
                            url=competitor_url,
                            name=data['name'],
                            current_price=data['price'],
                            image_url=data.get('image_url'),
                            last_checked=data['last_checked'],
                        )
                        session.add(competitor)
                        session.commit()
                        st.success('Competitor added successfully!')

                        # Refresh the page
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f'❌ Error adding competitor: {str(e)}')
                    

# Function to delete competitor
def delete_competitor(competitor_id: str):
    ''' Delete a competitor '''
    session = Session()
    competitor = session.query(Competitor).filter_by(id=competitor_id).first()
    if competitor:
        session.delete(competitor)
        session.commit()
    session.close()
    
    
# Function to display competitor details
def display_competitor_metrics(product, comp):
    ''' Display competitor price comparison metrics '''
    st.markdown(f'### # {urlparse(comp.url).netloc}')
    cols = st.columns([1, 2, 1, 1])
    # Calculate the price difference
    diff = ((comp.current_price - product.your_price) / product.your_price) * 100
    # Set price column with currency symbol
    with cols[0]:
        st.metric(
            label='💰 Competitor price',
            value=f'zł{comp.current_price:.2f}',
            delta=f'{diff:+.1f}%',
            delta_color='normal',
        )
    # Last checked time
    with cols[1]:
        st.markdown(f'**🕒 Checked:** {comp.last_checked.strftime('%Y-%m-%d %H:%M')}')
    # Button to visit competitor's webpage
    with cols[2]:
        st.button(
            'Visit product',
            key=f'visit_btn_{comp.id}',
            use_container_width=True,
            on_click=lambda: webbrowser.open_new_tab(comp.url),
        )   
    # Button to delete competitor
    with cols[3]:
        st.button(
            '🗑️',
            key=f'delete_comp_btn_{comp.id}',
            type='primary',
            use_container_width=True,
            on_click=lambda: delete_competitor(comp.id),
        )
        
        
# Function to display all competitors
def display_competitors(product):
    ''' Display all competitors for a product '''
    if product.competitors:
        with st.expander('Viev competitors', expanded=False):
            for comp in product.competitors:
                display_competitor_metrics(product, comp)
    else:
        st.info('No competitors added yet')
                    
# Load env variables
load_dotenv()


# Databse setup
engine = create_engine(os.getenv('POSTGRES_URL'))
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# Run the app
if __name__ == '__main__':
    main()