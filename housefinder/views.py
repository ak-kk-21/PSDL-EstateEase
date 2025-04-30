from django.shortcuts import render,redirect

# Create your views here.
import os
import mysql.connector
from django.contrib import messages
import pandas as pd 
import joblib


def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Basic@123',
        database='estate'
        
    )

#Very first page which you will see after hitting URL
def home(request):
    return render(request,'home.html')

#login view
def login_user(request):
    if request.method=='POST':
        uname=request.POST['user_name']
        pwd=request.POST['password']

        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM USER WHERE user_name=%s AND PASSWORD=%s", (uname, pwd))
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect('main_menu')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request,'login.html')

#register view
def register(request):
    if request.method=='POST':
        uname = request.POST['user_name']
        email = request.POST['email']
        phone = request.POST['phoneno']
        password = request.POST['password']

        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("INSERT INTO USER(USER_NAME, EMAIL, PHONENO, PASSWORD) VALUES (%s, %s, %s, %s)",
                       (uname, email, phone, password))
        
        conn.commit()
        conn.close()

        return redirect('main_menu')
    
    return render(request,'register.html')
def find_houses(request):
    houses = None
    form_submitted = False
    locations = []

    dataset_path = os.path.join('housefinder', 'Mumbai_updated_realistic.csv')
    df = pd.read_csv(dataset_path)

    df['Location'] = df['Location'].astype(str).str.strip()
    df['Area'] = df['Area'].astype(str).str.strip()

    locations = sorted(df['Location'].unique())

    if request.method == 'POST':
        form_submitted = True
        min_budget = int(request.POST.get('min_budget'))
        max_budget = int(request.POST.get('max_budget'))
        min_area = int(request.POST.get('min_area'))
        max_area = int(request.POST.get('max_area'))
        selected_location = request.POST.get('location') 
        selected_location = selected_location.replace('_', ' ').title()

        sort_option = request.POST.get('sort_option')  # new: get the sort option

        # Filter the houses
        filtered = df[
            (df['Price'] >= min_budget) &
            (df['Price'] <= max_budget) &
            (df['Area'].astype(float) >= min_area) &
            (df['Area'].astype(float) <= max_area) &
            (df['Location'] == selected_location)
        ][['Location', 'Society', 'Area', 'Price']]

        if not filtered.empty:
            # If a sort option was selected, sort accordingly
            if sort_option:
                if sort_option == 'price_low_high':
                    filtered = filtered.sort_values(by='Price', ascending=True)
                elif sort_option == 'price_high_low':
                    filtered = filtered.sort_values(by='Price', ascending=False)
                elif sort_option == 'area_low_high':
                    filtered = filtered.sort_values(by='Area', ascending=True, key=lambda x: x.astype(float))
                elif sort_option == 'area_high_low':
                    filtered = filtered.sort_values(by='Area', ascending=False, key=lambda x: x.astype(float))

            houses = filtered.to_dict(orient='records')
        else:
            houses = None

    selected_location1 = selected_location.replace('_', ' ').title() if 'selected_location' in locals() else ''

    return render(request, 'find_houses.html', {
        'houses': houses,
        'form_submitted': form_submitted,
        'locations': locations,
        'selected_location': selected_location1,
    })


# Load the pre-trained model
model_data = joblib.load(r"housefinder\ml models\random_forest_model.pkl")
model = model_data['model']
model_columns = model_data['columns']

def predict_price(request):
    if request.method == 'POST':
        # Get user inputs for area range and amenities
        location_raw = request.POST['location']
        location = location_raw.strip().title()

        loc_col = f"Location_{location}"
        if loc_col not in model_columns:
            # Friendly message for user
            from django.contrib import messages
            messages.warning(request,
            f"Sorry, we don’t have data for '{location}'. "
            "Results may be less accurate."
        )
        #society = request.POST['society']
        min_area = float(request.POST['min_area'])  # minimum area
        max_area = float(request.POST['max_area'])  # maximum area
        bedrooms = int(request.POST['bedrooms'])

        # Features that are amenities (binary 0/1)
        resale = int(request.POST.get('resale', 0))
        gym = int(request.POST.get('gym', 0))
        pool = int(request.POST.get('pool', 0))
        garden = int(request.POST.get('garden', 0))
        track = int(request.POST.get('track', 0))
        mall = int(request.POST.get('mall', 0))
        club = int(request.POST.get('club', 0))
        school = int(request.POST.get('school', 0))
        parking = int(request.POST.get('parking', 0))
        hospital = int(request.POST.get('hospital', 0))
        lift = int(request.POST.get('lift', 0))
        def build_features(area_value):
            # start with all zeros
            feature_dict = {col: 0 for col in model_columns}

            # fill values
            feature_dict['Area'] = area_value
            feature_dict['No. of Bedrooms'] = bedrooms
            feature_dict['Resale'] = resale
            feature_dict['Gymnasium'] = gym
            feature_dict['SwimmingPool'] = pool
            feature_dict['LandscapedGardens'] = garden
            feature_dict['JoggingTrack'] = track
            feature_dict['ShoppingMall'] = mall
            feature_dict['ClubHouse'] = club
            feature_dict['School'] = school
            feature_dict['CarParking'] = parking
            feature_dict['Hospital'] = hospital
            feature_dict['LiftAvailable'] = lift

            # set one-hot location column
            loc_col = f'Location_{location}'
            if loc_col in feature_dict:
                feature_dict[loc_col] = 1
            else:
                print(f"⚠ Warning: location {location} not recognized in training data.")

            return feature_dict
        
        # --- Create two inputs: one for min_area and one for max_area
        features_min_area = build_features(min_area)
        features_max_area = build_features(max_area)

        # Create dataframe with 2 rows: min_area and max_area
        df = pd.DataFrame([features_min_area, features_max_area], columns=model_columns)

        # Prediction
        preds = model.predict(df)

        min_price = round(preds[0], -3)  # nearest 1000
        max_price = round(preds[1], -3)

        # Display price range
        return render(request, 'predict_price_result.html', {
            'predicted_price_min_area': min_price,
            'predicted_price_max_area': max_price
        })

    # If GET request, just show the form
    return render(request, 'predict_price_form.html')

def main_menu(request):
    return render(request, 'main_menu.html')





#Home page of our platform
def main_menu(request):
    return render(request, 'main_menu.html')