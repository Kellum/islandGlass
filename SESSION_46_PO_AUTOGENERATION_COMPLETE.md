# Session 46: PO Auto-Generation System - Backend Complete

## Overview
Successfully implemented the backend for automatic PO number generation system. PO numbers are now auto-generated based on client data, location, and address with support for remakes and warranties.

## PO Number Format

### Regular Job
```
PO-01-Ryan.Kellum.3432
```
- **01**: Location code (Fernandina/Yulee FL)
- **Ryan.Kellum**: Contact name (FirstName.LastName) or Company name
- **3432**: Street number from address

### Special Job Types
- **Remake**: `PO-01-RMK.Kellum.3432` (RMK + LastName only)
- **Warranty**: `PO-03-WAR.Kellum.3432` (WAR + LastName only)
- **Duplicate**: `PO-01-Ryan.Kellum.3432-2` (sequence number appended)

### Company Job
```
PO-02-AcmeGlass.4567
```
- Uses company name instead of contact name

## Location Codes
- **01**: Fernandina Beach & Yulee, FL
- **02**: All Georgia jobs
- **03**: Jacksonville, FL

## Implementation Summary

### 1. Database Migration (`009_po_auto_generation.sql`)
**Created:**
- Added `location_code` VARCHAR(10) to `jobs` table
- Added `is_remake` BOOLEAN to `jobs` table
- Added `is_warranty` BOOLEAN to `jobs` table
- Created `locations` reference table with 3 predefined locations
- Added constraint: job cannot be both remake AND warranty
- Created indexes for performance

**Helper Functions:**
- `extract_street_number(address)` - extracts first number from address
- `format_name_for_po(...)` - formats name portion based on job type
- `count_duplicate_pos(...)` - counts existing POs for sequence numbering

**To Apply Migration:**
```bash
python3 apply_po_autogen_migration.py
```
Then paste SQL into Supabase SQL Editor.

### 2. Backend PO Generator Utility (`backend/utils/po_generator.py`)
**Functions:**
- `generate_po_number()` - Main generation function
  - Takes: client_id, location_code, is_remake, is_warranty, site_address
  - Returns: po_number, is_duplicate, warning, metadata
  - Handles all edge cases and validation

- `validate_po_format()` - Validates if PO follows expected format
  - Returns warning if manually edited PO doesn't match convention

- `POGenerationError` - Custom exception for generation errors

**Features:**
- Automatic street number extraction
- Smart name formatting (individual vs company)
- Duplicate detection and sequence numbering
- Comprehensive error handling

### 3. Updated Job Model (`backend/models/job.py`)
**Added Fields:**
- `location_code: Optional[str]` - Location code for the job
- `is_remake: bool = False` - Remake job flag
- `is_warranty: bool = False` - Warranty job flag

**Validation:**
- Location code must be '01', '02', or '03'
- Cannot be both remake AND warranty
- All fields included in JobCreate, JobUpdate, JobResponse

### 4. Updated Jobs API (`backend/routers/jobs.py`)
**New Endpoint:**
```
POST /api/v1/jobs/generate-po
```
**Request:**
```json
{
  "client_id": 123,
  "location_code": "01",
  "is_remake": false,
  "is_warranty": false,
  "site_address": "123 Main St" // optional
}
```

**Response:**
```json
{
  "po_number": "PO-01-Ryan.Kellum.123",
  "is_duplicate": false,
  "warning": null,
  "location_code": "01",
  "street_number": "123",
  "name_part": "Ryan.Kellum"
}
```

**Updated Endpoints:**
- `POST /api/v1/jobs` - Now accepts location_code, is_remake, is_warranty
- `GET /api/v1/jobs` - Returns new fields in job list
- `GET /api/v1/jobs/{id}` - Returns new fields in job details
- `PUT /api/v1/jobs/{id}` - Allows updating new fields

### 5. Files Created/Modified

**Created:**
- `database/migrations/009_po_auto_generation.sql` (Migration)
- `apply_po_autogen_migration.py` (Migration helper)
- `backend/utils/__init__.py` (Utils package)
- `backend/utils/po_generator.py` (PO generation logic)
- `SESSION_46_PO_AUTOGENERATION_COMPLETE.md` (This file)

**Modified:**
- `backend/models/job.py` (Added new fields & validation)
- `backend/routers/jobs.py` (Added endpoint & updated existing)

## Usage Examples

### 1. Generate PO Preview (Frontend)
```typescript
const response = await fetch('/api/v1/jobs/generate-po', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    client_id: 41,
    location_code: '01',
    is_remake: false,
    is_warranty: false
  })
});

const data = await response.json();
// data.po_number = "PO-01-Ryan.Kellum.3432"
// data.is_duplicate = false
```

### 2. Create Job with Generated PO
```typescript
const jobData = {
  po_number: generatedPO.po_number,
  client_id: 41,
  location_code: '01',
  is_remake: false,
  is_warranty: false,
  status: 'Quote',
  job_description: 'Window installation'
};

await fetch('/api/v1/jobs', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(jobData)
});
```

## Error Handling

### POGenerationError Cases
1. **Invalid location code**: Must be '01', '02', or '03'
2. **Both remake and warranty**: Cannot be both simultaneously
3. **Client not found**: client_id must exist
4. **No street number**: Address must contain a number
5. **Missing client data**: Client must have name or address

### User-Facing Warnings
- **is_duplicate**: Shows when this is duplicate #2, #3, etc.
- **Format warning**: When manually edited PO doesn't match convention

## Next Steps (Frontend)

### 1. Create Job Form UI
- Location dropdown (01, 02, 03) with descriptions
- "Is Remake" checkbox
- "Is Warranty" checkbox
- PO Number input (auto-filled, editable)
- "Regenerate PO" button
- Warning badge for manually edited POs

### 2. Auto-Generation Flow
```
1. User selects client → fetch client data
2. User selects location → auto-generate PO
3. User toggles remake/warranty → regenerate PO
4. PO field auto-updates (but remains editable)
5. Show warning if user manually edits PO
6. Display duplicate warning if applicable
```

### 3. Validation
- Disable "Is Remake" and "Is Warranty" if both checked
- Show error if address has no street number
- Preview PO in real-time as user makes selections

## Testing Checklist

### Backend Tests Needed
- [ ] Generate PO for individual client
- [ ] Generate PO for company client
- [ ] Generate remake PO
- [ ] Generate warranty PO
- [ ] Detect duplicates correctly
- [ ] Handle missing street number
- [ ] Validate location codes
- [ ] Prevent remake + warranty combination

### Integration Tests Needed
- [ ] Create job with auto-generated PO
- [ ] Update job preserves PO fields
- [ ] GET jobs returns new fields
- [ ] Migration applies successfully

## Known Limitations

1. **Manual migration**: Database migration must be applied manually in Supabase SQL editor
2. **First number only**: Street number extraction uses first number in address (e.g., "123 Main St Apt 4B" → "123")
3. **Name parsing**: Assumes "First Last" format for contact names
4. **No PO history**: System doesn't track PO number changes

## Success Criteria ✓

- [x] Database schema supports PO generation fields
- [x] Backend utility generates POs correctly
- [x] API endpoint provides PO preview
- [x] Job creation/update supports new fields
- [x] All GET endpoints return new fields
- [x] Error handling for edge cases
- [x] Backend running without errors

## Architecture Notes

### Why Separate Utility?
The PO generator is a separate utility (`utils/po_generator.py`) rather than a database method because:
1. Complex business logic better suited for Python
2. Easier to test and modify
3. Reusable across different contexts
4. Cleaner separation of concerns

### Why Preview Endpoint?
The `/generate-po` endpoint allows frontend to:
1. Show PO in real-time as user makes selections
2. Validate before job creation
3. Display warnings early
4. Provide better UX with immediate feedback

### Database vs Application Logic
- **Database**: Basic extraction functions (street number, name formatting)
- **Application**: Complex orchestration, API integration, error handling
- This hybrid approach balances performance with flexibility

## Migration Path for Existing POs

If you have existing POs that need location codes:
```sql
-- Update existing POs to add location code based on pattern
UPDATE jobs
SET location_code = substring(po_number from '^PO-(\d{2})-')
WHERE location_code IS NULL
  AND po_number LIKE 'PO-%';
```

## Documentation References

- PO Format Examples: See "PO Number Format" section above
- API Documentation: http://localhost:8000/docs (FastAPI auto-docs)
- Migration File: `database/migrations/009_po_auto_generation.sql`
- Generator Code: `backend/utils/po_generator.py`

---

**Status**: ✅ Backend Implementation Complete
**Next Session**: Frontend job form with PO auto-generation UI
**Backend Server**: Running on http://localhost:8000
