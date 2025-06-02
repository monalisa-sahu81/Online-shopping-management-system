#woring code 
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

class ShoppingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Shopping System")
        self.root.geometry("800x600")
        self.current_user = None
        
        # Database connection
        self.db_connect()
        
        # GUI Setup
        self.setup_login_frame()
        self.setup_main_frame()
        
        # Show login screen initially
        self.show_login()

    def db_connect(self):
        """Connect to MySQL database with error handling"""
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="shopping_db"
            )
            self.cursor = self.conn.cursor()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect: {e}")
            self.root.destroy()

    def setup_login_frame(self):
        """Create login/register interface"""
        self.login_frame = ttk.Frame(self.root, padding=20)
        
        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, pady=5)
        self.login_username = ttk.Entry(self.login_frame)
        self.login_username.grid(row=0, column=1, pady=5)
        
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, pady=5)
        self.login_password = ttk.Entry(self.login_frame, show="*")
        self.login_password.grid(row=1, column=1, pady=5)
        
        btn_frame = ttk.Frame(self.login_frame)
        btn_frame.grid(row=2, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Login", command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Register", command=self.register).pack(side=tk.LEFT, padx=5)

    def setup_main_frame(self):
        """Create main application interface"""
        self.main_frame = ttk.Frame(self.root, padding=20)
        
        # Product Management
        product_frame = ttk.LabelFrame(self.main_frame, text="Product Management", padding=10)
        product_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(product_frame, text="Name:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.product_name = ttk.Entry(product_frame)
        self.product_name.grid(row=0, column=1, padx=5)
        
        ttk.Label(product_frame, text="Price:").grid(row=1, column=0, padx=5, sticky=tk.W)
        self.product_price = ttk.Entry(product_frame)
        self.product_price.grid(row=1, column=1, padx=5)
        
        btn_frame = ttk.Frame(product_frame)
        btn_frame.grid(row=2, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View Products", command=self.view_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        
        # Products List
        list_frame = ttk.LabelFrame(self.main_frame, text="Products", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.products_list = tk.Listbox(list_frame, height=10, font=('Arial', 11))
        self.products_list.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.products_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.products_list.config(yscrollcommand=scrollbar.set)
        
        # Order Management
        order_frame = ttk.LabelFrame(self.main_frame, text="Order Management", padding=10)
        order_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(order_frame, text="Quantity:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.order_quantity = ttk.Entry(order_frame, width=10)
        self.order_quantity.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        btn_frame = ttk.Frame(order_frame)
        btn_frame.grid(row=1, columnspan=2, pady=5)
        
        ttk.Button(btn_frame, text="Place Order", command=self.place_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View My Orders", command=self.view_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Logout", command=self.logout).pack(side=tk.LEFT, padx=5)

    def show_login(self):
        """Show login screen and hide main screen"""
        self.main_frame.pack_forget()
        self.login_frame.pack()
        self.login_username.focus()

    def show_main(self):
        """Show main application screen"""
        self.login_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.view_products()

    def login(self):
        """Authenticate user"""
        username = self.login_username.get()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showwarning("Error", "Please enter both username and password")
            return
        
        try:
            self.cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", 
                              (username, password))
            user = self.cursor.fetchone()
            
            if user:
                self.current_user = user[0]
                self.show_main()
                messagebox.showinfo("Success", f"Welcome, {username}!")
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except Error as e:
            messagebox.showerror("Database Error", f"Login failed: {e}")

    def register(self):
        """Register new user"""
        username = self.login_username.get()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showwarning("Error", "Please enter both username and password")
            return
        
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                               (username, password))
            self.conn.commit()
            messagebox.showinfo("Success", "Registration successful! Please login.")
        except Error as e:
            messagebox.showerror("Error", f"Registration failed: {e}")

    def add_product(self):
        name = self.product_name.get()
        price = self.product_price.get()
    
        try:
            price = float(price)    # First check if price is valid number
        
        # Verify table structure (debugging)
            self.cursor.execute("SHOW COLUMNS FROM products LIKE 'price'")
            if not self.cursor.fetchone():
                messagebox.showerror("Error", "Price column missing in database!")
                return
            
        # Safe insert with error handling
            self.cursor.execute(
            "INSERT INTO products (name, price) VALUES (%s, %s)",
            (name, price))
            self.conn.commit()
            messagebox.showinfo("Success", "Product added!")
        
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add product: {err}")
    def view_products(self):
        """Display all products in the listbox"""
        try:
            self.cursor.execute("SELECT id, name, price FROM products")
            products = self.cursor.fetchall()
            
            self.products_list.delete(0, tk.END)
            for product in products:
                self.products_list.insert(tk.END, f"ID: {product[0]} | {product[1]} - ${product[2]:.2f}")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load products: {e}")

    def delete_product(self):
        """Delete selected product"""
        selection = self.products_list.curselection()
        if not selection:
            messagebox.showwarning("Error", "Please select a product to delete")
            return
        
        product_id = self.products_list.get(selection[0]).split("|")[0].split(":")[1].strip()
        
        try:
            # Check if product has orders
            self.cursor.execute("SELECT COUNT(*) FROM orders WHERE product_id = %s", (product_id,))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showwarning("Error", "Cannot delete - product has existing orders")
                return
            
            self.cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Product deleted successfully!")
            self.view_products()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to delete product: {e}")

    def place_order(self):
        """Place order for selected product"""
        selection = self.products_list.curselection()
        quantity = self.order_quantity.get()
    
        if not selection:
            messagebox.showwarning("Error", "Please select a product")
            return
    
        if not quantity:
            messagebox.showwarning("Error", "Please enter quantity")
            return
    
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer")
            return
    
        try:
            product_info = self.products_list.get(selection[0])  # Fixed: Added missing parenthesis
            product_id = product_info.split("|")[0].split(":")[1].strip()
            product_name = product_info.split("|")[1].split("-")[0].strip()
        
            self.cursor.execute(
                "INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                (self.current_user, product_id, quantity)
            )
            self.conn.commit()
            messagebox.showinfo("Order Confirmed", 
                          f"Your order for {quantity} x {product_name} has been confirmed!")
            self.order_quantity.delete(0, tk.END)
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to place order: {e}")
        
    def view_orders(self):
        """View current user's orders"""
        try:
            self.cursor.execute("""
                SELECT o.id, p.name, o.quantity, p.price * o.quantity as total 
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE o.user_id = %s
            """, (self.current_user,))
            orders = self.cursor.fetchall()
            
            self.products_list.delete(0, tk.END)
            for order in orders:
                self.products_list.insert(tk.END, 
                    f"Order #{order[0]} | {order[1]} x{order[2]} = ${order[3]:.2f}")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load orders: {e}")

    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.login_username.delete(0, tk.END)
        self.login_password.delete(0, tk.END)
        self.show_login()

    def __del__(self):
        """Clean up database connection when closing"""
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ShoppingSystem(root)
    root.mainloop()