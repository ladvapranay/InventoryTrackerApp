Itemize – Inventory Management System

Admin Username / Password

	• Username: admin
	•	Password: test 

Itemize is a Django-based web application that allows employees to raise office equipment requests, view available inventory, and enables admins to manage approvals and inventory records.

Prerequisites

	•	Python 3.8 or higher
 	•	Git
	•	pip (Python package installer)
 

 Clone the repository:
<pre>
git clone https://github.com/yourusername/InventoryTrackerApp.git
cd InventoryTrackerApp
</pre>

Create a virtual environment
<pre>
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
</pre>

Install dependencies
<pre>
pip install -r requirements.txt
</pre>


Initialize the database
<pre>
python manage.py migrate
</pre>

Running the Application
<pre>
python manage.py runserver
</pre>

Then Navigate to:
http://127.0.0.1:8000/

Features

	•	User authentication (Register/Login)
	•	Create inventory item requests
	•	Role-based access control (Admin/User)
	•	Admin approval/rejection for requests
	•	Edit/delete inventory and requests
	•	View available inventory
	•	Dashboard overview with status counts

 User Roles

1. Regular Users can:

	•	Register an account
	•	Create inventory requests
	•	View and edit their own requests
	•	View available inventory

2. Admin Users can:
   
	•	View all user requests
	•	Approve or reject item requests
	•	Edit or delete inventory and requests
	•	Add or update available inventory

