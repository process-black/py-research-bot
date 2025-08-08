"""Generic Airtable client utility for any base/table operations."""

import os
from typing import Dict, Any, Optional
from pyairtable import Api
from src.utils import colored_logs as llog


class AirtableClient:
    """Generic client for interacting with any Airtable base and table."""
    
    def __init__(self, base_id: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize Airtable client.
        
        Args:
            base_id: Airtable base ID (uses env var if not provided)
            api_token: Airtable API token (uses env var if not provided)
        """
        self.api_token = api_token or os.environ.get("AIRTABLE_API_TOKEN")
        self.base_id = base_id
        
        if not self.api_token:
            raise ValueError("AIRTABLE_API_TOKEN environment variable is not set")
            
        self.api = Api(self.api_token)
        llog.gray(f"🗃️ Initialized Airtable client")
    
    def get_table(self, base_id: str, table_name: str):
        """Get a specific table from a base."""
        return self.api.table(base_id, table_name)
    
    def create_record(self, base_id: str, table_name: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record in any Airtable table.
        
        Args:
            base_id: Airtable base ID
            table_name: Name of the table
            fields: Dictionary of field names and values
            
        Returns:
            dict: Created Airtable record
        """
        try:
            table = self.get_table(base_id, table_name)
            
            llog.cyan(f"📝 Creating record in {table_name}")
            record = table.create(fields)
            
            llog.green(f"✅ Created record: {record['id']}")
            return record
            
        except Exception as e:
            error_msg = str(e)
            # Truncate very long error messages (likely containing base64 data)
            if len(error_msg) > 500:
                error_msg = error_msg[:500] + "... [truncated - likely contains binary data]"
            llog.red(f"❌ Failed to create record: {error_msg}")
            raise e
    
    def update_record(self, base_id: str, table_name: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing record in any Airtable table.
        
        Args:
            base_id: Airtable base ID
            table_name: Name of the table
            record_id: Airtable record ID
            fields: Fields to update
            
        Returns:
            dict: Updated Airtable record
        """
        try:
            table = self.get_table(base_id, table_name)
            
            llog.cyan(f"🔄 Updating record: {record_id}")
            record = table.update(record_id, fields)
            
            llog.green(f"✅ Updated record: {record_id}")
            return record
            
        except Exception as e:
            llog.red(f"❌ Failed to update record: {str(e)}")
            raise e
    
    def search_records(self, base_id: str, table_name: str, formula: Optional[str] = None) -> list:
        """
        Search for records in any Airtable table.
        
        Args:
            base_id: Airtable base ID
            table_name: Name of the table
            formula: Airtable formula for filtering (optional)
            
        Returns:
            list: Matching records
        """
        try:
            table = self.get_table(base_id, table_name)
            
            if formula:
                records = table.all(formula=formula)
            else:
                records = table.all()
                
            llog.cyan(f"🔍 Found {len(records)} records in {table_name}")
            return records
            
        except Exception as e:
            llog.red(f"❌ Failed to search records: {str(e)}")
            return []
    
    def delete_record(self, base_id: str, table_name: str, record_id: str) -> bool:
        """
        Delete a record from any Airtable table.
        
        Args:
            base_id: Airtable base ID
            table_name: Name of the table
            record_id: Airtable record ID
            
        Returns:
            bool: True if successful
        """
        try:
            table = self.get_table(base_id, table_name)
            
            table.delete(record_id)
            llog.green(f"✅ Deleted record: {record_id}")
            return True
            
        except Exception as e:
            llog.red(f"❌ Failed to delete record: {str(e)}")
            return False
    
    def upload_attachment_to_record(self, base_id: str, table_name: str, record_id: str, field_name: str, file_path: str) -> Dict[str, Any]:
        """
        Upload attachment directly to an existing Airtable record using pyairtable's upload method.
        
        Args:
            base_id: Airtable base ID
            table_name: Name of the table
            record_id: Airtable record ID
            field_name: Name of the attachment field
            file_path: Path to local file
            
        Returns:
            dict: Updated Airtable record
        """
        try:
            table = self.get_table(base_id, table_name)
            
            llog.cyan(f"📎 Uploading attachment to record {record_id}")
            record = table.upload_attachment(record_id, field_name, file_path)
            
            llog.green(f"✅ Attachment uploaded successfully")
            return record
            
        except Exception as e:
            error_msg = str(e)
            # Truncate very long error messages (likely containing binary data)
            if len(error_msg) > 500:
                error_msg = error_msg[:500] + "... [truncated - likely contains binary data]"
            llog.red(f"❌ Failed to upload attachment: {error_msg}")
            raise e