# NEXT SESSION PROMPT - Session 56

## 📋 CONTEXT FOR NEW SESSION

**Project:** Island Glass Leads - Glass shop management app
**Current Status:** Quick Wins Phase - 1 of 4 features complete (25%)
**Last Session:** Session 55 - Vendor Management ✅ COMPLETE
**Next Feature:** Job Detail Sub-Items (4-6 hours estimated)

---

## ✅ WHAT WAS JUST COMPLETED (Session 55)

### Vendor Management - FULLY FUNCTIONAL
- ✅ Database: vendor_contacts table created and migrated
- ✅ Backend: Full CRUD APIs for vendors with multiple contacts
- ✅ Frontend: NewVendorModal with dynamic contact management
- ✅ Features: Company name, type, email, phone, address, notes
- ✅ Contacts: Multiple contacts per vendor with job titles and primary designation
- ✅ UI: Mobile-responsive, matches design system

**Files Modified:**
- `database/migrations/add_vendor_contacts.sql` (NEW)
- `backend/models/vendor.py` (added contact models)
- `backend/database.py` (added 5 contact methods)
- `backend/routers/vendors.py` (updated create, added 3 contact endpoints)
- `frontend/src/components/NewVendorModal.tsx` (NEW)
- `frontend/src/pages/Vendors.tsx` (integrated modal)
- `frontend/src/types/index.ts` (updated vendor types)

---

## 🎯 NEXT SESSION GOAL: Job Detail Sub-Items

### Primary Objective
Implement display and CRUD for all job-related sub-items in the Job Detail page.

### Sub-Items to Implement (5 sections):

#### 1. Work Items (job_work_items)
- **Purpose:** Tasks/line items for the job
- **Backend:** Verify API endpoints exist
- **Frontend:** Create WorkItemsSection component
- **Fields:** description, quantity, unit_price, total, status
- **UI:** Table or card list with Add/Edit/Delete

#### 2. Vendor Materials (job_vendor_materials)
- **Purpose:** Materials ordered from vendors for this job
- **Backend:** Verify API endpoints exist
- **Frontend:** Create VendorMaterialsSection component
- **Fields:** vendor_id, material_description, quantity, cost, status, delivery_date
- **UI:** Table with vendor lookup, Add/Edit/Delete

#### 3. Site Visits (job_site_visits)
- **Purpose:** Log of site visits with notes
- **Backend:** Verify API endpoints exist
- **Frontend:** Create SiteVisitsSection component
- **Fields:** visit_date, technician, duration, notes, photos
- **UI:** Timeline or card list, Add/Edit/Delete

#### 4. Comments (job_comments)
- **Purpose:** Notes and discussions about the job
- **Backend:** Verify API endpoints exist
- **Frontend:** Create CommentsSection component
- **Fields:** comment_text, created_by, created_at
- **UI:** Comment thread style, Add/Delete

#### 5. Files (job_files)
- **Purpose:** Attachments and documents
- **Backend:** Verify file upload API exists
- **Frontend:** Create FilesSection component
- **Fields:** file_name, file_url, file_type, uploaded_by, uploaded_at
- **UI:** Grid of file cards, Upload/Download/Delete

---

## 🔍 PRE-WORK NEEDED

### Step 1: Backend API Audit (15-20 min)
Check if these endpoints exist in `backend/routers/jobs.py`:

**Work Items:**
- [ ] GET /api/v1/jobs/{job_id}/work-items
- [ ] POST /api/v1/jobs/{job_id}/work-items
- [ ] PUT /api/v1/jobs/work-items/{item_id}
- [ ] DELETE /api/v1/jobs/work-items/{item_id}

**Vendor Materials:**
- [ ] GET /api/v1/jobs/{job_id}/materials
- [ ] POST /api/v1/jobs/{job_id}/materials
- [ ] PUT /api/v1/jobs/materials/{material_id}
- [ ] DELETE /api/v1/jobs/materials/{material_id}

**Site Visits:**
- [ ] GET /api/v1/jobs/{job_id}/visits
- [ ] POST /api/v1/jobs/{job_id}/visits
- [ ] PUT /api/v1/jobs/visits/{visit_id}
- [ ] DELETE /api/v1/jobs/visits/{visit_id}

**Comments:**
- [ ] GET /api/v1/jobs/{job_id}/comments
- [ ] POST /api/v1/jobs/{job_id}/comments
- [ ] DELETE /api/v1/jobs/comments/{comment_id}

**Files:**
- [ ] GET /api/v1/jobs/{job_id}/files
- [ ] POST /api/v1/jobs/{job_id}/files (with upload)
- [ ] DELETE /api/v1/jobs/files/{file_id}

**If Missing:** Create backend endpoints first (follow vendor_contacts pattern)

### Step 2: Database Schema Check (10 min)
Verify these tables exist in Supabase:
- [ ] job_work_items
- [ ] job_vendor_materials
- [ ] job_site_visits
- [ ] job_comments
- [ ] job_files

**If Missing:** Create migration SQL files and run in Supabase

### Step 3: TypeScript Types (10 min)
Check `frontend/src/types/index.ts` for:
- [ ] WorkItem interface
- [ ] VendorMaterial interface
- [ ] SiteVisit interface
- [ ] JobComment interface
- [ ] JobFile interface

**If Missing:** Add types based on database schema

---

## 💡 IMPLEMENTATION STRATEGY

### Approach: One Section at a Time
1. Start with **Work Items** (simplest, no file uploads)
2. Then **Comments** (simple CRUD)
3. Then **Site Visits** (date handling)
4. Then **Vendor Materials** (vendor lookup)
5. Finally **Files** (most complex - file uploads)

### Component Architecture

#### Option A: Tabs (Recommended)
```tsx
<JobDetail>
  <Tabs>
    <Tab label="Overview">Job details here</Tab>
    <Tab label="Work Items">WorkItemsSection</Tab>
    <Tab label="Materials">VendorMaterialsSection</Tab>
    <Tab label="Site Visits">SiteVisitsSection</Tab>
    <Tab label="Comments">CommentsSection</Tab>
    <Tab label="Files">FilesSection</Tab>
  </Tabs>
</JobDetail>
```

#### Option B: Accordion Sections
```tsx
<JobDetail>
  <OverviewSection />
  <AccordionSection title="Work Items">
    <WorkItemsSection />
  </AccordionSection>
  <AccordionSection title="Materials">
    <VendorMaterialsSection />
  </AccordionSection>
  {/* ... */}
</JobDetail>
```

**Recommendation:** Use Tabs for better organization and mobile navigation

---

## 🎨 UI/UX GUIDELINES

### Design Consistency
- Follow existing app patterns (purple theme, rounded corners)
- Use mobile-first responsive design
- Maintain 16px+ font sizes on inputs (iOS zoom prevention)
- Include active states for touch targets (44x44px minimum)

### Each Section Should Have:
1. **Header:** Section title + "Add [Item]" button
2. **Empty State:** Friendly message when no items
3. **List/Table:** Display existing items
4. **Actions:** Edit/Delete buttons on each item
5. **Modal:** Add/Edit form with validation

### Mobile vs Desktop
- **Mobile:** Card-based lists, stack vertically
- **Desktop:** Tables with proper columns, side-by-side where appropriate

---

## 📂 FILES TO CREATE

### Frontend Components (in `frontend/src/components/`)
1. `JobTabs.tsx` - Tab container for job detail sections
2. `WorkItemsSection.tsx` - Work items CRUD
3. `VendorMaterialsSection.tsx` - Materials CRUD
4. `SiteVisitsSection.tsx` - Site visits CRUD
5. `CommentsSection.tsx` - Comments thread
6. `FilesSection.tsx` - File upload/download
7. `AddWorkItemModal.tsx` - Add/Edit work item
8. `AddMaterialModal.tsx` - Add/Edit material
9. `AddSiteVisitModal.tsx` - Add/Edit site visit
10. `FileUploadModal.tsx` - Upload files

### Frontend Services (in `frontend/src/services/api.ts`)
Add service methods:
```typescript
export const workItemsService = {
  getAll: async (jobId: number) => {...},
  create: async (jobId: number, data: any) => {...},
  update: async (itemId: number, data: any) => {...},
  delete: async (itemId: number) => {...},
};

// Repeat for: materialsService, siteVisitsService, commentsService, filesService
```

---

## 🧪 TESTING CHECKLIST

After implementation, verify:
- [ ] Can view all sub-items for a job
- [ ] Can add new items in each section
- [ ] Can edit existing items
- [ ] Can delete items
- [ ] Empty states display correctly
- [ ] Mobile responsive layout works
- [ ] Loading states show during API calls
- [ ] Error messages display on failures
- [ ] Form validation works (required fields)
- [ ] Files upload and download correctly

---

## ⚠️ KNOWN CONSIDERATIONS

### 1. File Uploads
- Will need backend file storage (Supabase Storage or S3)
- Consider file size limits
- Handle file type validation
- Show upload progress

### 2. Vendor Lookup
- VendorMaterialsSection needs vendor dropdown
- Use existing vendorsService.getAll()
- Cache vendor list to avoid repeated calls

### 3. Date Handling
- Site visits need date picker
- Use consistent date format (ISO 8601)
- Consider timezone handling

### 4. User Display
- Comments show created_by (user_id)
- May need to fetch user names for display
- Consider caching user info

---

## 📊 SUCCESS CRITERIA

### When This Feature is Complete:
✅ All 5 sub-item sections visible in Job Detail
✅ Each section has functional CRUD operations
✅ UI matches app design system
✅ Mobile-responsive implementation
✅ Loading and error states handled
✅ Empty states are user-friendly
✅ File uploads work (if files section included)

### Quick Wins Progress After This:
- ✅ Vendor Management (Session 55)
- ✅ Job Detail Sub-Items (Session 56)
- ⏳ Dashboard Charts (Session 57)
- ⏳ Admin Settings Tabs (Session 58)

**Progress: 50% complete (2 of 4)**

---

## 🚀 RECOMMENDED SESSION FLOW

### Phase 1: Assessment (20 min)
1. Read checkpoint.md Session 55 summary
2. Review existing JobDetail page code
3. Audit backend APIs for sub-items
4. Check database schema in Supabase
5. Verify TypeScript types exist

### Phase 2: Backend (1-2 hours, if needed)
1. Create missing database tables (migrations)
2. Add Pydantic models for sub-items
3. Create database CRUD methods
4. Add API endpoints to jobs router
5. Test endpoints in FastAPI docs

### Phase 3: Frontend - First Section (1 hour)
1. Create WorkItemsSection component
2. Add AddWorkItemModal
3. Implement CRUD operations
4. Test mobile and desktop layouts

### Phase 4: Remaining Sections (2-3 hours)
1. Repeat pattern for other 4 sections
2. Comments → Site Visits → Materials → Files
3. Test each section thoroughly

### Phase 5: Integration & Polish (30-45 min)
1. Add tabs/accordion to JobDetail page
2. Verify navigation works
3. Test all sections together
4. Handle edge cases

---

## 🔗 HELPFUL COMMANDS

### Start dev servers:
```bash
# Backend (terminal 1)
cd backend && python3 -m uvicorn main:app --reload --port 8000

# Frontend (terminal 2)
cd frontend && npm run dev
```

### Check API endpoints:
Open: http://localhost:8000/docs

### Check running app:
Open: http://localhost:3001

---

## 📝 PROMPT FOR CLAUDE

**Use this prompt to start Session 56:**

```
I'm continuing work on the Island Glass Leads app. Last session (55) we completed Vendor Management with multiple contacts - fully functional with database, backend APIs, and frontend UI.

This session, I need to implement Job Detail Sub-Items - displaying and managing all related items for a job (work items, vendor materials, site visits, comments, and files).

Please:
1. Review the current state by reading checkpoint.md (Session 55 summary at the end)
2. Audit backend to see which APIs exist for job sub-items
3. Check if database tables exist for: job_work_items, job_vendor_materials, job_site_visits, job_comments, job_files
4. Verify TypeScript types exist for these entities
5. Create any missing backend infrastructure (following vendor_contacts pattern)
6. Build frontend components for each section (tabbed or accordion interface)
7. Implement CRUD operations for all sub-items
8. Ensure mobile-responsive design matching app style

See NEXT_SESSION.md for detailed requirements and implementation strategy.

Let's continue with #slowandintentional approach - no rushing, get it right.
```

---

## 🎯 KEY REMINDERS

1. **Follow Patterns:** Use vendor_contacts implementation as template
2. **Mobile-First:** 16px+ inputs, 44x44px touch targets, active states
3. **Design System:** Purple theme, rounded corners, consistent spacing
4. **Type Safety:** Full TypeScript types, Pydantic models
5. **Error Handling:** Loading states, error messages, empty states
6. **Testing:** Test each section before moving to next
7. **Documentation:** Update checkpoint.md when done

---

**Last Updated:** November 17, 2025 - End of Session 55
**Prepared For:** Session 56 - Job Detail Sub-Items
**Estimated Duration:** 4-6 hours
**#slowandintentional** - Quality over speed, get it right! 🎯
