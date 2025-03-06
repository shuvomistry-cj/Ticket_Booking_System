import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
from PIL import Image, ImageTk
import io
import base64
import random
import datetime

# Database setup
def setup_database():
    conn = sqlite3.connect('movie_booking.db')
    cursor = conn.cursor()
    
    # Create Movies table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        language TEXT,
        duration TEXT,
        release_date TEXT,
        genre TEXT,
        total_seats INTEGER,
        available_seats INTEGER,
        price REAL,
        image BLOB
    )
    ''')
    
    # Create Bookings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY,
        movie_id INTEGER,
        customer_name TEXT,
        phone TEXT,
        email TEXT,
        seats TEXT,
        total_amount REAL,
        booking_date TEXT,
        FOREIGN KEY (movie_id) REFERENCES movies (id)
    )
    ''')
    
    # Create Admin table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')
    
    # Insert default admin if not exists
    cursor.execute("SELECT * FROM admin WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('admin', 'admin123'))
    
    # Insert sample movies if table is empty
    cursor.execute("SELECT COUNT(*) FROM movies")
    if cursor.fetchone()[0] == 0:
        sample_movies = [
            ('Avengers: Endgame', 'After the devastating events of Infinity War, the universe is in ruins. With the help of remaining allies, the Avengers assemble once more to reverse Thanos\' actions and restore balance to the universe.', 'English', '3h 1m', '2019-04-26', 'Action, Adventure, Drama', 100, 100, 12.99, None),
            ('The Lion King', 'After the murder of his father, a young lion prince flees his kingdom only to learn the true meaning of responsibility and bravery.', 'English', '1h 58m', '2019-07-19', 'Animation, Adventure, Drama', 100, 100, 9.99, None),
            ('Joker', 'In Gotham City, mentally troubled comedian Arthur Fleck is disregarded and mistreated by society. He then embarks on a downward spiral of revolution and bloody crime. This path brings him face-to-face with his alter-ego: the Joker.', 'English', '2h 2m', '2019-10-04', 'Crime, Drama, Thriller', 100, 100, 10.99, None),
            ('Parasite', 'Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.', 'Korean', '2h 12m', '2019-10-11', 'Comedy, Drama, Thriller', 100, 100, 11.99, None),
        ]
        cursor.executemany("INSERT INTO movies (title, description, language, duration, release_date, genre, total_seats, available_seats, price, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sample_movies)
    
    conn.commit()
    conn.close()

# Main Application
class MovieTicketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Ticket Booking System")
        self.root.geometry("1000x650")
        self.root.configure(bg="#1a1a1a")  # Dark theme
        
        self.setup_styles()
        self.create_widgets()
        self.show_movies_page()
    
    def setup_styles(self):
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button style
        style.configure('TButton', font=('Helvetica', 12), background='#3498db', foreground='#ffffff')
        style.map('TButton', background=[('active', '#2980b9')])
        
        # Configure frame style
        style.configure('TFrame', background='#1a1a1a')
        
        # Configure label style
        style.configure('TLabel', background='#1a1a1a', foreground='#ffffff', font=('Helvetica', 12))
        
        # Configure movie card style
        style.configure('Card.TFrame', background='#2c3e50', borderwidth=1, relief='raised')
        
        # Configure heading style
        style.configure('Heading.TLabel', font=('Helvetica', 18, 'bold'), background='#1a1a1a', foreground='#3498db')
        
        # Configure entry style
        style.configure('TEntry', font=('Helvetica', 12))
    
    def create_widgets(self):
        # Main Frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header Frame
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=10)
        
        # App Title
        self.title_label = ttk.Label(self.header_frame, text="Movie Ticket Booking System", style='Heading.TLabel', font=('Helvetica', 24, 'bold'))
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Navigation Buttons
        self.nav_frame = ttk.Frame(self.header_frame)
        self.nav_frame.pack(side=tk.RIGHT)
        
        self.home_btn = ttk.Button(self.nav_frame, text="Home", command=self.show_movies_page)
        self.home_btn.pack(side=tk.LEFT, padx=5)
        
        self.admin_btn = ttk.Button(self.nav_frame, text="Admin Portal", command=self.show_admin_login)
        self.admin_btn.pack(side=tk.LEFT, padx=5)
        
        # Content Frame
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
    
    def show_movies_page(self):
        self.clear_frame(self.content_frame)
        
        # Header
        header_label = ttk.Label(self.content_frame, text="Available Movies", style='Heading.TLabel')
        header_label.pack(pady=10)
        
        # Movies container
        movies_container = ttk.Frame(self.content_frame)
        movies_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(movies_container, bg="#1a1a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(movies_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Fetch movies from database
        conn = sqlite3.connect('movie_booking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, language, duration, genre, available_seats, price, image FROM movies")
        movies = cursor.fetchall()
        conn.close()
        
        # Display movies in a grid
        row = 0
        col = 0
        for movie in movies:
            movie_id, title, description, language, duration, genre, available_seats, price, img_data = movie
            
            # Create movie card
            movie_frame = ttk.Frame(scrollable_frame, style='Card.TFrame', width=300, height=200)
            movie_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            movie_frame.grid_propagate(False)
            
            # Movie thumbnail
            img_label = ttk.Label(movie_frame, background='#2c3e50')
            if img_data:
                try:
                    img = Image.open(io.BytesIO(img_data))
                    img = img.resize((100, 150), Image.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    img_label.configure(image=img_tk)
                    img_label.image = img_tk
                except Exception as e:
                    print(f"Error loading image: {e}")
                    img_label.configure(text="[No Image]", foreground="#ffffff")
            else:
                img_label.configure(text="[No Image]", foreground="#ffffff")
            img_label.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
            
            # Movie details
            ttk.Label(movie_frame, text=title, style='Heading.TLabel', font=('Helvetica', 14, 'bold')).grid(row=0, column=1, sticky="w", padx=5)
            ttk.Label(movie_frame, text=f"Genre: {genre}", foreground="#ffffff", background='#2c3e50').grid(row=1, column=1, sticky="w", padx=5)
            ttk.Label(movie_frame, text=f"Duration: {duration}", foreground="#ffffff", background='#2c3e50').grid(row=2, column=1, sticky="w", padx=5)
            ttk.Label(movie_frame, text=f"Price: ${price}", foreground="#ffffff", background='#2c3e50').grid(row=3, column=1, sticky="w", padx=5)
            
            # Available seats
            ttk.Label(movie_frame, text=f"Available Seats: {available_seats}", foreground="#ffffff", background='#2c3e50').grid(row=4, column=0, columnspan=2, sticky="w", padx=5)
            
            # Book button
            book_btn = ttk.Button(movie_frame, text="Book Tickets", 
                                command=lambda m_id=movie_id, m_title=title, m_price=price: self.show_booking_page(m_id, m_title, m_price))
            book_btn.grid(row=5, column=0, columnspan=2, pady=10)
            
            # Update grid position
            col += 1
            if col > 2:  # 3 movies per row
                col = 0
                row += 1
    
    def show_booking_page(self, movie_id, movie_title, price):
        self.clear_frame(self.content_frame)
        
        # Header
        header_label = ttk.Label(self.content_frame, text=f"Book Tickets for {movie_title}", style='Heading.TLabel')
        header_label.pack(pady=10)
        
        # Get available seats
        conn = sqlite3.connect('movie_booking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT available_seats FROM movies WHERE id = ?", (movie_id,))
        available_seats = cursor.fetchone()[0]
        conn.close()
        
        # Create booking form
        booking_frame = ttk.Frame(self.content_frame)
        booking_frame.pack(pady=20)
        
        # Customer Information Frame
        customer_frame = ttk.Frame(booking_frame)
        customer_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH)
        
        ttk.Label(customer_frame, text="Customer Information", style='Heading.TLabel', font=('Helvetica', 16, 'bold')).pack(anchor="w", pady=10)
        
        ttk.Label(customer_frame, text="Name:").pack(anchor="w", pady=5)
        name_entry = ttk.Entry(customer_frame, width=30)
        name_entry.pack(anchor="w", pady=5)
        
        ttk.Label(customer_frame, text="Phone:").pack(anchor="w", pady=5)
        phone_entry = ttk.Entry(customer_frame, width=30)
        phone_entry.pack(anchor="w", pady=5)
        
        ttk.Label(customer_frame, text="Email:").pack(anchor="w", pady=5)
        email_entry = ttk.Entry(customer_frame, width=30)
        email_entry.pack(anchor="w", pady=5)
        
        ttk.Label(customer_frame, text=f"Price per Seat: ${price}").pack(anchor="w", pady=10)
        
        # Number of seats
        ttk.Label(customer_frame, text=f"Number of Seats (max {available_seats}):").pack(anchor="w", pady=5)
        seats_var = tk.StringVar()
        seats_spinbox = ttk.Spinbox(customer_frame, from_=1, to=available_seats, textvariable=seats_var, width=5)
        seats_spinbox.pack(anchor="w", pady=5)
        seats_var.set("1")  # Default value
        
        # Total amount label
        total_var = tk.StringVar()
        total_var.set(f"Total Amount: ${price}")
        total_label = ttk.Label(customer_frame, textvariable=total_var)
        total_label.pack(anchor="w", pady=10)
        
        # Update total when seats change
        def update_total(*args):
            try:
                num_seats = int(seats_var.get())
                total = num_seats * price
                total_var.set(f"Total Amount: ${total:.2f}")
            except ValueError:
                pass
        
        seats_var.trace("w", update_total)
        
        # Seat Selection Frame
        seat_frame = ttk.Frame(booking_frame)
        seat_frame.pack(side=tk.RIGHT, padx=20, fill=tk.BOTH)
        
        ttk.Label(seat_frame, text="Seat Selection", style='Heading.TLabel', font=('Helvetica', 16, 'bold')).pack(anchor="w", pady=10)
        
        # Create a simple visual representation of seats
        seats_layout = ttk.Frame(seat_frame)
        seats_layout.pack(pady=10)
        
        ttk.Label(seats_layout, text="SCREEN", foreground="#ffffff", background="#3498db", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, columnspan=10, sticky="ew", pady=10)
        
        self.selected_seats = []
        
        def seat_click(btn, seat_id):
            if seat_id in self.selected_seats:
                self.selected_seats.remove(seat_id)
                btn.configure(style='Available.TButton')
            else:
                if len(self.selected_seats) < int(seats_var.get()):
                    self.selected_seats.append(seat_id)
                    btn.configure(style='Selected.TButton')
                else:
                    messagebox.showwarning("Seat Selection", f"You can only select {seats_var.get()} seats.")
        
        # Create seat styles
        style = ttk.Style()
        style.configure('Available.TButton', background='#2ecc71', foreground='#ffffff')
        style.configure('Selected.TButton', background='#e74c3c', foreground='#ffffff')
        style.configure('Booked.TButton', background='#7f8c8d', foreground='#ffffff')
        
        # Generate seats
        self.seat_buttons = {}
        for row in range(1, 6):  # 5 rows
            for col in range(1, 11):  # 10 seats per row
                seat_id = f"{chr(64+row)}{col}"  # A1, A2, etc.
                
                # Randomly mark some seats as booked for demo purposes
                is_booked = random.random() < 0.3 and available_seats < 100  # 30% chance a seat is booked
                
                if is_booked:
                    seat_btn = ttk.Button(seats_layout, text=seat_id, style='Booked.TButton', state='disabled')
                else:
                    seat_btn = ttk.Button(seats_layout, text=seat_id, style='Available.TButton',
                                        command=lambda b=seat_btn, s=seat_id: seat_click(b, s))
                
                seat_btn.grid(row=row, column=col-1, padx=2, pady=2)
                self.seat_buttons[seat_id] = seat_btn
        
        # Function to handle booking
        def confirm_booking():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            num_seats = int(seats_var.get())
            
            # Validation
            if not name or not phone:
                messagebox.showerror("Error", "Name and Phone are required fields")
                return
                
            if len(self.selected_seats) != num_seats:
                messagebox.showerror("Error", f"Please select exactly {num_seats} seats")
                return
            
            # Calculate total amount
            total_amount = num_seats * price
            
            # Save booking to database
            conn = sqlite3.connect('movie_booking.db')
            cursor = conn.cursor()
            
            booking_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert booking
            cursor.execute('''
                INSERT INTO bookings (movie_id, customer_name, phone, email, seats, total_amount, booking_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (movie_id, name, phone, email, ','.join(self.selected_seats), total_amount, booking_date))
            
            # Update available seats in movies table
            cursor.execute('''
                UPDATE movies SET available_seats = available_seats - ? WHERE id = ?
            ''', (num_seats, movie_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Booking Confirmation", f"Booking confirmed!\nSeats: {', '.join(self.selected_seats)}\nTotal Amount: ${total_amount:.2f}")
            self.show_movies_page()
        
        # Confirm Booking Button
        confirm_btn = ttk.Button(booking_frame, text="Confirm Booking", command=confirm_booking)
        confirm_btn.pack(pady=20)

    #Admin Portal
    def show_admin_login(self):
        self.clear_frame(self.content_frame)

        # Header
        header_label = ttk.Label(self.content_frame, text="Admin Login", style='Heading.TLabel')
        header_label.pack(pady=10)

        # Login Form
        login_frame = ttk.Frame(self.content_frame)
        login_frame.pack(pady=20)

        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        username_entry = ttk.Entry(login_frame, width=30)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(login_frame, show="*", width=30)
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            conn = sqlite3.connect('movie_booking.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
            admin = cursor.fetchone()
            conn.close()

            if admin:
                self.show_admin_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")

        login_btn = ttk.Button(login_frame, text="Login", command=login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=10)

    def show_admin_dashboard(self):
         self.clear_frame(self.content_frame)

         # Header
         header_label = ttk.Label(self.content_frame, text="Admin Dashboard", style='Heading.TLabel')
         header_label.pack(pady=10)

         # Dashboard Frame
         dashboard_frame = ttk.Frame(self.content_frame)
         dashboard_frame.pack(pady=20)

         # Total Sales
         conn = sqlite3.connect('movie_booking.db')
         cursor = conn.cursor()
         cursor.execute("SELECT SUM(total_amount) FROM bookings")
         total_sales = cursor.fetchone()[0] or 0
         ttk.Label(dashboard_frame, text=f"Total Sales: ${total_sales:.2f}").pack(pady=5)

         # Movie-wise Ticket Purchases
         cursor.execute('''
             SELECT m.title, COUNT(b.id)
             FROM bookings b
             JOIN movies m ON b.movie_id = m.id
             GROUP BY m.title
         ''')
         movie_purchases = cursor.fetchall()

         ttk.Label(dashboard_frame, text="Movie-wise Ticket Purchases:").pack(pady=5)
         for movie, count in movie_purchases:
             ttk.Label(dashboard_frame, text=f"{movie}: {count}").pack(pady=2)
             
         conn.close()

         # Buttons to Manage Movies and Bookings
         manage_movies_btn = ttk.Button(dashboard_frame, text="Manage Movies", command=self.show_manage_movies)
         manage_movies_btn.pack(pady=10)

         manage_bookings_btn = ttk.Button(dashboard_frame, text="Manage Bookings", command=self.show_manage_bookings)
         manage_bookings_btn.pack(pady=10)
         
    def show_manage_movies(self):
        self.clear_frame(self.content_frame)

        # Header
        header_label = ttk.Label(self.content_frame, text="Manage Movies", style='Heading.TLabel')
        header_label.pack(pady=10)

        # Add Movie Button
        add_movie_btn = ttk.Button(self.content_frame, text="Add New Movie", command=self.show_add_movie_form)
        add_movie_btn.pack(pady=10)

        # Movie List
        movies_frame = ttk.Frame(self.content_frame)
        movies_frame.pack(fill=tk.BOTH, expand=True)

        # Fetch movies from database
        conn = sqlite3.connect('movie_booking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, language, duration, genre, total_seats, available_seats, price FROM movies")
        movies = cursor.fetchall()
        conn.close()

        for movie_id, title, description, language, duration, genre, total_seats, available_seats, price in movies:
            movie_label = ttk.Label(movies_frame, text=title)
            movie_label.pack(pady=2)

            # Update and Delete buttons for each movie
            update_btn = ttk.Button(movies_frame, text="Update", command=lambda m_id=movie_id: self.show_update_movie_form(m_id))
            update_btn.pack(side=tk.LEFT, padx=5)

            delete_btn = ttk.Button(movies_frame, text="Delete", command=lambda m_id=movie_id: self.delete_movie(m_id))
            delete_btn.pack(side=tk.LEFT, padx=5)
            
    def show_add_movie_form(self):
        self.clear_frame(self.content_frame)

        # Header
        header_label = ttk.Label(self.content_frame, text="Add New Movie", style='Heading.TLabel')
        header_label.pack(pady=10)

        # Form Frame
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(pady=20)

        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        title_entry = ttk.Entry(form_frame, width=30)
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        description_entry = tk.Text(form_frame, width=30, height=5)
        description_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Language:").grid(row=2, column=0, padx=5, pady=5)
        language_entry = ttk.Entry(form_frame, width=30)
        language_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Duration:").grid(row=3, column=0, padx=5, pady=5)
        duration_entry = ttk.Entry(form_frame, width=30)
        duration_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Release Date:").grid(row=4, column=0, padx=5, pady=5)
        release_date_entry = ttk.Entry(form_frame, width=30)
        release_date_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Genre:").grid(row=5, column=0, padx=5, pady=5)
        genre_entry = ttk.Entry(form_frame, width=30)
        genre_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Total Seats:").grid(row=6, column=0, padx=5, pady=5)
        total_seats_entry = ttk.Entry(form_frame, width=30)
        total_seats_entry.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Price:").grid(row=7, column=0, padx=5, pady=5)
        price_entry = ttk.Entry(form_frame, width=30)
        price_entry.grid(row=7, column=1, padx=5, pady=5)

        # Image Upload
        ttk.Label(form_frame, text="Image:").grid(row=8, column=0, padx=5, pady=5)
        image_label = ttk.Label(form_frame, text="No image selected")
        image_label.grid(row=8, column=1, padx=5, pady=5)
        self.image_data = None

        def upload_image():
            filename = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if filename:
                try:
                    img = Image.open(filename)
                    img = img.resize((100, 150), Image.LANCZOS)
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    self.image_data = img_byte_arr  # Store image data
                    img_tk = ImageTk.PhotoImage(img)
                    image_label.configure(image=img_tk)
                    image_label.image = img_tk
                except Exception as e:
                    messagebox.showerror("Error", f"Error loading image: {e}")

        upload_btn = ttk.Button(form_frame, text="Upload Image", command=upload_image)
        upload_btn.grid(row=9, column=1, padx=5, pady=5)

        def add_movie():
            title = title_entry.get().strip()
            description = description_entry.get("1.0", tk.END).strip()
            language = language_entry.get().strip()
            duration = duration_entry.get().strip()
            release_date = release_date_entry.get().strip()
            genre = genre_entry.get().strip()
            try:
                total_seats = int(total_seats_entry.get().strip())
                price = float(price_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Total Seats and Price must be valid numbers.")
                return

            # Validation
            if not title or not language or not duration or not release_date or not genre:
                messagebox.showerror("Error", "All fields are required.")
                return

            # Save to database
            conn = sqlite3.connect('movie_booking.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO movies (title, description, language, duration, release_date, genre, total_seats, available_seats, price, image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, language, duration, release_date, genre, total_seats, total_seats, price, self.image_data))  # Initially available seats = total seats
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Movie added successfully.")
            self.show_manage_movies()

        add_btn = ttk.Button(form_frame, text="Add Movie", command=add_movie)
        add_btn.grid(row=10, column=0, columnspan=2, pady=10)
        
    def show_update_movie_form(self, movie_id):
        self.clear_frame(self.content_frame)

        # Header
        header_label = ttk.Label(self.content_frame, text="Update Movie", style='Heading.TLabel')
        header_label.pack(pady=10)

        # Form Frame
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(pady=20)

        # Fetch movie details from database
        conn = sqlite3.connect('movie_booking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title, description, language, duration, release_date, genre, total_seats, price, image FROM movies WHERE id = ?", (movie_id,))
        movie = cursor.fetchone()
        conn.close()

        if not movie:
            messagebox.showerror("Error", "Movie not found.")
            self.show_manage_movies()
            return

        title, description, language, duration, release_date, genre, total_seats, price, image_data = movie

        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        title_entry = ttk.Entry(form_frame, width=30)
        title_entry.grid(row=0, column=1, padx=5, pady=5)
        title_entry.insert(0, title)

        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        description_entry = tk.Text(form_frame, width=30, height=5)
        description_entry.grid(row=1, column=1, padx=5, pady=5)
        description_entry.insert("1.0", description)

        ttk.Label(form_frame, text="Language:").grid(row=2, column=0, padx=5, pady=5)
        language_entry = ttk.Entry(form_frame, width=30)
        language_entry.grid(row=2, column=1, padx=5, pady=5)
        language_entry.insert(0, language)

        ttk.Label(form_frame, text="Duration:").grid(row=3, column=0, padx=5, pady=5)
        duration_entry = ttk.Entry(form_frame, width=30)
        duration_entry.grid(row=3, column=1, padx=5, pady=5)
        duration_entry.insert(0, duration)

        ttk.Label(form_frame, text="Release Date:").grid(row=4, column=0, padx=5, pady=5)
        release_
