import tkinter as tk
import requests
import json
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import webbrowser

# Load cookies from cookies.json
def load_cookies():
    try:
        with open('cookies.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Cookies file not found.")
        return []

class TrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Tracker, Phone Tracker, and AI Chat")
        self.cookies = load_cookies()

        # Create UI Elements
        self.ip_label = tk.Label(root, text="Your IP:")
        self.ip_label.pack()

        self.track_ip_button = tk.Button(root, text="Show My IP", command=self.show_my_ip)
        self.track_ip_button.pack()

        self.ip_result_label = tk.Label(root, text="")
        self.ip_result_label.pack()

        # Phone Tracker
        self.phone_label = tk.Label(root, text="Enter Phone Number to Track:")
        self.phone_label.pack()

        self.phone_entry = tk.Entry(root, width=50)
        self.phone_entry.pack()

        self.track_phone_button = tk.Button(root, text="Track Phone", command=self.phoneGW)
        self.track_phone_button.pack()

        self.phone_result_label = tk.Label(root, text="")
        self.phone_result_label.pack()

        # IP Tracker using IPgeolocation API
        self.ip_info_label = tk.Label(root, text="Enter IP to track:")
        self.ip_info_label.pack()

        self.ip_entry = tk.Entry(root, width=50)
        self.ip_entry.pack()

        self.track_ip_info_button = tk.Button(root, text="Track IP Info", command=self.track_ip_info)
        self.track_ip_info_button.pack()

        self.track_info_result_label = tk.Label(root, text="")
        self.track_info_result_label.pack()

        self.map_button = tk.Button(root, text="Show Map", command=self.show_map, state=tk.DISABLED)
        self.map_button.pack()

    def show_my_ip(self):
        try:
            response = requests.get("https://api64.ipify.org/?format=json")
            if response.status_code == 200:
                ip_data = response.json()
                self.ip_result_label.config(text=f"Your IP: {ip_data['ip']}")
            else:
                self.ip_result_label.config(text="Failed to retrieve IP.")
        except Exception as e:
            self.ip_result_label.config(text=f"Error: {str(e)}")

    def track_ip_info(self):
        ip_address = self.ip_entry.get()
        if ip_address:
            self.get_ip_info(ip_address)
        else:
            self.track_info_result_label.config(text="Please enter an IP address.")

    def get_ip_info(self, ip_address):
        try:
            # Use your actual IP Geolocation API token here
            response = requests.get(f"https://api.ipgeolocation.io/ipgeo?apiKey=ef5a151c7d264d96803fd37402e38fc6&ip={ip_address}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 200:
                ip_info = response.json()
                latitude = ip_info.get('latitude')
                longitude = ip_info.get('longitude')

                self.track_info_result_label.config(text=json.dumps(ip_info, indent=2))
                self.map_button.config(state=tk.NORMAL)
                self.latitude = latitude
                self.longitude = longitude

                # Display latitude and longitude
                lat_long_info = f"Latitude: {latitude}, Longitude: {longitude}"
                self.track_info_result_label.config(text=f"{self.track_info_result_label['text']}\n{lat_long_info}")

                # Automatically show the map
                self.show_map()
            else:
                error_message = response.json().get('message', 'Failed to retrieve IP information.')
                self.track_info_result_label.config(text=f"Error: {error_message}")
        except Exception as e:
            self.track_info_result_label.config(text=f"Error: {str(e)}")

    def show_map(self):
        if hasattr(self, 'latitude') and hasattr(self, 'longitude'):
            map_url = f"https://www.openstreetmap.org/#map=15/{self.latitude}/{self.longitude}"
            webbrowser.open(map_url)

    def phoneGW(self):
        user_phone = self.phone_entry.get()
        default_region = "ID"  # Default region Indonesia

        try:
            parsed_number = phonenumbers.parse(user_phone, default_region)
            region_code = phonenumbers.region_code_for_number(parsed_number)
            jenis_provider = carrier.name_for_number(parsed_number, "en")
            location = geocoder.description_for_number(parsed_number, "id")
            is_valid_number = phonenumbers.is_valid_number(parsed_number)
            is_possible_number = phonenumbers.is_possible_number(parsed_number)
            formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            formatted_number_for_mobile = phonenumbers.format_number_for_mobile_dialing(parsed_number, default_region, with_formatting=True)
            number_type = phonenumbers.number_type(parsed_number)
            timezone1 = timezone.time_zones_for_number(parsed_number)
            timezoneF = ', '.join(timezone1)

            result = f"""
            ========== SHOW INFORMATION PHONE NUMBERS ==========  
            Location             : {location}
            Region Code          : {region_code}
            Timezone             : {timezoneF}
            Operator             : {jenis_provider}
            Valid number         : {is_valid_number}
            Possible number      : {is_possible_number}
            International format : {formatted_number}
            Mobile format        : {formatted_number_for_mobile}
            Original number      : {parsed_number.national_number}
            E.164 format         : {phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)}
            Country code         : {parsed_number.country_code}
            Local number         : {parsed_number.national_number}
            """

            if number_type == phonenumbers.PhoneNumberType.MOBILE:
                result += "Type                 : This is a mobile number"
            elif number_type == phonenumbers.PhoneNumberType.FIXED_LINE:
                result += "Type                 : This is a fixed-line number"
            else:
                result += "Type                 : This is another type of number"

            self.phone_result_label.config(text=result)
        except phonenumbers.NumberParseException:
            self.phone_result_label.config(text="Invalid phone number format.")
        except Exception as e:
            self.phone_result_label.config(text=f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrackerApp(root)
    root.mainloop()
