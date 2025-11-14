// User types
export interface User {
  user_id: string;
  email: string;
  full_name: string | null;
  role: string | null;
  company_id: string | null;
  is_active: boolean;
}

// Auth types
export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: User;
}

// Job types - matches backend JobResponse
export interface Job {
  job_id: number;
  po_number: string;
  client_id: number;
  client_name: string | null;  // Client name for display

  // PO Auto-Generation Fields
  location_code: string | null; // '01', '02', or '03'
  is_remake: boolean;
  is_warranty: boolean;

  // Dates
  job_date: string | null;
  estimated_completion_date: string | null;
  actual_completion_date: string | null;

  // Status - matches backend valid statuses
  status: 'Quote' | 'Scheduled' | 'In Progress' | 'Pending Materials' | 'Ready for Install' | 'Installed' | 'Completed' | 'Cancelled' | 'On Hold';

  // Financials
  total_estimate: number | null;
  actual_cost: number | null;
  material_cost: number | null;
  labor_cost: number | null;
  profit_margin: number | null;

  // Details
  job_description: string | null;
  internal_notes: string | null;
  customer_notes: string | null;

  // Site Information
  site_address: string | null;
  site_contact_name: string | null;
  site_contact_phone: string | null;

  // Metadata
  company_id: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
}

// Job Detail - matches backend JobDetailResponse (extends Job)
export interface JobDetail extends Job {
  work_item_count: number;
  material_count: number;
  visit_count: number;
}

// Client types
export interface Client {
  id: number;  // Backend returns 'id', not 'client_id'
  client_name: string | null;
  client_type: 'residential' | 'contractor' | 'commercial';
  address: string | null;
  city: string | null;
  state: string | null;
  zipcode: string | null;  // Backend uses 'zipcode', not 'zip_code'
  company_id: string | null;
  created_at: string | null;
  updated_at: string | null;
  created_by: string | null;
  updated_by: string | null;
  primary_contact_email: string | null;
  primary_contact_phone: string | null;
}

// Vendor types
export interface Vendor {
  vendor_id: number;
  vendor_name: string;
  contact_name: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  website: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}
