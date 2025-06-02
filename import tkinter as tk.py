import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import threading
import time
from datetime import datetime

class ShoppingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Shopping System")
        self.root.geometry("900x650")
        self.current_user = None
        self.last_order_check = None
        self.last_product_update = None
        
        # Center the window
        self.center_window()
        
        # Database connection
        self.db_connect()
        
        # Setup GUI
        self.setup_login_frame()
        self.setup_main_frame()
        
        # Show login screen initially
        self.show_login()
        
        # Start background thread for real-time updates
        self.start_update_thread()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def db_connect(self):
        """Connect to MySQL database"""
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="shopping_db"
            )
            self.cursor = self.conn.cursor()
            
            # Create tables if they don't exist
            self.create_tables()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect: {e}")
            self.root.destroy()

    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            # Create users table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create products table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create orders table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            self.conn.commit()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to create tables: {e}")

    def setup_login_frame(self):
        """Create login/register interface"""
        self.login_frame = ttk.Frame(self.root, padding=30)
        
        # Center the login frame
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Make the login frame content
        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, pady=5, sticky=tk.E)
        self.login_username = ttk.Entry(self.login_frame, width=25)
        self.login_username.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, pady=5, sticky=tk.E)
        self.login_password = ttk.Entry(self.login_frame, show="*", width=25)
        self.login_password.grid(row=1, column=1, pady=5, padx=5)
        
        btn_frame = ttk.Frame(self.login_frame)
        btn_frame.grid(row=2, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="Login", command=self.login, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Register", command=self.register, width=10).pack(side=tk.LEFT, padx=5)

    def setup_main_frame(self):
        """Create main application interface with tabs"""
        self.main_frame = ttk.Frame(self.root, padding=10)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.setup_products_tab()
        self.setup_orders_tab()
        self.setup_profile_tab()
        
        # Real-time notification area
        self.notification_var = tk.StringVar()
        self.notification_label = ttk.Label(
            self.main_frame, 
            textvariable=self.notification_var,
            wraplength=800,
            foreground="blue",
            padding=(10, 5)
        )
        self.notification_label.pack(fill=tk.X, pady=5)
        
        # Logout button
        ttk.Button(
            self.main_frame, 
            text="Logout", 
            command=self.logout,
            width=15
        ).pack(pady=10)

    def setup_products_tab(self):
        """Products management tab"""
        self.products_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.products_tab, text="Products")
        
        # Search frame
        search_frame = ttk.Frame(self.products_tab, padding=5)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.search_entry.bind('<KeyRelease>', self.search_products)
        
        # Products Treeview with scrollbar
        tree_frame = ttk.Frame(self.products_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.products_tree = ttk.Treeview(tree_frame, columns=('id', 'name', 'price'), show='headings')
        self.products_tree.heading('id', text='ID')
        self.products_tree.heading('name', text='Product Name')
        self.products_tree.heading('price', text='Price')
        self.products_tree.column('id', width=50, anchor='center')
        self.products_tree.column('name', width=300)
        self.products_tree.column('price', width=100, anchor='e')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Product management frame
        manage_frame = ttk.LabelFrame(self.products_tab, text="Product Management", padding=10)
        manage_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(manage_frame, text="Name:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.product_name = ttk.Entry(manage_frame)
        self.product_name.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        ttk.Label(manage_frame, text="Price:").grid(row=1, column=0, padx=5, sticky=tk.W)
        self.product_price = ttk.Entry(manage_frame)
        self.product_price.grid(row=1, column=1, padx=5, sticky=tk.EW)
        
        btn_frame = ttk.Frame(manage_frame)
        btn_frame.grid(row=2, columnspan=2, pady=5)
        
        ttk.Button(btn_frame, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update Product", command=self.update_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=5)

    def setup_orders_tab(self):
        """Orders management tab"""
        self.orders_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_tab, text="My Orders")
        
        # Orders Treeview with improved layout
        tree_frame = ttk.Frame(self.orders_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.orders_tree = ttk.Treeview(
            tree_frame, 
            columns=('id', 'product', 'quantity', 'price', 'total', 'date'), 
            show='headings'
        )
        
        # Configure columns
        self.orders_tree.heading('id', text='Order ID')
        self.orders_tree.heading('product', text='Product')
        self.orders_tree.heading('quantity', text='Qty')
        self.orders_tree.heading('price', text='Unit Price')
        self.orders_tree.heading('total', text='Total')
        self.orders_tree.heading('date', text='Order Date')
        
        self.orders_tree.column('id', width=70, anchor='center')
        self.orders_tree.column('product', width=200)
        self.orders_tree.column('quantity', width=60, anchor='center')
        self.orders_tree.column('price', width=90, anchor='e')
        self.orders_tree.column('total', width=90, anchor='e')
        self.orders_tree.column('date', width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        
        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Order placement frame
        order_frame = ttk.LabelFrame(self.orders_tab, text="Place New Order", padding=10)
        order_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(order_frame, text="Product:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.order_product = ttk.Combobox(order_frame, state='readonly')
        self.order_product.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        ttk.Label(order_frame, text="Quantity:").grid(row=1, column=0, padx=5, sticky=tk.W)
        self.order_quantity = ttk.Spinbox(order_frame, from_=1, to=100, width=5)
        self.order_quantity.grid(row=1, column=1, padx=5, sticky=tk.W)
        
        ttk.Button(
            order_frame, 
            text="Place Order", 
            command=self.place_order
        ).grid(row=2, columnspan=2, pady=5)

    def setup_profile_tab(self):
        """User profile tab"""
        self.profile_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_tab, text="My Profile")
        
        # User info frame
        info_frame = ttk.LabelFrame(self.profile_tab, text="User Information", padding=10)
        info_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(info_frame, text="Username:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.profile_username = ttk.Label(info_frame, text="", font=('TkDefaultFont', 10, 'bold'))
        self.profile_username.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(info_frame, text="Registration Date:").grid(row=1, column=0, padx=5, sticky=tk.W)
        self.profile_regdate = ttk.Label(info_frame, text="")
        self.profile_regdate.grid(row=1, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(info_frame, text="Total Orders:").grid(row=2, column=0, padx=5, sticky=tk.W)
        self.profile_orders = ttk.Label(info_frame, text="", font=('TkDefaultFont', 10, 'bold'))
        self.profile_orders.grid(row=2, column=1, padx=5, sticky=tk.W)

    def start_update_thread(self):
        """Start background thread for real-time updates"""
        def update_loop():
            while hasattr(self, 'root') and self.root.winfo_exists():
                if self.current_user:
                    self.check_for_updates()
                time.sleep(5)  # Check every 5 seconds
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

    def check_for_updates(self):
        """Check for new products or orders"""
        try:
            # Check for new products
            if self.last_product_update:
                self.cursor.execute(
                    "SELECT COUNT(*) FROM products WHERE created_at > %s",
                    (self.last_product_update,))
            else:
                self.cursor.execute("SELECT COUNT(*) FROM products")
            
            product_count = self.cursor.fetchone()[0]
            if product_count > 0:
                self.root.after(0, self.show_notification, f"New products available! {product_count} new item(s)")
                self.root.after(0, self.load_products)
                self.last_product_update = datetime.now()
            
            # Check for order updates
            if self.last_order_check and self.current_user:
                self.cursor.execute(
                    """SELECT COUNT(*) FROM orders 
                    WHERE user_id = %s AND order_date > %s""",
                    (self.current_user, self.last_order_check)
                )
                new_orders = self.cursor.fetchone()[0]
                if new_orders > 0:
                    self.root.after(0, self.show_notification, f"You have {new_orders} new order(s)")
                    self.root.after(0, self.load_orders)
            
            self.last_order_check = datetime.now()
            
        except Error as e:
            print(f"Update check error: {e}")

    def show_notification(self, message):
        """Show a notification message"""
        self.notification_var.set(message)
        self.root.after(5000, lambda: self.notification_var.set(""))  # Clear after 5 seconds

    def search_products(self, event=None):
        """Search products by name"""
        search_term = self.search_entry.get()
        try:
            if search_term:
                self.cursor.execute(
                    "SELECT id, name, price FROM products WHERE name LIKE %s",
                    (f"%{search_term}%",))
            else:
                self.cursor.execute("SELECT id, name, price FROM products")
            
            self.products_tree.delete(*self.products_tree.get_children())
            for product in self.cursor.fetchall():
                self.products_tree.insert('', 'end', values=product)
        except Error as e:
            messagebox.showerror("Error", f"Failed to search products: {e}")

    def load_products(self):
        """Load all products into the Treeview"""
        try:
            self.cursor.execute("SELECT id, name, price FROM products")
            self.products_tree.delete(*self.products_tree.get_children())
            for product in self.cursor.fetchall():
                self.products_tree.insert('', 'end', values=product)
            
            # Update product combobox in orders tab
            self.cursor.execute("SELECT id, name FROM products")
            products = self.cursor.fetchall()
            self.order_product['values'] = [f"{p[0]} - {p[1]}" for p in products]
            if products:
                self.order_product.current(0)
        except Error as e:
            messagebox.showerror("Error", f"Failed to load products: {e}")

    def load_orders(self):
        """Load user's orders into the Treeview with proper formatting"""
        if not self.current_user:
            return
            
        try:
            self.cursor.execute(
                """SELECT o.id, p.name, o.quantity, p.price, 
                (p.price * o.quantity) as total, o.order_date
                FROM orders o JOIN products p ON o.product_id = p.id
                WHERE o.user_id = %s ORDER BY o.order_date DESC""",
                (self.current_user,)
            )
            
            self.orders_tree.delete(*self.orders_tree.get_children())
            for order in self.cursor.fetchall():
                # Format the values for display
                formatted_order = (
                    order[0],  # ID
                    order[1],  # Product name
                    order[2],  # Quantity
                    f"${order[3]:.2f}",  # Unit price
                    f"${order[4]:.2f}",  # Total
                    order[5].strftime("%Y-%m-%d %H:%M")  # Formatted date
                )
                self.orders_tree.insert('', 'end', values=formatted_order)
        except Error as e:
            messagebox.showerror("Error", f"Failed to load orders: {e}")

    def load_profile(self):
        """Load user profile information"""
        if not self.current_user:
            return
            
        try:
            # Get user info
            self.cursor.execute(
                "SELECT username, created_at FROM users WHERE id = %s",
                (self.current_user,)
            )
            user = self.cursor.fetchone()
            self.profile_username.config(text=user[0])
            self.profile_regdate.config(text=user[1].strftime("%Y-%m-%d %H:%M:%S"))
            
            # Get order count
            self.cursor.execute(
                "SELECT COUNT(*) FROM orders WHERE user_id = %s",
                (self.current_user,)
            )
            order_count = self.cursor.fetchone()[0]
            self.profile_orders.config(text=str(order_count))
        except Error as e:
            messagebox.showerror("Error", f"Failed to load profile: {e}")

    def add_product(self):
        """Add a new product"""
        name = self.product_name.get()
        price = self.product_price.get()
        
        if not name or not price:
            messagebox.showwarning("Error", "Please enter both name and price")
            return
            
        try:
            price = float(price)
            self.cursor.execute(
                "INSERT INTO products (name, price) VALUES (%s, %s)",
                (name, price)
            )
            self.conn.commit()
            messagebox.showinfo("Success", "Product added successfully")
            self.load_products()
            self.product_name.delete(0, tk.END)
            self.product_price.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
        except Error as e:
            messagebox.showerror("Error", f"Failed to add product: {e}")

    def update_product(self):
        """Update selected product"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Please select a product to update")
            return
            
        product_id = self.products_tree.item(selected[0])['values'][0]
        name = self.product_name.get()
        price = self.product_price.get()
        
        if not name or not price:
            messagebox.showwarning("Error", "Please enter both name and price")
            return
            
        try:
            price = float(price)
            self.cursor.execute(
                "UPDATE products SET name = %s, price = %s WHERE id = %s",
                (name, price, product_id)
            )
            self.conn.commit()
            messagebox.showinfo("Success", "Product updated successfully")
            self.load_products()
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
        except Error as e:
            messagebox.showerror("Error", f"Failed to update product: {e}")

    def delete_product(self):
        """Delete selected product"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Please select a product to delete")
            return
            
        product_id = self.products_tree.item(selected[0])['values'][0]
        
        try:
            # Check if product has orders
            self.cursor.execute(
                "SELECT COUNT(*) FROM orders WHERE product_id = %s",
                (product_id,)
            )
            if self.cursor.fetchone()[0] > 0:
                messagebox.showwarning("Error", "Cannot delete - product has existing orders")
                return
                
            self.cursor.execute(
                "DELETE FROM products WHERE id = %s",
                (product_id,)
            )
            self.conn.commit()
            messagebox.showinfo("Success", "Product deleted successfully")
            self.load_products()
        except Error as e:
            messagebox.showerror("Error", f"Failed to delete product: {e}")

    def place_order(self):
        """Place a new order"""
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
            
        product_selection = self.order_product.get()
        quantity = self.order_quantity.get()
        
        if not product_selection or not quantity:
            messagebox.showwarning("Error", "Please select a product and quantity")
            return
            
        try:
            product_id = int(product_selection.split(' - ')[0])
            quantity = int(quantity)
            
            if quantity <= 0:
                raise ValueError
                
            # Get product price
            self.cursor.execute(
                "SELECT price FROM products WHERE id = %s",
                (product_id,)
            )
            price = self.cursor.fetchone()[0]
            
            # Insert order
            self.cursor.execute(
                """INSERT INTO orders 
                (user_id, product_id, quantity, order_date) 
                VALUES (%s, %s, %s, NOW())""",
                (self.current_user, product_id, quantity)
            )
            self.conn.commit()
            
            messagebox.showinfo(
                "Success", 
                f"Order placed successfully!\n"
                f"Product: {product_selection}\n"
                f"Quantity: {quantity}\n"
                f"Total: ${price * quantity:.2f}"
            )
            
            self.load_orders()
            self.load_profile()
            self.order_quantity.delete(0, tk.END)
            self.order_quantity.insert(0, "1")
            
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer")
        except Error as e:
            messagebox.showerror("Error", f"Failed to place order: {e}")

    def login(self):
        """Authenticate user"""
        username = self.login_username.get()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showwarning("Error", "Please enter both username and password")
            return
            
        try:
            self.cursor.execute(
                "SELECT id FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            user = self.cursor.fetchone()
            
            if user:
                self.current_user = user[0]
                self.show_main()
                self.load_products()
                self.load_orders()
                self.load_profile()
                self.last_order_check = datetime.now()
                self.last_product_update = datetime.now()
                messagebox.showinfo("Success", f"Welcome, {username}!")
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except Error as e:
            messagebox.showerror("Error", f"Login failed: {e}")

    def register(self):
        """Register new user"""
        username = self.login_username.get()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showwarning("Error", "Please enter both username and password")
            return
            
        try:
            # Check if username exists
            self.cursor.execute(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )
            if self.cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return
                
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            self.conn.commit()
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.login_username.delete(0, tk.END)
            self.login_password.delete(0, tk.END)
        except Error as e:
            messagebox.showerror("Error", f"Registration failed: {e}")

    def show_login(self):
        """Show login screen"""
        if hasattr(self, 'main_frame'):
            self.main_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        self.login_username.focus()

    def show_main(self):
        """Show main application screen"""
        self.login_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.center_window()  # Re-center after showing main window

    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.login_username.delete(0, tk.END)
        self.login_password.delete(0, tk.END)
        self.show_login()

    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ShoppingSystem(root)
    root.mainloop()