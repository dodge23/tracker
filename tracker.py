import tkinter as tk
import requests
import json
import phonenumbers
from phonenumbers import carrier, geocoder
from tkinterweb import HtmlFrame  # Import HtmlFrame for displaying HTML content
import sqlite3

# Load cookies from cookies.json
def load_cookies():
    try:
        with open('cookies.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Cookies file not found.")
        return []

# Create or connect to a SQLite database
def create_connection():
    conn = sqlite3.connect('tracker_data.db')  # Change the database name if needed
    return conn

# Create tables if they do not exist
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Create table for tracking IP addresses
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ip_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        data TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create table for tracking phone numbers
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS phone_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT NOT NULL,
        data TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

# Function to save IP tracking data
def save_ip_tracking(ip, data):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ip_tracking (ip, data) VALUES (?, ?)", (ip, data))
    conn.commit()
    conn.close()

# Function to save phone tracking data
def save_phone_tracking(phone, data):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO phone_tracking (phone, data) VALUES (?, ?)", (phone, data))
    conn.commit()
    conn.close()

class TrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Tracker, Phone Tracker, and AI Chat")
        self.cookies = load_cookies()
        create_tables()  # Ensure tables are created

        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create result frame
        self.result_frame = tk.Frame(root, width=300)
        self.result_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Create scrollbar for the main frame
        self.main_scrollbar = tk.Scrollbar(self.main_frame)
        self.main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create UI Elements in main frame
        self.ip_label = tk.Label(self.main_frame, text="Your IP:")
        self.ip_label.pack(pady=(10, 0))

        self.track_ip_button = tk.Button(self.main_frame, text="Show My IP", command=self.show_my_ip)
        self.track_ip_button.pack(pady=(5, 10))

        self.ip_result_label = tk.Label(self.main_frame, text="")
        self.ip_result_label.pack()

        # IP Tracker using IPgeolocation API
        self.ip_info_label = tk.Label(self.main_frame, text="Enter IP to track:")
        self.ip_info_label.pack(pady=(10, 0))

        self.ip_entry = tk.Entry(self.main_frame, width=50)
        self.ip_entry.pack(pady=(5, 10))

        self.track_ip_info_button = tk.Button(self.main_frame, text="Track IP Info", command=self.track_ip_info)
        self.track_ip_info_button.pack(pady=(5, 10))

        # Create a text widget in the result frame
        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, bg="#f0f0f0", fg="black", height=30)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar for the result frame
        self.scrollbar = tk.Scrollbar(self.result_frame, command=self.result_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the text widget to use the scrollbar
        self.result_text.config(yscrollcommand=self.scrollbar.set)

        # Create buttons for phone tracking
        self.phone_label = tk.Label(self.main_frame, text="Enter Phone Number:")
        self.phone_label.pack(pady=(10, 0))

        self.phone_entry = tk.Entry(self.main_frame, width=50)
        self.phone_entry.pack(pady=(5, 10))

        self.track_phone_info_button = tk.Button(self.main_frame, text="Track Phone Info", command=self.phoneGW)
        self.track_phone_info_button.pack(pady=(5, 10))

        # Create a button to get the location on the map
        self.get_map_button = tk.Button(self.main_frame, text="Get Map", command=self.show_map)
        self.get_map_button.pack(pady=(5, 10))

        # Create an embedded map frame
        self.map_frame = HtmlFrame(self.main_frame, horizontal_scrollbar="auto")
        self.map_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Clear button to clear the results
        self.clear_button = tk.Button(self.main_frame, text="Clear Results", command=self.clear_results)
        self.clear_button.pack(pady=(5, 10))

        self.ip_data = None  # To store IP data for later use

    def show_my_ip(self):
        try:
            response = requests.get("https://api64.ipify.org/?format=json")
            if response.status_code == 200:
                ip_data = response.json()
                self.ip_result_label.config(text=f"Your IP: {ip_data['ip']}")
                self.result_text.delete('1.0', tk.END)  # Clear previous results
                self.result_text.insert(tk.END, f"Your IP: {ip_data['ip']}\n")
            else:
                self.ip_result_label.config(text="Failed to retrieve IP.")
        except Exception as e:
            self.ip_result_label.config(text=f"Error: {str(e)}")

    def track_ip_info(self):
        ip_address = self.ip_entry.get()
        if ip_address:
            self.get_ip_info(ip_address)
        else:
            self.result_text.delete('1.0', tk.END)  # Clear previous results
            self.result_text.insert(tk.END, "Please enter an IP address.\n")

    def get_ip_info(self, ip_address):
        try:
            # Use your actual IP Geolocation API token here
            response = requests.get(f"https://api.ipgeolocation.io/ipgeo?apiKey=ef5a151c7d264d96803fd37402e38fc6&ip={ip_address}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 200:
                ip_info = response.json()
                self.ip_data = ip_info  # Store IP info for later use
                latitude = ip_info.get('latitude')
                longitude = ip_info.get('longitude')

                # Save IP info to the database
                save_ip_tracking(ip_address, json.dumps(ip_info))

                lat_long_info = f"Latitude: {latitude}, Longitude: {longitude}"

                # Display the results
                self.result_text.delete('1.0', tk.END)  # Clear previous results
                self.result_text.insert(tk.END, f"IP Info: {json.dumps(ip_info, indent=2)}\n{lat_long_info}\n")

            else:
                error_message = response.json().get('message', 'Failed to retrieve IP information.')
                self.result_text.delete('1.0', tk.END)  # Clear previous results
                self.result_text.insert(tk.END, f"Error: {error_message}\n")
        except Exception as e:
            self.result_text.delete('1.0', tk.END)  # Clear previous results
            self.result_text.insert(tk.END, f"Error: {str(e)}\n")

    def show_map(self):
        if self.ip_data:
            latitude = self.ip_data.get('latitude')
            longitude = self.ip_data.get('longitude')
            if latitude and longitude:
                map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={longitude-0.01},{latitude-0.01},{longitude+0.01},{latitude+0.01}&layer=mapnik&marker={latitude},{longitude}"
                self.map_frame.set_html(f'<iframe width="100%" height="500" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="{map_url}"></iframe>')
            else:
                self.result_text.delete('1.0', tk.END)
                self.result_text.insert(tk.END, "Latitude and Longitude not available.\n")
        else:
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, "Please track an IP address first.\n")

    def phoneGW(self):
        user_phone = self.phone_entry.get()
        default_region = "ID"  # Default region Indonesia

        try:
            parsed_number = phonenumbers.parse(user_phone, default_region)
            region_code = phonenumbers.region_code_for_number(parsed_number)
            jenis_provider = carrier.name_for_number(parsed_number, "en")
            location = geocoder.description_for_number(parsed_number, "en")

            phone_info = f"Number: {parsed_number}\nRegion Code: {region_code}\nProvider: {jenis_provider}\nLocation: {location}"

            # Save phone info to the database
            save_phone_tracking(user_phone, phone_info)

            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, phone_info + "\n")

        except phonenumbers.phonenumberutil.NumberParseException as e:
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, f"Error parsing phone number: {str(e)}\n")

    def clear_results(self):
        self.result_text.delete('1.0', tk.END)  # Clear the text widget
        self.ip_result_label.config(text="")  # Clear IP label
        self.ip_entry.delete(0, tk.END)  # Clear IP entry
        self.phone_entry.delete(0, tk.END)  # Clear phone entry
        self.map_frame.set_html("")  # Clear the map frame

if __name__ == "__main__":
    root = tk.Tk()
    app = TrackerApp(root)
    root.mainloop()
