#
# Database handler for the HCP Interaction Logger.
#
import os
import mysql.connector
import json
from datetime import date
from typing import List, Dict, Any, Optional

# --- Database Configuration ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Abhishek@1259")
DB_NAME = os.getenv("DB_NAME", "hcpinteractio")

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise

# NEW: Add this function to fetch a record by its primary key.
def get_interaction_by_id(interaction_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a single interaction record by its unique ID."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM hcp_interactions WHERE id = %s"
        cursor.execute(query, (interaction_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error fetching interaction by ID from DB: {err}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_tables():
    """Creates the necessary tables if they do not exist."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hcp_interactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hcp_name VARCHAR(255),
                interaction_type VARCHAR(50),
                interaction_date DATE,
                summary TEXT,
                discussion_topics JSON,
                sentiment VARCHAR(20),
                outcomes TEXT,
                follow_up TEXT,
                logging_method VARCHAR(10) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# MODIFIED: This function now returns the newly created record.
def insert_interaction_to_db(data: Dict[str, Any], logging_method: str) -> Optional[Dict[str, Any]]:
    """Inserts a new interaction record and returns the newly created record."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hcp_name = data.get('hcpName')
        interaction_type = data.get('interactionType')
        interaction_date = data.get('interactionDate')
        summary = data.get('summary')
        discussion_topics = data.get('discussionTopics')
        if discussion_topics is not None:
            discussion_topics = json.dumps(discussion_topics)
        sentiment = data.get('sentiment')
        outcomes = data.get('outcomes')
        follow_up = data.get('followUp')
        
        query = """
            INSERT INTO hcp_interactions (
                hcp_name, interaction_type, interaction_date, summary, 
                discussion_topics, sentiment, outcomes, follow_up, logging_method
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (hcp_name, interaction_type, interaction_date, summary, discussion_topics, sentiment, outcomes, follow_up, logging_method)
        cursor.execute(query, values)
        new_id = cursor.lastrowid # Get the ID of the new row
        conn.commit()

        if new_id:
            return get_interaction_by_id(new_id) # Return the full new record
        return None
        
    except mysql.connector.Error as err:
        print(f"Error inserting data into DB: {err}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
def update_interaction_in_db(interaction_id: int, data: Dict[str, Any]) -> bool:
    """Updates an existing interaction record."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        updates = []
        values = []
        db_field_map = {
            'hcpName': 'hcp_name', 'interactionType': 'interaction_type', 'interactionDate': 'interaction_date',
            'summary': 'summary', 'discussionTopics': 'discussion_topics', 'sentiment': 'sentiment',
            'outcomes': 'outcomes', 'followUp': 'follow_up',
        }
        for key, value in data.items():
            db_key = db_field_map.get(key)
            if db_key:
                if db_key == 'discussion_topics' and value is not None:
                    value = json.dumps(value)
                if value is not None:
                    updates.append(f"{db_key} = %s")
                    values.append(value)
        if not updates:
            return False
        query = f"UPDATE hcp_interactions SET {', '.join(updates)} WHERE id = %s"
        values.append(interaction_id)
        cursor.execute(query, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            return False
        return True
    except mysql.connector.Error as err:
        print(f"Error updating data in DB: {err}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_interactions() -> List[Dict[str, Any]]:
    """Fetches all interaction records from the database."""
    conn = None
    interactions = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM hcp_interactions ORDER BY created_at DESC"
        cursor.execute(query)
        interactions = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching data from DB: {err}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    return interactions
    
def find_interactions_by_criteria(hcp_name: str, interaction_date: str) -> List[Dict[str, Any]]:
    """Fetches all interaction records matching an HCP name and date."""
    conn = None
    interactions = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, hcp_name, interaction_date, summary FROM hcp_interactions
            WHERE hcp_name = %s AND interaction_date = %s
            ORDER BY created_at DESC
        """
        cursor.execute(query, (hcp_name, interaction_date))
        interactions = cursor.fetchall() 
    except mysql.connector.Error as err:
        print(f"Error fetching interaction from DB: {err}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    return interactions

def get_interaction_by_hcp_and_date(hcp_name: str, interaction_date: str) -> Optional[Dict[str, Any]]:
    """Fetches a single full interaction record by HCP name and date."""
    conn = None
    interaction = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM hcp_interactions
            WHERE hcp_name = %s AND interaction_date = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        cursor.execute(query, (hcp_name, interaction_date))
        interaction = cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error fetching interaction from DB: {err}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    return interaction


if __name__ == '__main__':
    create_tables()