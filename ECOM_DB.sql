use ecom;
Create TABLE customer_new(
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(80) NOT NULL,
email VARCHAR (50) NOT NULL UNIQUE,
phone_num VARCHAR(13) NOT NULL
);

CREATE TABLE customer_accounts(
id INT AUTO_INCREMENT PRIMARY KEY,
user_name VARCHAR(50) NOT NULL UNIQUE,
password VARCHAR(15) NOT NULL,
cust_id INT NOT NULL,
FOREIGN KEY (cust_id) REFERENCES Customer(id)
);

Create TABLE product(
id INT AUTO_INCREMENT PRIMARY KEY,
product_name VARCHAR(80) NOT NULL,
price INT NOT NULL
);

CREATE TABLE orders_new (
id INT AUTO_INCREMENT PRIMARY KEY,
cust_id INT NOT NULL,
date DATETIME NOT NULL,
FOREIGN KEY (cust_id) REFERENCES Customer(id) 
);

create TABLE order_products(
id INT AUTO_INCREMENT PRIMARY KEY,
order_id INT NOT NULL,
product_id INT NOT NULL
); 
DROP TABLE order_products;
-- had to drop this table to create a new one for mini-project 






