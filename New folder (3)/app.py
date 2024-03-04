from flask import Flask, render_template, jsonify, request, redirect, session
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import logging
import mysql.connector
import xlrd
# import seaborn as sns

app = Flask(__name__)
app.debug = True
logging.basicConfig(level=logging.DEBUG)

# Establish the database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Harsh@7987",
    database="userdetails"
)

# Create a cursor object
mycursor = db.cursor()


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = 'static'


os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Generate a random secret key
secret_key = os.urandom(24).hex()
app.secret_key = secret_key


# For login page 
# Replace with your actual credentials
VALID_CREDENTIALS = {'username': 'password'}


#  To upload the files 
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return 'No file uploaded'

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return 'No file selected'

        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename) # type: ignore
        file.save(file_path)

        # Store the file path in a session variable
        session['uploaded_file_path'] = file_path  

        # Get the selected graph type from the form
        graph_type = request.form.get('graph_type')  

        if graph_type == 'none':
            return 'Please select a valid graph type'

        try:
            # Generate the requested graph based on the uploaded file and graph type
            generate_graph(file_path, graph_type)
            return 'File uploaded and graph generated successfully'
        except Exception as e:
            return f'Error generating graph: {str(e)}'

    return render_template('upload.html')


# To choose the graph type and generate graph
def generate_graph(file_path, graph_type):
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == '.txt':
        # Process text file
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Remove the header line
        lines = lines[1:]

        # Extract the data from each line
        data = [line.strip().split() for line in data] # type: ignore

        # Create a DataFrame with the extracted data
        df = pd.DataFrame(data, columns=['Column_1', 'Column_2'])

    elif file_ext == '.csv' or file_ext == '.xlsx' or file_ext == '.xls' or file_ext == 'xlrd':
        # Process CSV or Excel file
        data = pd.read_csv(file_path) if file_ext == '.csv' else pd.read_excel(file_path)
        columns = data.columns.tolist()

        if 'x' in columns and 'y' in columns:
            # If the file has 'x' and 'y' columns, use them for generating the graph
            x = data['x']
            y = data['y']
            student_names = ['x'] * len(x)  # Dummy student names for generic x and y columns
        elif 'Name' in columns and 'Population' in columns:
            # If the file has 'Name' and 'Population' columns, use them for generating the graph
            x = data['Name']
            y = data['Population'].astype(float)
            student_names = data['Name'].tolist()  # Use student names from the 'Name' column
        elif 'total_bill' in columns and 'tip' in columns:
            x = data['total_bill']
            y = data['tip']
            student_names = ['Bill'] * len(x)  # Dummy student names for generic x and y columns
        elif 'District name' in columns and 'Population' in columns:
            # If the file has 'Name' and 'Population' columns, use them for generating the graph
            x = data['District name']
            y = data['Population'].astype(float)
            student_names = data['District name'].tolist()  # Use student names from the 'Name' column
        elif 'Name' in columns and 'Marks' in columns:
            # If the file has 'Name' and 'Marks' columns, group the data by 'Name' and 'Subject'
            # and calculate the average marks for each subject per student
            numeric_columns = ['Marks']
            if data[numeric_columns].applymap(lambda x: isinstance(x, (int, float))).all().all(): #type:ignore
                grouped_data = data.groupby(['Name', 'Subject'])[numeric_columns].mean().reset_index()
                x = grouped_data['Subject']
                y = grouped_data['Marks']
                student_names = grouped_data['Name'].tolist()  # Use student names from the 'Name' column
            else:
                raise ValueError("Invalid column type in 'Marks' column")
        elif 'Category' in columns and 'Value' in columns:
            # If the file has 'Category' and 'Value' columns, use them for generating the graph
            x = data['Category']
            y = data['Value'].astype(float)
            student_names = ['Student'] * len(x)  # Dummy student names for generic x and y columns
        elif 'Hobby' in columns and 'No. of student' in columns:
            # If the file has 'Hobby' and 'No. of student' columns, use them for generating the graph
            x = data['Hobby']
            y = data['No. of student'].astype(float)
            if graph_type == 'pie':
                student_names = x.tolist()  # Use hobby names as student names
            else:
                student_names = [''] * len(x)  # Dummy student names for other graph types
        elif 'Name' in columns and 'E-mail' in columns and 'Message' in columns:
            # Skip the first row (column headers)
            data = data[1:]
            # Extract the data for the graph
            x = range(len(data))  # Use a range of values as x-coordinates
            y = []  # Empty y-coordinates
            student_names = data['Name'].tolist()  # Use student names from the 'Name' column
        else:
            raise ValueError("Unsupported file format in the uploaded file")  
    else:
        raise ValueError("Unsupported file extension")
    
    
    # Calculate the range of data on the y-axis
    y_range = max(y) - min(y)

    # Set a threshold for the number of data points that can fit in the graph without resizing
    data_points_threshold = 10  # You can adjust this threshold as per your preference

    # Check if the data points exceed the threshold before adjusting the figure size
    if len(y) > data_points_threshold:
        # Calculate the width of the figure based on the number of data points (adjust the factor as needed)
        width_factor = 0.2  # You can adjust this factor as per your preference
        figure_width = len(x) * width_factor
        figure_height = 6  # You can adjust the height as per your preference

        # Generate the requested graph with the adjusted figure size
        plt.figure(figsize=(figure_width, figure_height))

    # Generate the requested graph based on the graph_type
    if graph_type == 'line':
        plt.plot(x, y)
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Line Graph')
        for i in range(len(x)):
           plt.text(i + 1, y[i], student_names[i], ha='center', va='bottom', rotation='vertical')
        plt.xticks(rotation='vertical')  # Rotate the x-axis tick labels vertically
    elif graph_type == 'bar':
        plt.bar(x, y)
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Bar Graph')
        for i in range(len(x)):
            plt.text(i + 1, y[i], student_names[i], ha='center',  rotation='vertical')
            plt.xticks(rotation='vertical')  # Rotate the x-axis tick labels vertically
    elif graph_type == 'scatter':
        plt.scatter(x, y)
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Scatter Plot')
        for i in range(len(x)):
            plt.text(i + 1, y[i], student_names[i], ha='center', va='bottom', rotation='vertical')
        plt.xticks(rotation='vertical')  # Rotate the x-axis tick labels vertically
    elif graph_type == 'histogram':
        plt.hist(y, bins='auto')
        plt.title('Histogram')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        for i in range(len(x)):
            plt.text(y[i], 0, student_names[i], ha='center', va='bottom', rotation='vertical')
        plt.xticks(rotation='vertical')  # Rotate the x-axis tick labels vertically
    elif graph_type == 'boxplot':
        if isinstance(y[0], (int, float)):
            plt.boxplot(y)
        else:
            raise ValueError(f'Invalid column type: {type(y[0])}')
        plt.title('Box Plot')
        plt.ylabel('Value')
        for i in range(len(x)):
            plt.text(i + 1, y[i], student_names[i], ha='center', va='bottom', rotation='vertical')
            plt.xticks(rotation='vertical')  # Rotate the x-axis tick labels vertically
    elif graph_type == 'pie':
        if isinstance(y[0], (int, float)):
            plt.pie(y, labels=x, autopct='%1.1f%%') # type: ignore
        else:
            raise ValueError(f'Invalid column type: {type(y[0])}')
        plt.title('Pie Chart')
    elif graph_type == 'area':
        if isinstance(y[0], (int, float)):
            plt.fill_between(range(len(x)), y, color='skyblue')
            plt.plot(range(len(x)), y, color='blue')
            plt.xlabel('X-axis')
            plt.ylabel('Y-axis')
            plt.title('Area Graph')
            for i in range(len(x)):
                plt.text(i + 1, y[i], student_names[i], ha='center', va='bottom', rotation='vertical')
            plt.xticks(rotation='vertical')  # Rotate the x-axis tick labels vertically
        else:
            raise ValueError(f'Invalid column type: {type(y[0])}')
    else:
        raise ValueError(f'Invalid graph type: {graph_type}')

    plt.savefig('static/graph.png')  # Save the graph image
    plt.close()


# To show the data frame
def show_dataframe():
    print("Inside show_dataframe function")  # Add this print statement

    uploaded_file_path = session.get('uploaded_file_path')
    if not uploaded_file_path:
        return 'No file uploaded'

    file_ext = os.path.splitext(uploaded_file_path)[1].lower()
    print("File extension:", file_ext)

    if file_ext == '.txt':
        # Process text file
        with open(uploaded_file_path, 'r') as f:
            data = f.readlines()

        # Extract the data from each line
        data = [line.strip().split() for line in data]

        # Extract the columns (assuming there are more than two values per line)
        columns = list(zip(*data))

        # Create a DataFrame with the extracted columns
        df = pd.DataFrame(columns)

        # If you want, you can rename the columns
        df.columns = [f'Column_{i}' for i in range(len(columns))]

    elif file_ext in ['.csv', '.xlsx', '.xls']:
        # Process CSV, Excel, or other supported file types
        print("Processing CSV or Excel file")  # Add this print statement
        df = pd.read_csv(uploaded_file_path) if file_ext == '.csv' else pd.read_excel(uploaded_file_path)
    else:
        print("Unsupported file format")  # Add this print statement
        return 'Unsupported file format'
    
    print("DataFrame:", df)

    return render_template('harsh.html', dataframe=df.to_html(index=False))

def render_dataframe(df):
    return df.to_html(index=False)


# To access webpage
@app.route('/harsh')
def harsh():
    # Initialize with None
    rendered_table = None  
    
    # Check if the uploaded file path is stored in the session
    uploaded_file_path = session.get('uploaded_file_path')
    if uploaded_file_path:
        # Process the uploaded file to create a DataFrame
        file_ext = os.path.splitext(uploaded_file_path)[1].lower()

        if file_ext == '.csv' or file_ext == '.xlsx' or file_ext == '.xls':
            # Process CSV, Excel, or other supported file types
            df = pd.read_csv(uploaded_file_path) if file_ext == '.csv' else pd.read_excel(uploaded_file_path)
            # Use the DataFrame for rendering the table
            rendered_table = render_dataframe(df)  # Convert DataFrame to HTML
            # Set mtcars to the uploaded DataFrame
            global mtcars
            mtcars = df.copy()
        elif file_ext == '.txt':
            # Process text file
            with open(uploaded_file_path, 'r') as f:
                data = f.readlines()
            # Extract the data from each line
            data = [line.strip().split() for line in data]
            # Extract the columns (assuming there are more than two values per line)
            columns = list(zip(*data))
            # Create a DataFrame with the extracted columns
            df = pd.DataFrame(columns)
            # If you want, you can rename the columns
            df.columns = [f'Column_{i}' for i in range(len(columns))]
        else:
            return 'Unsupported file format'        
    return render_template('harsh.html', dataframe=rendered_table)

# To access homepage
@app.route('/')
def index():
    return render_template('index.html')

# To access about us page
@app.route('/about')
def about():
    return render_template('about.html')

# To access why page
@app.route('/Why')
def Why():
    return render_template('Why.html')


# to Fill the feedback form
@app.route('/save_data', methods=['POST'])
def save_data():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    mycursor.execute("CREATE TABLE IF NOT EXISTS userdata(name varchar(25), email varchar(255), message varchar(255))")

    mycursor.execute("INSERT INTO userdata(name, email, message) VALUES (%s, %s, %s)", (name, email, message))

    db.commit()

    return redirect('/about')


# To login/signup form
@app.route('/login', methods=['POST', 'GET'])  # Show login form for GET requests
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if VALID_CREDENTIALS.get(username) == password:
            return 'Login successful'
        else:
            return 'Login failed'

    return render_template('login.html')  # Allow both POST and GET for login
    
    
@app.route('/register', methods=['POST', 'GET'])  # Allow both POST and GET for registration
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return 'Passwords do not match'

        if username in VALID_CREDENTIALS:
            return 'Username already exists'
        
        # Add the new username and password to the VALID_CREDENTIALS dictionary
        VALID_CREDENTIALS[username] = password

        return 'Registration successful'

    return render_template('register.html')  # Show registration form for GET requests


if __name__ == '__main__':
    app.run(debug=True)