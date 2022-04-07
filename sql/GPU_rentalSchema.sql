/*******************

  Create the schema

********************/

CREATE TABLE IF NOT EXISTS User1(
 First_name VARCHAR(64) NOT NULL,
 Last_name VARCHAR(64) NOT NULL,
 Email VARCHAR(64) UNIQUE NOT NULL,
 Customerid VARCHAR(16) PRIMARY KEY,
 Wallet_balance NUMERIC NOT NULL CHECK (wallet_balance >= 0),
 Phone_number NUMERIC NOT NULL CHECK (Phone_number <= 9999999999 and Phone_number > 999999999),
 Pass_word VARCHAR(64) NOT NULL,
 Credit_card_number NUMERIC NOT NULL CHECK (
	 (Credit_card_type = 'mastercard' and Credit_card_number <= 5999999999999999 and Credit_card_number > 4999999999999999) or
	(Credit_card_type = 'visa' and ((Credit_card_number <= 4999999999999999 and Credit_card_number > 3999999999999999) or (Credit_card_number <= 4999999999999 and Credit_card_number > 3999999999999))) or
	(Credit_card_type = 'americanexpress' and ((Credit_card_number <= 349999999999999 and Credit_card_number > 339999999999999) or (Credit_card_number <= 379999999999999 and Credit_card_number > 369999999999999)))),
 Credit_card_type VARCHAR(64) NOT NULL CHECK (Credit_card_type = 'mastercard' or Credit_card_type = 'visa' or Credit_card_type = 'americanexpress'));
	
 CREATE TABLE IF NOT EXISTS GPU(
 GPU_model VARCHAR(32),
 GPU_brand VARCHAR(32),
 PRIMARY KEY (GPU_model, GPU_brand),
 Memory_size VARCHAR(16) NOT NULL,
 Memory_type VARCHAR(16) NOT NULL,
 Memory_interface VARCHAR(16) NOT NULL,
 Base_clock VARCHAR(16) NOT NULL,
 Memory_clock VARCHAR(16) NOT NULL,
 Shaders NUMERIC NOT NULL,
 TMU NUMERIC NOT NULL,
 ROP NUMERIC NOT NULL
 );
  
 CREATE TABLE IF NOT EXISTS GPU_Listing(
 Listingid NUMERIC CHECK (Listingid >= 0) PRIMARY KEY,
 GPU_model VARCHAR(32),
 GPU_brand VARCHAR(32),
 FOREIGN KEY (GPU_model, GPU_brand) REFERENCES GPU(GPU_model, GPU_brand) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
 Customerid VARCHAR(16) REFERENCES User1(Customerid) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
 Available_start_day DATE NOT NULL CHECK (Available_start_day <= Available_end_day AND Available_start_day >= CURRENT_DATE),
 Available_end_day DATE NOT NULL CHECK(Available_end_day >= Available_start_day),
 Price NUMERIC NOT NULL CHECK (Price >= 0));

CREATE TABLE IF NOT EXISTS GPU_Listing_Archive(
 Listingid NUMERIC CHECK (Listingid >= 0) PRIMARY KEY,
 GPU_model VARCHAR(32),
 GPU_brand VARCHAR(32),
 FOREIGN KEY (GPU_model, GPU_brand) REFERENCES GPU(GPU_model, GPU_brand) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
 Customerid VARCHAR(16) REFERENCES User1(Customerid) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
 Price NUMERIC NOT NULL CHECK (Price >= 0));

 CREATE TABLE IF NOT EXISTS Rental(
 Borrower_id VARCHAR(16) REFERENCES User1(Customerid) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
 GPU_model VARCHAR(32),
 GPU_brand VARCHAR(32),
 FOREIGN KEY (GPU_model, GPU_brand) REFERENCES GPU(GPU_model, GPU_brand) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
 Listingid NUMERIC CHECK (Listingid >= 0) REFERENCES GPU_Listing_Archive(Listingid) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
 Start_day DATE NOT NULL CHECK (Start_day <= End_day),
 End_day DATE NOT NULL CHECK (End_day >= Start_day));

