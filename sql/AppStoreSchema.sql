/*******************

  Create the schema

********************/

CREATE TABLE IF NOT EXISTS User(
 First_name VARCHAR(64) NOT NULL,
 Last_name VARCHAR(64) NOT NULL,
 Email VARCHAR(64) UNIQUE NOT NULL,
 Dob DATE NOT NULL,
 Since DATE NOT NULL,
 Customerid VARCHAR(16) PRIMARY KEY,
 Wallet_balance NUMERIC NOT NULL CHECK (wallet_balance >= 0),
 Phone_number CHAR(8) CHECK (phone_number NOT LIKE '%[^0-9]%')
 Pass_word VARCHAR(64) CHECK (len(password) >= 8));
	
 CREATE TABLE IF NOT EXISTS GPU(
 GPU_model VARCHAR(32) NOT NULL,
 GPU_brand VARCHAR(32) NOT NULL,
 PRIMARY KEY (GPU_model, GPU_brand),
 Memory_type VARCHAR(8) NOT NULL,
 Memory_size VARCHAR(8) NOT NULL,
 Memory_interface VARCHAR(8) NOT NULL,
 Memory_bandwidth VARCHAR(8) NOT NULL,
 Base_clock VARCHAR(8) NOT NULL,
 Boost_clock VARCHAR(8) NOT NULL,
 Cores_Processors VARCHAR(8) NOT NULL,
 );
  
 CREATE TABLE GPU_Listing(
 Customerid VARCHAR(16) REFERENCES User(Customerid) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
 GPU_model VARCHAR(32) NOT NULL,
 GPU_brand VARCHAR(32) NOT NULL,
 FOREIGN KEY (GPU_model, GPU_brand) REFERENCES GPU(GPU_model, GPU_brand) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED),
 Available_start_day DATE NOT NULL
 Available_end_day DATE NOT NULL
 Price NUMERIC NOT NULL CHECK (Price >= 0);

 CREATE TABLE Rental(
 Borrower_id VARCHAR(16) REFERENCES User(Customerid) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
 Owner_id VARCHAR(16),
 GPU_model VARCHAR(32) NOT NULL,
 GPU_brand VARCHAR(32) NOT NULL,
 FOREIGN KEY (Owner_id, GPU_model, GPU_brand) REFERENCES GPU(Owner_id, GPU_model, GPU_brand) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED),
 Start_day DATE NOT NULL
 End_day DATE NOT NULL;