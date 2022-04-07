CREATE OR REPLACE FUNCTION Log_listing()
	RETURNS TRIGGER
	LANGUAGE PLPGSQL
	AS
$$
BEGIN
	INSERT INTO GPU_Listing_Archive VALUES (NEW.Listingid, NEW.GPU_model, NEW.GPU_brand, NEW.Customerid, NEW.Price);
	RETURN NEW;
END;
$$;

CREATE TRIGGER Update_listing 
AFTER INSERT 
ON GPU_Listing
FOR EACH ROW
EXECUTE PROCEDURE Log_listing();

CREATE OR REPLACE FUNCTION Date_now()
	RETURNS TRIGGER
	LANGUAGE PLPGSQL
	AS
$$
BEGIN
	IF (SELECT COUNT(*) FROM GPU_Listing WHERE Available_end_day < CURRENT_DATE) <> 0 THEN
	DELETE FROM GPU_Listing
	WHERE Available_start_day < CURRENT_DATE;
	END IF;
	IF (SELECT COUNT(*) FROM GPU_Listing WHERE Available_start_day < CURRENT_DATE) <> 0 THEN
	UPDATE GPU_Listing SET Available_start_day = CURRENT_DATE
	WHERE Available_start_day < CURRENT_DATE;
	END IF;
	RETURN NEW;
END;
$$;

CREATE TRIGGER Update_timing 
AFTER UPDATE OR DELETE
ON User1
FOR EACH STATEMENT
EXECUTE PROCEDURE Date_now();


CREATE OR REPLACE FUNCTION Rentals()
	RETURNS TRIGGER
	LANGUAGE PLPGSQL
	AS
$$
BEGIN
	IF ((NEW.Start_day = (SELECT Available_start_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (NEW.End_day = (SELECT Available_end_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (CURRENT_DATE >= (SELECT Available_start_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (CURRENT_DATE >= (SELECT Available_end_day FROM GPU_Listing WHERE Listingid = NEW.Listingid))) THEN
	END IF;
	IF ((NEW.Start_day = (SELECT Available_start_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (NEW.End_day < (SELECT Available_end_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (CURRENT_DATE >= (SELECT Available_start_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (CURRENT_DATE >= (SELECT Available_end_day FROM GPU_Listing WHERE Listingid = NEW.Listingid))) THEN
	INSERT INTO GPU_Listing VALUES ((SELECT g1.Listingid + 1 FROM GPU_Listing_Archive g1 WHERE g1.listingid >= all (SELECT g2.listingid FROM GPU_Listing_Archive g2)), 
									NEW.GPU_model,
								    NEW.GPU_brand,
								    (SELECT Customerid FROM GPU_Listing WHERE Listingid = NEW.Listingid),
								    NEW.End_Day + 1,
								    (SELECT Available_end_day FROM GPU_Listing WHERE Listingid = NEW.Listingid),
								   	(SELECT Price FROM GPU_Listing WHERE Listingid = NEW.Listingid));
	END IF;
	IF ((NEW.Start_day > (SELECT Available_start_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (NEW.End_day = (SELECT Available_end_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (CURRENT_DATE >= (SELECT Available_start_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (CURRENT_DATE >= (SELECT Available_end_day FROM GPU_Listing WHERE Listingid = NEW.Listingid))) THEN
	INSERT INTO GPU_Listing VALUES ((SELECT g1.Listingid + 1 FROM GPU_Listing_Archive g1 WHERE g1.listingid >= all (SELECT g2.listingid FROM GPU_Listing_Archive g2)), 
									NEW.GPU_model,
								    NEW.GPU_brand,
								    (SELECT Customerid FROM GPU_Listing WHERE Listingid = NEW.Listingid),
									(SELECT Available_start_day FROM GPU_Listing WHERE Listingid = NEW.Listingid),
								    NEW.Start_day - 1,
								   	(SELECT Price FROM GPU_Listing WHERE Listingid = NEW.Listingid));					
	END IF;
	IF ((NEW.Start_day > (SELECT Available_start_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (NEW.End_day < (SELECT Available_end_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (CURRENT_DATE >= (SELECT Available_start_day FROM GPU_Listing WHERE Listingid = NEW.Listingid)) AND (CURRENT_DATE >= (SELECT Available_end_day FROM GPU_Listing WHERE Listingid = NEW.Listingid))) THEN
	INSERT INTO GPU_Listing VALUES ((SELECT g1.Listingid + 1 FROM GPU_Listing_Archive g1 WHERE g1.listingid >= all (SELECT g2.listingid FROM GPU_Listing_Archive g2)),  
									NEW.GPU_model,
								    NEW.GPU_brand,
								    (SELECT Customerid FROM GPU_Listing WHERE Listingid = NEW.Listingid),
									(SELECT Available_start_day FROM GPU_Listing WHERE Listingid = NEW.Listingid),
								    NEW.Start_day - 1,
								   	(SELECT Price FROM GPU_Listing WHERE Listingid = NEW.Listingid));
	INSERT INTO GPU_Listing VALUES ((SELECT g1.Listingid + 1 FROM GPU_Listing_Archive g1 WHERE g1.listingid >= all (SELECT g2.listingid FROM GPU_Listing_Archive g2)),  
									NEW.GPU_model,
								    NEW.GPU_brand,
								    (SELECT Customerid FROM GPU_Listing WHERE Listingid = NEW.Listingid),
								    NEW.End_Day + 1,
								    (SELECT Available_end_day FROM GPU_Listing WHERE Listingid = NEW.Listingid),
									(SELECT Price FROM GPU_Listing WHERE Listingid = NEW.Listingid));
	END IF;
	DELETE FROM GPU_Listing WHERE Listingid = NEW.Listingid;
	RETURN NEW;	
END;
$$;

CREATE TRIGGER After_rental_listing
AFTER INSERT
ON Rental
FOR EACH ROW
EXECUTE PROCEDURE Rentals();